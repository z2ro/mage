from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, TYPE_CHECKING


@dataclass
class StackItem:
    source: "Card"
    ability: "Ability"
    controller: Optional["Player"] = None


class Stack:
    def __init__(self) -> None:
        self.items: List[StackItem] = []

    def push(self, item: StackItem) -> None:
        self.items.append(item)

    def pop(self) -> StackItem:
        return self.items.pop()

    def peek(self) -> Optional[StackItem]:
        return self.items[-1] if self.items else None

    def is_empty(self) -> bool:
        return not self.items


if TYPE_CHECKING:
    from py_mage.core.abilities import Ability
    from py_mage.core.card import Card
    from py_mage.core.player import Player
