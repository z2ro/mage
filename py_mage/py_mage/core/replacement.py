from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TYPE_CHECKING


ReplacementEffect = Callable[["GameState", "GameEvent"], bool]


@dataclass
class Replacement:
    name: str
    applies: ReplacementEffect


class ReplacementEffects:
    def __init__(self) -> None:
        self.effects: list[Replacement] = []

    def add(self, effect: Replacement) -> None:
        self.effects.append(effect)

    def handle(self, game_state: "GameState", event: "GameEvent") -> bool:
        for effect in self.effects:
            if effect.applies(game_state, event):
                return True
        return False


if TYPE_CHECKING:
    from py_mage.core.events import GameEvent
    from py_mage.core.game_state import GameState
