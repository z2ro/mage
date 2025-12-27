#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install -e py_mage[dev]
pytest -q
python -m py_mage validate smoke --seed 123
if [[ "${VERIFY_FAST:-}" != "1" ]]; then
  python -m py_mage cards import-mage --out py_mage/data/mage_catalog.sqlite
  python -m py_mage cards validate --in py_mage/data/mage_catalog.sqlite --strict
  python -m py_mage cards report --in py_mage/data/mage_catalog.sqlite --out py_mage/docs/CATALOG_REPORT.md
fi
