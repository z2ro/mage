from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, Iterable, List, TYPE_CHECKING


@dataclass(frozen=True)
class GameEvent:
    name: str
    payload: Dict[str, Any]


EventHandler = Callable[["GameState", GameEvent], Iterable["Ability"]]


class EventBus:
    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[EventHandler]] = DefaultDict(list)

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        self._handlers[event_name].append(handler)

    def emit(self, game_state: "GameState", event_name: str, **payload: Any) -> List["Ability"]:
        event = GameEvent(name=event_name, payload=payload)
        abilities: List["Ability"] = []
        for handler in self._handlers[event_name]:
            abilities.extend(handler(game_state, event))
        return abilities


if TYPE_CHECKING:
    from py_mage.core.abilities import Ability
    from py_mage.core.game_state import GameState
