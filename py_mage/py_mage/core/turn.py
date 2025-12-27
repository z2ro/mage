from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator, List


class Step(Enum):
    UNTAP = "untap"
    UPKEEP = "upkeep"
    DRAW = "draw"
    MAIN1 = "main1"
    COMBAT_BEGIN = "combat_begin"
    DECLARE_ATTACKERS = "declare_attackers"
    DECLARE_BLOCKERS = "declare_blockers"
    COMBAT_DAMAGE = "combat_damage"
    COMBAT_END = "combat_end"
    MAIN2 = "main2"
    END = "end"
    CLEANUP = "cleanup"


@dataclass
class TurnManager:
    steps: List[Step] = None
    current_index: int = 0

    def __post_init__(self) -> None:
        if self.steps is None:
            self.steps = list(Step)

    def current_step(self) -> Step:
        return self.steps[self.current_index]

    def advance(self) -> Step:
        self.current_index = (self.current_index + 1) % len(self.steps)
        return self.current_step()

    def iter_steps(self) -> Iterator[Step]:
        for _ in range(len(self.steps)):
            yield self.current_step()
            self.advance()
