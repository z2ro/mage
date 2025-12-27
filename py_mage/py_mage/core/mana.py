from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ManaCost:
    generic: int = 0
    colored: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_string(cls, value: str) -> "ManaCost":
        generic = 0
        colored: Dict[str, int] = {}
        for symbol in value.replace("{", "").split("}"):
            if not symbol:
                continue
            if symbol.isdigit():
                generic += int(symbol)
            else:
                colored[symbol] = colored.get(symbol, 0) + 1
        return cls(generic=generic, colored=colored)

    def total(self) -> int:
        return self.generic + sum(self.colored.values())


@dataclass
class ManaPool:
    amounts: Dict[str, int] = field(default_factory=dict)

    def add(self, symbol: str, amount: int = 1) -> None:
        self.amounts[symbol] = self.amounts.get(symbol, 0) + amount

    def clear(self) -> None:
        self.amounts.clear()

    def can_pay(self, cost: ManaCost) -> bool:
        if sum(self.amounts.values()) < cost.total():
            return False
        for symbol, amount in cost.colored.items():
            if self.amounts.get(symbol, 0) < amount:
                return False
        return True

    def pay(self, cost: ManaCost) -> None:
        if not self.can_pay(cost):
            raise ValueError("Insufficient mana")
        for symbol, amount in cost.colored.items():
            self.amounts[symbol] -= amount
        remaining = cost.generic
        for symbol in list(self.amounts.keys()):
            if remaining <= 0:
                break
            spend = min(self.amounts[symbol], remaining)
            self.amounts[symbol] -= spend
            remaining -= spend
        if remaining > 0:
            raise ValueError("Could not spend generic mana")
