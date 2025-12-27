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
