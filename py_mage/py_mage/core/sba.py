from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING


@dataclass
class StateBasedActions:
    def check(self, game_state: "GameState") -> List[str]:
        results: List[str] = []
        for player in game_state.players:
            if player.life <= 0:
                player.has_lost = True
                results.append(f"{player.name} loses the game")
        for player in game_state.players:
            for card in list(player.battlefield.cards):
                if card.toughness is not None and card.damage >= card.toughness:
                    player.battlefield.remove(card)
                    player.graveyard.add(card)
                    results.append(f"{card.name} died")
        return results


if TYPE_CHECKING:
    from py_mage.core.game_state import GameState
