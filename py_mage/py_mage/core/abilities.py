from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, TYPE_CHECKING


Effect = Callable[["GameState", "StackItem"], None]


@dataclass
class Ability:
    name: str
    source: "Card"
    effect: Effect
    target: Optional["Card"] = None

    def resolve(self, game_state: "GameState", stack_item: "StackItem") -> None:
        self.effect(game_state, stack_item)


@dataclass
class ActivatedAbility(Ability):
    cost: Optional[Callable[["GameState", "Card"], None]] = None

    def activate(self, game_state: "GameState") -> None:
        if self.cost:
            self.cost(game_state, self.source)
        from py_mage.core.stack import StackItem

        game_state.stack.push(StackItem(self.source, self, controller=self.source.controller))


if TYPE_CHECKING:
    from py_mage.core.card import Card
    from py_mage.core.game_state import GameState
    from py_mage.core.stack import StackItem
