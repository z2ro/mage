python -m venv .venv
. .\.venv\Scripts\Activate.ps1
pip install -e py_mage[dev]
pytest -q
python -m py_mage validate smoke --seed 123
