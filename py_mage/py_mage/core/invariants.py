from __future__ import annotations

from typing import Iterable, Set


def check_invariants(game_state: "GameState") -> None:
    seen: Set[int] = set()
    for player in game_state.players:
        for zone in (
            player.library,
            player.hand,
            player.battlefield,
            player.graveyard,
            player.exile,
        ):
            for card in zone.cards:
                card_id = id(card)
                if card_id in seen:
                    raise AssertionError(f"Card {card.name} appears in multiple zones")
                seen.add(card_id)
        for amount in player.mana_pool.amounts.values():
            if amount < 0:
                raise AssertionError("Mana pool contains negative amount")
        if not isinstance(player.life, int):
            raise AssertionError("Player life must be an integer")
    for item in game_state.stack.items:
        if item.source is None or item.controller is None:
            raise AssertionError("Stack item must have source and controller")
    _check_combat(game_state)


def _check_combat(game_state: "GameState") -> None:
    for attacker, defender in game_state.combat.attackers:
        if attacker not in attacker.controller.battlefield.cards:
            raise AssertionError("Attacker is not on the battlefield")
        if defender not in game_state.players:
            raise AssertionError("Defender is not a player in the game")
    attackers = [attacker for attacker, _ in game_state.combat.attackers]
    for attacker, blockers in game_state.combat.blockers:
        if attacker not in attackers:
            raise AssertionError("Blocker assigned to non-attacking creature")
        for blocker in blockers:
            if blocker not in blocker.controller.battlefield.cards:
                raise AssertionError("Blocker is not on the battlefield")


from py_mage.core.game_state import GameState  # noqa: E402
