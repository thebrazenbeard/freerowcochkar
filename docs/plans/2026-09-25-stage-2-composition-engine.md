# Stage-2 Composition Engine Implementation Plan

> **For agentic workers:** Use the host's available task-by-task implementation workflow. Steps use checkbox syntax for tracking.

**Goal:** Detect a prohibited terminal state reachable through at least three individually permitted state transitions, then prove that an explicit hardening prohibition closes that path.

**Architecture:** Add deterministic state-transition extraction beside the existing rule parser, feed typed transitions and forbidden states into ConstraintGraph, and run bounded cycle-safe path search. A transition is traversable only when it is permitted and is not exactly blocked by a matching prohibition.

**Tech Stack:** Python 3.10+, dataclasses, regex parsing, unittest, existing dependency-free package.

## Global Constraints

- Preserve exact source spans and deterministic output.
- Require at least three permitted transitions before emitting a composition finding.
- Bound search depth and prevent cycles from producing unbounded traversal.
- Hardening closure must be executable evidence: the vulnerable fixture finds the path and the hardened rewrite removes it.
- Keep findings as structural candidates, not claims of real-world exploitability.

### Task 1: State-transition extraction

- [x] Add StateTransition and ForbiddenState records.
- [x] Add extract_state_model(text) for explicit transition and forbidden-state grammar.
- [x] Add focused parser tests.

### Task 2: Bounded compositional path search

- [x] Add FRC-PATH-COMPOSE / composition_gap path search.
- [x] Require at least three permitted transitions.
- [x] Bound depth and prevent repeated-state cycles.
- [x] Add two-step and cycle negative tests.

### Task 3: Hardening closure and analyzer integration

- [x] Emit composition_gap through analyze(text).
- [x] Prove vulnerable-before / hardened-after closure.
- [x] Integrate state model into --graph-json.
- [x] Add positive and closure corpus fixtures.

### Task 4: Exact-head verification and documentation

- [x] Update architecture, roadmap, benchmarks, and README.
- [ ] Run full unittest suite at exact head.
- [ ] Run git diff origin/main...HEAD --check.
- [ ] Verify graph-json output and exact branch/PR head.
