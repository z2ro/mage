# py_mage (Python Magic Engine)

Incremental migration of the MAGE rules engine to Python. This package focuses on
rules fidelity, determinism, and offline operation.

## Running offline

The engine runs without network access. The current phase ships a core rules loop,
zones, stack handling, and a minimal card subset for testing.

## Scryfall sync (optional)

This phase does **not** require network access. A future command will allow syncing
card images and metadata into a local cache for offline use.

## Deck import

Deck import and CLI gameplay will be introduced in Phase C.

## Development setup

Create a virtual environment and install the project in editable mode:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e py_mage[dev]
```

Run tests:

```bash
pytest -q
```

Run the validation harness:

```bash
python -m py_mage validate smoke --seed 123
python -m py_mage validate replay py_mage/py_mage/tests/golden/cast_spell_simple/input.json
python -m py_mage validate dump-state --out /tmp/state.json
```

Optional coverage tooling:

```bash
pip install pytest-cov
```

## MAGE catalog import (Phase B1)

```bash
python -m py_mage cards import-mage --out py_mage/data/mage_catalog.sqlite
```

Validate a catalog:

```bash
python -m py_mage cards validate --in py_mage/data/mage_catalog.sqlite --strict
```

Generate a report from an existing catalog:

```bash
python -m py_mage cards report --in py_mage/data/mage_catalog.sqlite --out py_mage/docs/CATALOG_REPORT.md
python -m py_mage cards report --in py_mage/data/mage_catalog.sqlite --out py_mage/docs/catalog_metrics.json --format json
```
