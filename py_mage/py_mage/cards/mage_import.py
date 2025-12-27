from __future__ import annotations

import json
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from py_mage.cards.registry import get_definition

SET_CODE_RE = re.compile(r'super\(".*?",\s*"([^"]+)"')
SET_CARD_RE = re.compile(
    r'new SetCardInfo\("(?P<name>[^"]+)",\s*(?P<number>"[^"]+"|\d+),\s*Rarity\.(?P<rarity>[A-Z_]+),\s*(?P<class>mage\.cards\.[A-Za-z0-9_.]+)\.class'
)
TYPES_RE = re.compile(r"new CardType\[]\{([^}]+)\}")
TYPE_TOKEN_RE = re.compile(r"CardType\.([A-Z_]+)")
SUPERTYPE_RE = re.compile(r"supertype\.add\(SuperType\.([A-Z_]+)\)")
SUBTYPE_RE = re.compile(r"subtype\.add\(SubType\.([A-Z0-9_]+)\)")
MANA_RE = re.compile(r'new CardType\[]\{[^}]+\}\s*,\s*"([^"]*)"')
POWER_RE = re.compile(r"this\.power\s*=\s*new MageInt\(([-0-9]+)\)")
TOUGHNESS_RE = re.compile(r"this\.toughness\s*=\s*new MageInt\(([-0-9]+)\)")
ABILITY_RE = re.compile(r"new\s+([A-Za-z0-9]+Ability)")
ABILITY_INSTANCE_RE = re.compile(r"([A-Za-z0-9]+Ability)\.getInstance\(")

KNOWN_KEYWORDS = {
    "DeathtouchAbility",
    "DefenderAbility",
    "DoubleStrikeAbility",
    "FirstStrikeAbility",
    "FlashAbility",
    "FlyingAbility",
    "HasteAbility",
    "HexproofAbility",
    "IndestructibleAbility",
    "LifelinkAbility",
    "MenaceAbility",
    "ReachAbility",
    "TrampleAbility",
    "VigilanceAbility",
    "WardAbility",
}


@dataclass
class CardRecord:
    name: str
    set_code: str
    collector_number: str
    rarity: str
    card_class: str
    mana_cost: Optional[str]
    types: Sequence[str]
    supertypes: Sequence[str]
    subtypes: Sequence[str]
    power: Optional[int]
    toughness: Optional[int]
    keywords: Sequence[str]
    mana_parse_ok: bool
    types_parse_ok: bool
    source_path: str


def import_mage_cards(mage_root: Path, out_path: Path) -> tuple[Dict[str, int], Counter[str]]:
    records, metrics, keyword_counts = build_records(mage_root)
    write_sqlite(out_path, records)
    return metrics, keyword_counts


def build_records(mage_root: Path) -> tuple[List[CardRecord], Dict[str, int], Counter[str]]:
    set_dir = mage_root / "Mage.Sets" / "src" / "mage" / "sets"
    card_dir = mage_root / "Mage.Sets" / "src" / "mage" / "cards"
    records: List[CardRecord] = []
    mana_ok = 0
    mana_fail = 0
    types_ok = 0
    types_fail = 0
    keyword_counts: Counter[str] = Counter()

    for set_file in sorted(set_dir.glob("*.java")):
        content = set_file.read_text(encoding="utf-8", errors="ignore")
        set_code_match = SET_CODE_RE.search(content)
        if not set_code_match:
            continue
        set_code = set_code_match.group(1)
        for match in SET_CARD_RE.finditer(content):
            name = match.group("name")
            number = match.group("number").strip('"')
            rarity = match.group("rarity")
            card_class = match.group("class")
            class_path = card_dir / Path(card_class.replace("mage.cards.", "").replace(".", "/") + ".java")
            parsed = parse_card_class(class_path)
            for keyword in parsed.keywords:
                keyword_counts[keyword] += 1
            if parsed.mana_parse_ok:
                mana_ok += 1
            else:
                mana_fail += 1
            if parsed.types_parse_ok:
                types_ok += 1
            else:
                types_fail += 1
            records.append(
                CardRecord(
                    name=name,
                    set_code=set_code,
                    collector_number=number,
                    rarity=rarity,
                    card_class=card_class,
                    mana_cost=parsed.mana_cost,
                    types=parsed.types,
                    supertypes=parsed.supertypes,
                    subtypes=parsed.subtypes,
                    power=parsed.power,
                    toughness=parsed.toughness,
                    keywords=parsed.keywords,
                    mana_parse_ok=parsed.mana_parse_ok,
                    types_parse_ok=parsed.types_parse_ok,
                    source_path=str(class_path) if class_path.exists() else "",
                )
            )

    supported = count_supported(records)
    metrics = {
        "total_cards": len(records),
        "mana_parse_ok": mana_ok,
        "mana_parse_fail": mana_fail,
        "types_parse_ok": types_ok,
        "types_parse_fail": types_fail,
        "supported_cards": supported,
        "stub_required": len(records) - supported,
    }
    metrics.update(report_keywords(keyword_counts))
    return records, metrics, keyword_counts


def count_supported(records: Sequence[CardRecord]) -> int:
    supported = 0
    for record in records:
        try:
            get_definition(record.name)
        except KeyError:
            continue
        supported += 1
    return supported


def report_keywords(keyword_counts: Counter[str]) -> Dict[str, int]:
    recognized = sum(
        count for keyword, count in keyword_counts.items() if keyword in KNOWN_KEYWORDS
    )
    unknown = sum(
        count for keyword, count in keyword_counts.items() if keyword not in KNOWN_KEYWORDS
    )
    return {
        "keywords_recognized": recognized,
        "keywords_unknown": unknown,
    }


