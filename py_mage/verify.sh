#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
source .venv/bin/activate
pip install -e py_mage[dev]
pytest -q
python -m py_mage validate smoke --seed 123
