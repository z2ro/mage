python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e py_mage[dev]
pytest -q
python -m py_mage validate smoke --seed 123
if ($env:VERIFY_FAST -ne "1") {
    python -m py_mage cards import-mage --out py_mage/data/mage_catalog.sqlite
    python -m py_mage cards validate --in py_mage/data/mage_catalog.sqlite --strict
    python -m py_mage cards report --in py_mage/data/mage_catalog.sqlite --out py_mage/docs/CATALOG_REPORT.md
}