def keyword_top_unknown(keyword_counts: Counter[str], limit: int = 50) -> List[Tuple[str, int]]:
    unknown = [(kw, count) for kw, count in keyword_counts.items() if kw not in KNOWN_KEYWORDS]
    unknown.sort(key=lambda item: (-item[1], item[0]))
    return unknown[:limit]


def write_catalog_report(report_path: Path, metrics: Dict[str, int], keyword_counts: Counter[str]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    unknown_top = keyword_top_unknown(keyword_counts)
    lines = [
        "# MAGE Catalog Report (Phase B1)",
        "",
        "## Summary",
        f"- Total cards: {metrics['total_cards']}",
        f"- Mana parse ok: {metrics['mana_parse_ok']}",
        f"- Mana parse fail: {metrics['mana_parse_fail']}",
        f"- Types parse ok: {metrics['types_parse_ok']}",
        f"- Types parse fail: {metrics['types_parse_fail']}",
        f"- Keywords recognized: {metrics['keywords_recognized']}",
        f"- Keywords unknown: {metrics['keywords_unknown']}",
        f"- Fully supported: {metrics['supported_cards']}",
        f"- Stub required: {metrics['stub_required']}",
        "",
        "## Top 50 Unknown Keywords",
        "",
    ]
    for keyword, count in unknown_top:
        lines.append(f"- {keyword}: {count}")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@dataclass
class ParsedCard:
    mana_cost: Optional[str]
    types: Sequence[str]
    supertypes: Sequence[str]
    subtypes: Sequence[str]
    power: Optional[int]
    toughness: Optional[int]
    keywords: Sequence[str]
    mana_parse_ok: bool
    types_parse_ok: bool


def parse_card_class(path: Path) -> ParsedCard:
    if not path.exists():
        return ParsedCard(
            mana_cost=None,
            types=(),
            supertypes=(),
            subtypes=(),
            power=None,
            toughness=None,
            keywords=(),
            mana_parse_ok=False,
            types_parse_ok=False,
        )
    content = path.read_text(encoding="utf-8", errors="ignore")
    types = parse_types(content)
    supertypes = SUPERTYPE_RE.findall(content)
    subtypes = SUBTYPE_RE.findall(content)
    mana_cost = parse_mana_cost_from_source(content)
    mana_parse_ok = mana_cost is None or validate_mana_cost(mana_cost)
    types_parse_ok = bool(types)
    power = parse_int(POWER_RE.search(content))
    toughness = parse_int(TOUGHNESS_RE.search(content))
    keywords = parse_keywords(content)
    return ParsedCard(
        mana_cost=mana_cost,
        types=types,
        supertypes=supertypes,
        subtypes=subtypes,
        power=power,
        toughness=toughness,
        keywords=keywords,
        mana_parse_ok=mana_parse_ok,
        types_parse_ok=types_parse_ok,
    )


def parse_types(content: str) -> Sequence[str]:
    match = TYPES_RE.search(content)
    if not match:
        return ()
    return TYPE_TOKEN_RE.findall(match.group(1))


def parse_mana_cost_from_source(content: str) -> Optional[str]:
    match = MANA_RE.search(content)
    if not match:
        return None
    return match.group(1).strip()


def validate_mana_cost(mana_cost: str) -> bool:
    if mana_cost == "":
        return True
    tokens = re.findall(r"\{([^}]+)\}", mana_cost)
    reconstructed = "".join(f"{{{token}}}" for token in tokens)
    if reconstructed != mana_cost:
        return False
    for token in tokens:
        if not re.fullmatch(r"[0-9A-Z/]+", token):
            return False
    return True


def parse_keywords(content: str) -> Sequence[str]:
    keywords = set(ABILITY_RE.findall(content))
    keywords.update(ABILITY_INSTANCE_RE.findall(content))
    return sorted(keywords)


def parse_int(match: Optional[re.Match[str]]) -> Optional[int]:
    if not match:
        return None
    return int(match.group(1))


def write_sqlite(path: Path, records: Iterable[CardRecord]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(path)
    try:
        conn.execute(
            """
            CREATE TABLE cards (
                name TEXT NOT NULL,
                set_code TEXT NOT NULL,
                collector_number TEXT NOT NULL,
                rarity TEXT NOT NULL,
                card_class TEXT NOT NULL,
                mana_cost TEXT,
                types TEXT,
                supertypes TEXT,
                subtypes TEXT,
                power INTEGER,
                toughness INTEGER,
                keywords TEXT,
                mana_parse_ok INTEGER NOT NULL,
                types_parse_ok INTEGER NOT NULL,
                source_path TEXT
            )
            """
        )
        conn.executemany(
            """
            INSERT INTO cards (
                name,
                set_code,
                collector_number,
                rarity,
                card_class,
                mana_cost,
                types,
                supertypes,
                subtypes,
                power,
                toughness,
                keywords,
                mana_parse_ok,
                types_parse_ok,
                source_path
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    record.name,
                    record.set_code,
                    record.collector_number,
                    record.rarity,
                    record.card_class,
                    record.mana_cost,
                    json.dumps(record.types),
                    json.dumps(record.supertypes),
                    json.dumps(record.subtypes),
                    record.power,
                    record.toughness,
                    json.dumps(record.keywords),
                    int(record.mana_parse_ok),
                    int(record.types_parse_ok),
                    record.source_path,
                )
                for record in records
            ],
        )
        conn.commit()
    finally:
        conn.close()
