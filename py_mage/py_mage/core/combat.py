from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CombatState:
    attackers: List[Tuple["Card", "Player"]] = field(default_factory=list)
    blockers: List[Tuple["Card", List["Card"]]] = field(default_factory=list)

    def clear(self) -> None:
        self.attackers.clear()
        self.blockers.clear()


from py_mage.core.card import Card  # noqa: E402
from py_mage.core.player import Player  # noqa: E402
