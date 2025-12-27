# Migration Plan

## Status

**Phase A:** Engine foundations (in progress)

## Milestones

### Milestone 1 — Core engine + minimal playable subset
- [x] Game state, turns/steps, priority, stack
- [x] Zones and mana pool
- [x] State-based actions
- [x] Continuous effects skeleton (layers)
- [x] Trigger/event bus skeleton
- [x] Replacement/prevention framework skeleton
- [x] Minimal card subset (lands, creature, damage spell)
- [x] Initial regression tests

Known deviations for Milestone 1:
- Combat is stubbed (steps exist but no attacker/blocker handling).
- Continuous effect dependencies/timestamps are simplified.
- Triggered abilities are not auto-enqueued (manual use only).

### Milestone 2 — Common abilities + catalog import
- [ ] Importer for MAGE card data and Java ability mappings
- [ ] Library of common ability/effect primitives
- [ ] Initial coverage reporting

### Milestone 3 — Full catalog coverage + robust regression
- [ ] Broad card coverage with fewer stubs
- [ ] Headless Java MAGE comparison harness
- [ ] Expanded CLI play/testing
