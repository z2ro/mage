from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from py_mage.cards.mage_import import import_mage_cards


def run_report(catalog: Path, out_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "py_mage",
            "cards",
            "report",
            "--in",
            str(catalog),
            "--out",
            str(out_path),
        ],
        check=True,
    )


def test_cards_report_deterministic(tmp_path: Path) -> None:
    mage_root = Path(__file__).resolve().parents[3]
    catalog = tmp_path / "catalog.sqlite"
    import_mage_cards(mage_root, catalog)
    first = tmp_path / "report1.md"
    second = tmp_path / "report2.md"
    run_report(catalog, first)
    run_report(catalog, second)
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_metrics_split(tmp_path: Path) -> None:
    mage_root = Path(__file__).resolve().parents[3]
    catalog = tmp_path / "catalog.sqlite"
    import_mage_cards(mage_root, catalog)
    report_path = tmp_path / "report.md"
    run_report(catalog, report_path)
    data = report_path.read_text(encoding="utf-8")
    assert "## Magic Keywords" in data
    assert "## MAGE Ability/Effect Types" in data
    assert "## Parse/Schema Stats" in data
    magic_section = data.split("## Magic Keywords", 1)[1].split("## MAGE Ability/Effect Types", 1)[0]
    assert "SimpleActivatedAbility" not in magic_section
