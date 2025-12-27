# Validation Harness

## Quick verification

```bash
./py_mage/verify.sh
```

On Windows (PowerShell):

```powershell
.\py_mage\verify.ps1
```

## Golden tests

Each scenario lives under `py_mage/py_mage/tests/golden/<scenario>/` and includes:

- `input.json` (seed + initial zones + action sequence)
- `expected_state.json` (serialized final state)
- `expected_log.txt` (normalized log output)

To add a new golden test:

1. Create a new scenario directory.
2. Provide an `input.json` script and run:
   ```bash
   python -m py_mage validate replay <input.json> --out /tmp/state.json --log /tmp/log.txt
   ```
3. Copy `/tmp/state.json` to `expected_state.json` and `/tmp/log.txt` to `expected_log.txt`.
4. Add a test entry in `py_mage/py_mage/tests/test_golden.py`.

## Debugging differences

If a golden test fails:

- Compare logs (`expected_log.txt` vs actual) to see which action diverged.
- Compare `expected_state.json` with the new state dump to locate mismatched zones or damage.
- Re-run with `--assert-invariants` to catch structural issues early.

## Known deviations (Phase A)

- Combat resolution only supports one blocker per attacker and no abilities (first strike, trample, etc.).
- No triggered ability automation; actions must explicitly call `check_sba`.
- Continuous effect dependencies/timestamps are simplified.
