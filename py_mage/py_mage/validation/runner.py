from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from py_mage.cards.basic import make_creature_spell, make_lightning_bolt_spell
from py_mage.cards.registry import get_definition
from py_mage.core.card import Card
from py_mage.core.game_state import GameState
from py_mage.core.invariants import check_invariants
from py_mage.core.player import Player
from py_mage.validation.state import serialize_game_state


@dataclass
class ActionScript:
    seed: int
    players: List[Dict[str, Any]]
    initial_zones: Dict[str, Dict[str, List[str]]]
    actions: List[Dict[str, Any]]

    @classmethod
    def from_path(cls, path: Path) -> "ActionScript":
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            seed=data.get("seed", 0),
            players=data["players"],
            initial_zones=data.get("initial_zones", {}),
            actions=data.get("actions", []),
        )


@dataclass
class ActionRunner:
    script: ActionScript
    assert_invariants: bool = False
    log: List[str] = field(default_factory=list)

    def run(self) -> GameState:
        random.seed(self.script.seed)
        players = [Player(entry["name"]) for entry in self.script.players]
        game_state = GameState(players=players)
        self._apply_initial_zones(game_state)
        if self.assert_invariants:
            check_invariants(game_state)
        for action in self.script.actions:
            self._apply_action(game_state, action)
            if self.assert_invariants:
                check_invariants(game_state)
        return game_state

    def _apply_initial_zones(self, game_state: GameState) -> None:
        for player in game_state.players:
            zones = self.script.initial_zones.get(player.name, {})
            self._populate_zone(player.battlefield.cards, zones.get("battlefield", []), player)
            self._populate_zone(player.hand.cards, zones.get("hand", []), player)
            self._populate_zone(player.library.cards, zones.get("library", []), player)

    def _populate_zone(self, destination: List[Card], names: Iterable[str], owner: Player) -> None:
        for name in names:
            definition = get_definition(name)
            destination.append(Card(definition, owner=owner, controller=owner))

    def _apply_action(self, game_state: GameState, action: Dict[str, Any]) -> None:
        kind = action["action"]
        if kind == "advance_step":
            count = action.get("count", 1)
            for _ in range(count):
                step = game_state.advance_step().value
                self.log.append(f"step:{step}")
            return
        if kind == "activate_mana":
            player = self._get_player(game_state, action["player"])
            card = self._find_card(player.battlefield.cards, action["card"], action.get("index", 0))
            ability = card.definition.abilities[0](card, game_state)[0]
            ability.activate(game_state)
            self._resolve_stack(game_state)
            self.log.append(f"{player.name} activates {card.name}")
            return
        if kind == "cast_creature":
            player = self._get_player(game_state, action["player"])
            card = self._find_card(player.hand.cards, action["card"], action.get("index", 0))
            game_state.cast_spell(player, card, make_creature_spell(card))
            self._resolve_stack(game_state)
            self.log.append(f"{player.name} casts {card.name}")
            return
        if kind == "cast_bolt":
            player = self._get_player(game_state, action["player"])
            target_player = self._get_player(game_state, action["target_player"])
            target_card = self._find_card(
                target_player.battlefield.cards,
                action["target_card"],
                action.get("target_index", 0),
            )
            card = self._find_card(player.hand.cards, action["card"], action.get("index", 0))
            game_state.cast_spell(player, card, make_lightning_bolt_spell(card, target_card))
            self._resolve_stack(game_state)
            self.log.append(f"{player.name} casts {card.name} targeting {target_card.name}")
            return
        if kind == "declare_attackers":
            player = self._get_player(game_state, action["player"])
            defender = self._get_player(game_state, action["defender"])
            attackers = [
                self._find_card(player.battlefield.cards, name, idx)
                for idx, name in enumerate(action["attackers"])
            ]
            game_state.declare_attackers(attackers, defender)
            self.log.append(f"{player.name} attacks {defender.name} with {[c.name for c in attackers]}")
            return
        if kind == "declare_blockers":
            player = self._get_player(game_state, action["player"])
            assignments: List[tuple[Card, List[Card]]] = []
            for assignment in action["assignments"]:
                attacker = self._find_card(
                    self._get_player(game_state, assignment["attacker_player"]).battlefield.cards,
                    assignment["attacker"],
                    assignment.get("attacker_index", 0),
                )
                blockers = [
                    self._find_card(player.battlefield.cards, name, idx)
                    for idx, name in enumerate(assignment["blockers"])
                ]
                assignments.append((attacker, blockers))
            game_state.declare_blockers(assignments)
            self.log.append(f"{player.name} blocks")
            return
        if kind == "resolve_combat":
            game_state.resolve_combat()
            results = game_state.check_state_based_actions()
            self.log.extend(results)
            self.log.append("combat resolved")
            return
        if kind == "check_sba":
            results = game_state.check_state_based_actions()
            self.log.extend(results)
            self.log.append("sba checked")
            return
        raise ValueError(f"Unknown action: {kind}")

    def _resolve_stack(self, game_state: GameState) -> None:
        while not game_state.stack.is_empty():
            for _ in game_state.players:
                game_state.pass_priority()

    def _get_player(self, game_state: GameState, name: str) -> Player:
        for player in game_state.players:
            if player.name == name:
                return player
        raise ValueError(f"Unknown player: {name}")

    def _find_card(self, cards: List[Card], name: str, index: int) -> Card:
        matches = [card for card in cards if card.name == name]
        if len(matches) <= index:
            raise ValueError(f"Card {name} index {index} not found")
        return matches[index]


def run_script(path: Path, assert_invariants: bool) -> tuple[GameState, List[str]]:
    script = ActionScript.from_path(path)
    runner = ActionRunner(script=script, assert_invariants=assert_invariants)
    game_state = runner.run()
    return game_state, runner.log


def run_smoke(seed: int, assert_invariants: bool) -> tuple[GameState, List[str]]:
    script = ActionScript(
        seed=seed,
        players=[{"name": "A"}, {"name": "B"}],
        initial_zones={
            "A": {"battlefield": ["Forest", "Forest"], "hand": ["Grizzly Bears"]},
            "B": {"battlefield": ["Forest", "Forest"], "hand": ["Grizzly Bears"]},
        },
        actions=[
            {"action": "activate_mana", "player": "A", "card": "Forest", "index": 0},
            {"action": "activate_mana", "player": "A", "card": "Forest", "index": 1},
            {"action": "cast_creature", "player": "A", "card": "Grizzly Bears", "index": 0},
            {"action": "activate_mana", "player": "B", "card": "Forest", "index": 0},
            {"action": "activate_mana", "player": "B", "card": "Forest", "index": 1},
            {"action": "cast_creature", "player": "B", "card": "Grizzly Bears", "index": 0},
        ],
    )
    runner = ActionRunner(script=script, assert_invariants=assert_invariants)
    game_state = runner.run()
    return game_state, runner.log


def dump_state(game_state: GameState, out_path: Path) -> None:
    out_path.write_text(json.dumps(serialize_game_state(game_state), indent=2), encoding="utf-8")
