# Adversarial Benchmark Corpus

FreeRowCochkar's detector changes are evaluated against a checked-in deterministic corpus.

Current corpus:

`tests/fixtures/v1_cases.json`

## Case contract

Each case contains:

```json
{
  "id": "stable-case-id",
  "profile": "instructions | code | mixed",
  "text": "source under analysis",
  "must_include": ["finding_category"],
  "must_exclude": ["finding_category"]
}
```

A case is not a claim that the example is a real-world legal or security exploit. It is a
regression contract for a structural analysis behavior.

## Why both positive and negative expectations matter

A loophole finder can become useless by maximizing findings. The corpus therefore tests
both directions:

- `must_include` prevents known loophole shapes from disappearing silently.
- `must_exclude` prevents known hardening patterns or scope differences from becoming
  false positives.

The initial corpus covers:

- vague normative language;
- undefined dependency failure behavior;
- explicit fail-closed behavior;
- direct-only prohibition gaps;
- direct-and-indirect closure;
- delegation laundering across separate rules;
- scope-preserving effect normalization;
- swallowed exceptions;
- broad exception handling.

## Corpus governance

When a detector produces a confirmed false positive or false negative:

1. reduce it to the smallest source fixture that still reproduces the behavior;
2. add that fixture to the corpus before or with the fix;
3. state the required category presence/absence;
4. keep source wording stable unless the case itself is intentionally superseded.

Future semantic/model-assisted benchmarks must be stored separately from deterministic
cases so nondeterministic interpretation does not masquerade as deterministic regression
evidence.
