# Threat Model

## Adversary

FreeRowCochkar assumes a motivated literalist.

The adversary is not assumed to break a rule. The interesting case is an actor who tries
to produce a forbidden or unintended outcome while maintaining a plausible argument that
every local step complied with the written system.

Capabilities may include:

- choosing among overlapping rules;
- selecting favorable interpretations of undefined qualifiers;
- invoking exceptions;
- delegating an action;
- changing roles or routes;
- triggering failure/fallback behavior;
- composing individually permitted steps;
- exploiting timing, retries, stale state, or version mismatch;
- using a lower layer when a higher-layer prohibition is not enforced there.

## Protected property

The protected property is the intended invariant supplied by the author or inferred only
when a deterministic source rule establishes it.

Examples:

- no protected effect without explicit authorization;
- no disclosure of protected data;
- no merge/deploy without the required approval;
- no state transition that bypasses a validation gate.

## Primary weakness classes

### Ambiguity
A rule depends on a term whose boundary is undefined.

### Negative-space gap
The system prohibits one route but is silent about an equivalent adjacent route.

### Delegation laundering
The actor cannot perform an effect directly but can cause another actor/tool to perform it.

### Permission/prohibition collision
Two rules govern the same effect in opposite directions without explicit precedence.

### Exception swallowing
An exception is broader or easier to invoke than the base rule suggests.

### Failure-path laundering
A required dependency or validation step has no defined behavior when unavailable.

### Cross-layer mismatch
Policy says one thing while code/configuration permits another.

### Composition gap
Each step is individually allowed while the combined sequence reaches a forbidden outcome.

## Defender assumptions

The defender wants findings that are:

- source-bound;
- reproducible;
- reviewable;
- narrow enough to harden;
- testable after hardening.

A finding that cannot show its evidence path is low value.

## Safety boundary

Finding a path is distinct from executing it.

The base engine produces structural analysis and hardening guidance. Integration layers
that can mutate systems, send requests, change permissions, deploy code, or otherwise
exercise a path must implement their own authority checks.
