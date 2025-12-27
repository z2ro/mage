from __future__ import annotations

from dataclasses import dataclass, field

from py_mage.core.mana import ManaPool
from py_mage.core.zones import Zone


@dataclass
class Player:
    name: str
    life: int = 20
    mana_pool: ManaPool = field(default_factory=ManaPool)
    library: Zone = field(default_factory=lambda: Zone("Library"))
    hand: Zone = field(default_factory=lambda: Zone("Hand"))
    battlefield: Zone = field(default_factory=lambda: Zone("Battlefield"))
    graveyard: Zone = field(default_factory=lambda: Zone("Graveyard"))
    exile: Zone = field(default_factory=lambda: Zone("Exile"))
    has_lost: bool = False

    def draw(self) -> None:
        if not self.library.cards:
            self.has_lost = True
            return
        self.hand.add(self.library.cards.pop())
