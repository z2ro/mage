from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PriorityManager:
    active_player_index: int = 0
    passed: int = 0

    def reset(self) -> None:
        self.passed = 0

    def pass_priority(self, total_players: int) -> bool:
        self.passed += 1
        if self.passed >= total_players:
            self.passed = 0
            return True
        return False

    def next_player(self, total_players: int) -> int:
        self.active_player_index = (self.active_player_index + 1) % total_players
        return self.active_player_index
