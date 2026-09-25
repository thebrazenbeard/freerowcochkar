> **License:** Source-visible, not open source. Original material is proprietary. Commercial use, redistribution, hosted-service use, and commercial derivative products require written permission. See [LICENSE](LICENSE) and [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md). Separately identified third-party components retain their own licenses.

# FreeRowCochkar

A defensive adversarial loophole finder inspired by the literalist, boundary-testing
reasoning associated with Nick Freeman, Clarence Darrow, Johnnie Cochran, and
B. R. Ambedkar.

The name is a mashup; the actual project is broader than law.

FreeRowCochkar asks a specific question:

> Where can someone obey the written rules literally while defeating what the system
> was clearly built to accomplish?

That question applies to legal and policy text, AI or human instructions, software
specifications, code, configuration, authorization systems, operating procedures, and
compliance controls.

## What the deterministic core does

The first implementation is deterministic and dependency-free. It reports candidate
loopholes with exact evidence, an adversarial literal-reading path, and a hardening
suggestion.

Current detectors cover:

- vague qualifiers inside mandatory or prohibitive rules;
- exceptions that can swallow a base rule;
- overlapping instructions with conflicting permission or prohibition;
- required external dependencies with no defined failure path;
- prohibitions that cover direct action but omit delegated or indirect equivalents;
- swallowed exceptions in code;
- broad exception boundaries;
- fail-open and allow-by-default code signals;
- three-or-more-step permitted state-transition chains that terminate in an explicitly
  forbidden state, with cycle-safe bounded search and regression-proven closure.

This is intentionally an auditor, not an oracle. A finding means "inspect this boundary,"
not "this is definitely exploitable" and not "this behavior is lawful."

## Install

~~~bash
python -m pip install -e .
~~~

## Use

Audit an instruction or policy file:

~~~bash
freerowcochkar policy.md
~~~

Audit code:

~~~bash
freerowcochkar auth.py --profile code
~~~

Pipe text directly:

~~~bash
printf 'Operators must take reasonable steps before release.' | freerowcochkar -
~~~

Add the invariant the author actually intended:

~~~bash
freerowcochkar rules.md --intent "No protected effect occurs without explicit authorization"
~~~

Machine-readable finding output:

~~~bash
freerowcochkar rules.md --json
~~~

Inspect the extracted rule/constraint graph and adversarial paths:

~~~bash
freerowcochkar rules.md --graph-json
~~~

## Example

Input:

~~~text
Operators must not export customer records.
Operators may export customer records for support.
~~~

FreeRowCochkar flags a precedence collision because a motivated literalist can point to
the permissive rule and claim that "for support" controls the prohibition. The hardening
question is then concrete: who can invoke that exception, under what conditions, with
what scope, and which invariant remains non-waivable?

## Direction

The deterministic core now includes typed rules, a constraint graph, and a bounded
multi-step state-transition search:

~~~text
rule text
  -> obligations / permissions / prohibitions / transitions
  -> state-and-action graph
  -> bounded adversarial path search
  -> evidence-bound loophole candidate
  -> hardening rewrite
  -> regression case proving the path closes
~~~

The current Stage-2 grammar is deliberately explicit rather than semantic: it recognizes
state-transition sentences and forbidden terminal states without guessing equivalence.
The next work is to enrich transition semantics with preconditions, role changes,
temporal constraints, fallback/exception activation, and explicit precedence while
preserving deterministic provenance.

Architecture is committed in the repository:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system layers, graph model, evidence classes, failure model, and package boundaries.
- [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) — the motivated-literalist adversary and protected properties.
- [docs/ROADMAP.md](docs/ROADMAP.md) — staged path from deterministic linting to multi-step compositional search and policy/code comparison.
- [docs/DESIGN.md](docs/DESIGN.md) — concise design rationale and detector inventory.
