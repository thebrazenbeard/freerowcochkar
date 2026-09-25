# Roadmap

## Stage 0 — deterministic local audit

Status: implemented in the current V1 branch.

- clause heuristics;
- code heuristics;
- evidence-bound findings;
- CLI and JSON output;
- regression tests.

## Stage 1 — typed rule graph

Status: initial implementation present.

- `Rule` schema;
- modality extraction;
- normalized effects;
- typed constraint edges;
- delegation route representation;
- graph-based permission/prohibition search.

Exit condition: graph findings are emitted through the public analyzer and exact-head CI
covers positive and closure cases.

## Stage 2 — multi-step composition engine

Build a state-transition representation where a path can contain more than two rules.

Required capabilities:

- preconditions;
- postconditions;
- role/identity transitions;
- state mutation;
- temporal constraints;
- fallback transitions;
- exception activation;
- explicit precedence;
- path length bounds;
- cycle detection.

Exit condition: detect a loophole that requires at least three individually permitted
steps and prove that adding one hardening rule closes that path.

## Stage 3 — source-aware parsers

Add structured adapters for:

- Markdown instruction sets;
- YAML/JSON policy/configuration;
- Python AST;
- JavaScript/TypeScript AST;
- GitHub Actions;
- common authorization/policy formats.

Exit condition: source locations and semantics survive round-trip into the graph.

## Stage 4 — semantic equivalence layer

Add optional model-assisted or embedding-assisted suggestions for effects that may be
equivalent even when verbs differ.

Examples:

- remove / delete / purge;
- disclose / export / send;
- authorize / cause / direct.

These are candidates only and must retain a separate evidence class.

Exit condition: semantic suggestions cannot silently create deterministic findings.

## Stage 5 — policy/code cross-layer analysis

Analyze an instruction or policy together with its implementation.

Examples:

- policy forbids direct write; API fallback still writes;
- approval required in docs; CI workflow permits bypass;
- role prohibited in policy; configuration grants equivalent capability.

Exit condition: every cross-layer finding binds to exact versions of both sources.

## Stage 6 — hardening closure

Generate a proposed hardening patch plus a regression fixture proving the original path is
closed.

Exit condition: the tool can show before/after reachability, not merely prose advice.

## Stage 7 — repository/CI integration

Potential modes:

- pre-commit rule audit;
- pull-request review;
- policy-drift check;
- spec/code mismatch check;
- machine-readable SARIF-like output.

No repository mutation should occur by default.
