from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional

from py_mage.core.abilities import Ability
from py_mage.core.events import EventBus
from py_mage.core.layers import ContinuousEffects
from py_mage.core.priority import PriorityManager
from py_mage.core.replacement import ReplacementEffects
from py_mage.core.sba import StateBasedActions
from py_mage.core.stack import Stack, StackItem
from py_mage.core.turn import Step, TurnManager


@dataclass
class GameState:
    players: List["Player"]
    stack: Stack = field(default_factory=Stack)
    turn_manager: TurnManager = field(default_factory=TurnManager)
    priority_manager: PriorityManager = field(default_factory=PriorityManager)
    continuous_effects: ContinuousEffects = field(default_factory=ContinuousEffects)
    replacement_effects: ReplacementEffects = field(default_factory=ReplacementEffects)
    event_bus: EventBus = field(default_factory=EventBus)
    sba: StateBasedActions = field(default_factory=StateBasedActions)
    active_player_index: int = 0
    timestamp_counter: int = 0

    def active_player(self) -> "Player":
        return self.players[self.active_player_index]

    def non_active_players(self) -> Iterable["Player"]:
        for index, player in enumerate(self.players):
            if index != self.active_player_index:
                yield player

    def start(self) -> None:
        for player in self.players:
            for _ in range(7):
                player.draw()

    def advance_step(self) -> Step:
        step = self.turn_manager.advance()
        if step == Step.UNTAP:
            for card in self.active_player().battlefield.cards:
                card.tapped = False
            self.active_player().mana_pool.clear()
        if step == Step.DRAW:
            self.active_player().draw()
        self.priority_manager.reset()
        return step

    def apply_continuous_effects(self) -> None:
        self.continuous_effects.apply(self)

    def check_state_based_actions(self) -> List[str]:
        return self.sba.check(self)

    def add_to_stack(self, source: "Card", ability: Ability, controller: Optional["Player"] = None) -> None:
        self.stack.push(StackItem(source=source, ability=ability, controller=controller))

    def resolve_top(self) -> None:
        if self.stack.is_empty():
            return
        item = self.stack.pop()
        item.ability.resolve(self, item)
        if item.source.is_type("Instant") or item.source.is_type("Sorcery"):
            item.source.owner.graveyard.add(item.source)
        self.event_bus.emit(self, "resolved", item=item)

    def pass_priority(self) -> None:
        all_passed = self.priority_manager.pass_priority(len(self.players))
        if all_passed:
            if not self.stack.is_empty():
                self.resolve_top()
            else:
                self.advance_step()

    def cast_spell(self, player: "Player", card: "Card", ability: Ability) -> None:
        if not player.mana_pool.can_pay(card.mana_cost):
            raise ValueError("Cannot pay mana cost")
        player.mana_pool.pay(card.mana_cost)
        player.hand.remove(card)
        self.add_to_stack(card, ability, controller=player)

    def next_timestamp(self) -> int:
        self.timestamp_counter += 1
        return self.timestamp_counter


from py_mage.core.card import Card  # noqa: E402
from py_mage.core.player import Player  # noqa: E402
