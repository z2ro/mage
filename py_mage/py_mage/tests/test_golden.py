from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


GOLDEN_DIR = Path(__file__).parent / "golden"


def run_replay(scenario: str, tmp_path: Path) -> tuple[str, dict]:
    scenario_dir = GOLDEN_DIR / scenario
    input_path = scenario_dir / "input.json"
    out_state = tmp_path / f"{scenario}_state.json"
    out_log = tmp_path / f"{scenario}_log.txt"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "py_mage",
            "validate",
            "replay",
            str(input_path),
            "--out",
            str(out_state),
            "--log",
            str(out_log),
            "--assert-invariants",
        ],
        check=True,
    )
    return out_log.read_text(encoding="utf-8"), json.loads(out_state.read_text(encoding="utf-8"))


def assert_golden(scenario: str, tmp_path: Path) -> None:
    scenario_dir = GOLDEN_DIR / scenario
    expected_log = (scenario_dir / "expected_log.txt").read_text(encoding="utf-8")
    expected_state = json.loads((scenario_dir / "expected_state.json").read_text(encoding="utf-8"))
    actual_log, actual_state = run_replay(scenario, tmp_path)
    assert actual_log == expected_log
    assert actual_state == expected_state


def test_cast_spell_simple(tmp_path: Path) -> None:
    assert_golden("cast_spell_simple", tmp_path)


def test_mana_payment(tmp_path: Path) -> None:
    assert_golden("mana_payment", tmp_path)


def test_combat_simple(tmp_path: Path) -> None:
    assert_golden("combat_simple", tmp_path)
