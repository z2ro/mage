from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional, Sequence, TYPE_CHECKING

from py_mage.core.mana import ManaCost


@dataclass(frozen=True)
class CardDefinition:
    name: str
    mana_cost: ManaCost
    types: Sequence[str]
    subtypes: Sequence[str] = ()
    power: Optional[int] = None
    toughness: Optional[int] = None
    abilities: Sequence["AbilityFactory"] = ()


AbilityFactory = Callable[["Card", "GameState"], Iterable["Ability"]]


@dataclass
class Card:
    definition: CardDefinition
    owner: "Player"
    controller: "Player"
    tapped: bool = False
    damage: int = 0
    zone: Optional[str] = None
    timestamp: int = 0

    def __post_init__(self) -> None:
        self.types = list(self.definition.types)
        self.subtypes = list(self.definition.subtypes)
        self.power = self.definition.power
        self.toughness = self.definition.toughness
        self.abilities: List[Ability] = []

    @property
    def name(self) -> str:
        return self.definition.name

    @property
    def mana_cost(self) -> ManaCost:
        return self.definition.mana_cost

    def is_type(self, card_type: str) -> bool:
        return card_type in self.types

    def clone_for_stack(self) -> "Card":
        return Card(definition=self.definition, owner=self.owner, controller=self.controller)


if TYPE_CHECKING:
    from py_mage.core.abilities import Ability
    from py_mage.core.game_state import GameState
    from py_mage.core.player import Player
