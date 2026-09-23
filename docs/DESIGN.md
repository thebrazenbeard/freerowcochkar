# FreeRowCochkar design

## Core idea

A loophole exists when the literal reachable behavior of a rule system is broader than
its intended invariant.

FreeRowCochkar audits that gap.

It is not limited to statutes or contracts. The same structural failure appears in
natural-language instructions, prompt hierarchies, organizational policy, software
specifications, API contracts, source code, configuration, authorization logic, and
compliance systems where every local step can be technically allowed while the composed
result defeats the purpose.

## Adversarial model

The analyzer assumes a smart, motivated literalist who:

1. obeys what is actually written rather than what the author hoped was implied;
2. chooses favorable interpretations of undefined terms;
3. composes individually permitted steps;
4. prefers exception and low-friction paths;
5. exploits missing precedence and missing failure behavior;
6. distinguishes a prohibition on one action from silence about adjacent actions.

The output is a candidate loophole, never an assertion that exploitation is lawful,
safe, ethical, or correct.

## V1 detectors

- FRC-SCOPE-001: undefined qualifiers inside normative rules.
- FRC-EXC-001: exception surfaces capable of swallowing base rules.
- FRC-PREC-001: overlapping rules with conflicting polarity or permission.
- FRC-FAIL-001: mandatory external dependency without a nearby stated failure mode.
- FRC-INDIRECT-001: direct prohibition that omits delegated or equivalent indirect effects.
- FRC-CODE-001: swallowed exceptions.
- FRC-CODE-002: allow-by-default or fail-open signals.
- FRC-CODE-003: overbroad exception boundaries.

## Architecture direction

V1 is deterministic and dependency-free so findings are reproducible. Later layers can
add parsers and model-assisted semantic review, but model output should remain evidence
attached to a deterministic report rather than silently becoming truth.

The intended pipeline is:

ingest -> normalize -> extract rules -> build constraint graph -> search adversarial paths
-> produce evidence-bound findings -> propose hardening -> regression-test the loophole

The key future primitive is a constraint graph where nodes are states or actions and edges
are permission, obligation, prohibition, exception, precedence, fallback, or delegation.
Loophole search then becomes path search over the reachable behavior graph.
