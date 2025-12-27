from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, List, TYPE_CHECKING


class Layer(Enum):
    COPY = 1
    CONTROL = 2
    TEXT = 3
    TYPE = 4
    COLOR = 5
    ABILITY = 6
    POWER_TOUGHNESS = 7


LayerEffect = Callable[["GameState"], None]


@dataclass
class ContinuousEffect:
    layer: Layer
    apply: LayerEffect
    timestamp: int
    description: str = ""


class ContinuousEffects:
    def __init__(self) -> None:
        self.effects: List[ContinuousEffect] = []

    def add(self, effect: ContinuousEffect) -> None:
        self.effects.append(effect)

    def apply(self, game_state: "GameState") -> None:
        for effect in sorted(self.effects, key=lambda item: (item.layer.value, item.timestamp)):
            effect.apply(game_state)


if TYPE_CHECKING:
    from py_mage.core.game_state import GameState
