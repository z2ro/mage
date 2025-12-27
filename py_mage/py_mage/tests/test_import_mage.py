from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path

from py_mage.cards.mage_import import import_mage_cards


EXPECTED_CARD_COUNT = 87360


def read_hash(db_path: Path) -> str:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT name, set_code, collector_number, rarity, card_class FROM cards ORDER BY name, set_code, collector_number"
        ).fetchall()
    finally:
        conn.close()
    hasher = hashlib.sha256()
    for row in rows:
        hasher.update("|".join(str(col) for col in row).encode("utf-8"))
        hasher.update(b"\n")
    return hasher.hexdigest()


def count_cards(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT COUNT(*) FROM cards").fetchone()[0]
    finally:
        conn.close()


def test_import_is_deterministic(tmp_path: Path) -> None:
    mage_root = Path(__file__).resolve().parents[3]
    first = tmp_path / "first.sqlite"
    second = tmp_path / "second.sqlite"
    import_mage_cards(mage_root, first)
    import_mage_cards(mage_root, second)
    assert count_cards(first) == count_cards(second)
    assert read_hash(first) == read_hash(second)


def test_import_card_count_is_stable(tmp_path: Path) -> None:
    mage_root = Path(__file__).resolve().parents[3]
    out = tmp_path / "catalog.sqlite"
    import_mage_cards(mage_root, out)
    assert count_cards(out) == EXPECTED_CARD_COUNT
