from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, TYPE_CHECKING


@dataclass
class Zone:
    name: str
    cards: List["Card"] = field(default_factory=list)

    def add(self, card: "Card") -> None:
        self.cards.append(card)

    def remove(self, card: "Card") -> None:
        self.cards.remove(card)

    def extend(self, cards: Iterable["Card"]) -> None:
        self.cards.extend(cards)


if TYPE_CHECKING:
    from py_mage.core.card import Card
