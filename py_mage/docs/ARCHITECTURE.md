# Architecture Overview

## Event Loop
- The `GameState` owns the main loop primitives: stack, priority, and turn steps.
- `pass_priority` resolves the stack when all players pass or advances the step.

## Priority + Stack
- `PriorityManager` tracks consecutive passes.
- `Stack` is LIFO of `StackItem` entries (spell/ability).

## State-Based Actions (SBAs)
- `StateBasedActions.check` runs after changes to move dead creatures to graveyards
  and declare players with 0 life as having lost.

## Continuous Effects + Layers
- `ContinuousEffects` stores layered effects (rules 613 skeleton).
- Effects are applied in layer order with timestamp ordering.

## Triggers
- `EventBus.emit` returns abilities that can be placed on the stack.
- Triggered ability placement is explicit in Phase A (future automation).

## Replacement/Prevention
- `ReplacementEffects.handle` allows effects to replace events.
- Currently a placeholder for future hooks.
