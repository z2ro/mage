from __future__ import annotations

from typing import Dict

from py_mage.cards.basic import (
    forest_definition,
    grizzly_bears_definition,
    lightning_bolt_definition,
    mountain_definition,
)
from py_mage.core.card import CardDefinition


_REGISTRY: Dict[str, CardDefinition] = {
    "Forest": forest_definition(),
    "Mountain": mountain_definition(),
    "Grizzly Bears": grizzly_bears_definition(),
    "Lightning Bolt": lightning_bolt_definition(),
}


def get_definition(name: str) -> CardDefinition:
    try:
        return _REGISTRY[name]
    except KeyError as exc:
        raise KeyError(f"Unknown card: {name}") from exc
