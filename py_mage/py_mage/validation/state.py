from __future__ import annotations

from typing import Any, Dict, List


def serialize_game_state(game_state: "GameState") -> Dict[str, Any]:
    return {
        "turn": game_state.turn_manager.current_step().value,
        "players": [serialize_player(player) for player in game_state.players],
        "stack": [serialize_stack_item(item) for item in game_state.stack.items],
    }


def serialize_player(player: "Player") -> Dict[str, Any]:
    return {
        "name": player.name,
        "life": player.life,
        "mana_pool": dict(player.mana_pool.amounts),
        "zones": {
            "library": serialize_zone(player.library.cards),
            "hand": serialize_zone(player.hand.cards),
            "battlefield": serialize_zone(player.battlefield.cards),
            "graveyard": serialize_zone(player.graveyard.cards),
            "exile": serialize_zone(player.exile.cards),
        },
    }


def serialize_zone(cards: List["Card"]) -> List[Dict[str, Any]]:
    return [serialize_card(card) for card in cards]


def serialize_card(card: "Card") -> Dict[str, Any]:
    return {
        "name": card.name,
        "tapped": card.tapped,
        "damage": card.damage,
        "power": card.power,
        "toughness": card.toughness,
    }


def serialize_stack_item(item: "StackItem") -> Dict[str, Any]:
    return {
        "source": item.source.name,
        "ability": item.ability.name,
        "controller": item.controller.name if item.controller else None,
    }


from py_mage.core.card import Card  # noqa: E402
from py_mage.core.game_state import GameState  # noqa: E402
from py_mage.core.player import Player  # noqa: E402
from py_mage.core.stack import StackItem  # noqa: E402
