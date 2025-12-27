from __future__ import annotations

from typing import Iterable, List

from py_mage.core.abilities import Ability, ActivatedAbility
from py_mage.core.card import Card, CardDefinition
from py_mage.core.game_state import GameState
from py_mage.core.mana import ManaCost


def forest_definition() -> CardDefinition:
    return CardDefinition(
        name="Forest",
        mana_cost=ManaCost(),
        types=("Land",),
        subtypes=("Forest",),
        abilities=(forest_mana_ability,),
    )


def forest_mana_ability(card: Card, game_state: GameState) -> Iterable[Ability]:
    def pay_cost(state: GameState, source: Card) -> None:
        if source.tapped:
            raise ValueError("Land already tapped")
        source.tapped = True

    def effect(state: GameState, stack_item) -> None:
        stack_item.controller.mana_pool.add("G", 1)

    return [ActivatedAbility(name="Tap: Add G", source=card, effect=effect, cost=pay_cost)]


def grizzly_bears_definition() -> CardDefinition:
    return CardDefinition(
        name="Grizzly Bears",
        mana_cost=ManaCost.from_string("{1}{G}"),
        types=("Creature",),
        subtypes=("Bear",),
        power=2,
        toughness=2,
    )


def lightning_bolt_definition() -> CardDefinition:
    return CardDefinition(
        name="Lightning Bolt",
        mana_cost=ManaCost.from_string("{R}"),
        types=("Instant",),
    )


def make_creature_spell(card: Card, target: Card | None = None) -> Ability:
    def effect(state: GameState, stack_item) -> None:
        card.controller.battlefield.add(card)
        card.zone = "Battlefield"
        for ability in _build_abilities(card, state):
            card.abilities.append(ability)

    return Ability(name=f"Resolve {card.name}", source=card, effect=effect, target=target)


def make_lightning_bolt_spell(card: Card, target: Card) -> Ability:
    def effect(state: GameState, stack_item) -> None:
        target.damage += 3

    return Ability(name="Lightning Bolt", source=card, effect=effect, target=target)


def _build_abilities(card: Card, game_state: GameState) -> List[Ability]:
    abilities: List[Ability] = []
    for factory in card.definition.abilities:
        abilities.extend(factory(card, game_state))
    return abilities
