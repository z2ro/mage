from __future__ import annotations

import argparse
from pathlib import Path

from py_mage.cards.mage_import import import_mage_cards, write_catalog_report
from py_mage.validation.runner import dump_state, run_script, run_smoke


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="py_mage")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validation harness")
    validate_sub = validate.add_subparsers(dest="validate_cmd", required=True)

    smoke = validate_sub.add_parser("smoke", help="Run deterministic smoke scenario")
    smoke.add_argument("--seed", type=int, required=True)
    smoke.add_argument("--assert-invariants", action="store_true")

    dump_state_cmd = validate_sub.add_parser("dump-state", help="Dump state to JSON")
    dump_state_cmd.add_argument("--out", type=Path, required=True)
    dump_state_cmd.add_argument("--seed", type=int, default=123)
    dump_state_cmd.add_argument("--assert-invariants", action="store_true")

    replay = validate_sub.add_parser("replay", help="Replay an action script")
    replay.add_argument("input", type=Path)
    replay.add_argument("--out", type=Path, required=True)
    replay.add_argument("--log", type=Path, required=True)
    replay.add_argument("--assert-invariants", action="store_true")

    cards = subparsers.add_parser("cards", help="Card catalog tools")
    cards_sub = cards.add_subparsers(dest="cards_cmd", required=True)
    import_cmd = cards_sub.add_parser("import-mage", help="Import MAGE card catalog")
    import_cmd.add_argument("--out", type=Path, required=True)
    import_cmd.add_argument(
        "--report",
        type=Path,
        default=Path("py_mage/docs/CATALOG_REPORT.md"),
    )
    import_cmd.add_argument(
        "--mage-root",
        type=Path,
        default=Path.cwd(),
        help="Path to the MAGE repository root",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "validate" and args.validate_cmd == "smoke":
        state, log = run_smoke(seed=args.seed, assert_invariants=args.assert_invariants)
        print("\n".join(log))
        return
    if args.command == "validate" and args.validate_cmd == "dump-state":
        state, _ = run_smoke(seed=args.seed, assert_invariants=args.assert_invariants)
        dump_state(state, args.out)
        return
    if args.command == "validate" and args.validate_cmd == "replay":
        state, log = run_script(args.input, assert_invariants=args.assert_invariants)
        dump_state(state, args.out)
        args.log.write_text("\n".join(log) + "\n", encoding="utf-8")
        return
    if args.command == "cards" and args.cards_cmd == "import-mage":
        metrics, keyword_counts = import_mage_cards(args.mage_root, args.out)
        write_catalog_report(args.report, metrics, keyword_counts)
        print(f"Wrote catalog to {args.out}")
        print(f"Wrote report to {args.report}")
        return
    parser.print_help()
