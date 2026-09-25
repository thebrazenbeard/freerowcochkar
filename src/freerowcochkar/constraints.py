from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class Modality(str, Enum):
    PERMIT = "permit"
    PROHIBIT = "prohibit"
    REQUIRE = "require"
    UNKNOWN = "unknown"


class Relation(str, Enum):
    PERMITS = "permits"
    PROHIBITS = "prohibits"
    REQUIRES = "requires"
    DELEGATES = "delegates"
    EXCEPTS = "excepts"
    PRECEDES = "precedes"
    FALLBACK = "fallback"


@dataclass(frozen=True)
class SourceSpan:
    line_start: int
    line_end: int
    text: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    modality: Modality
    subject: str
    action: str
    object: str
    effect_key: str
    source: SourceSpan
    condition: str | None = None
    exception: str | None = None
    indirect: bool = False
    delegated_actor: str | None = None
    confidence: float = 0.5


@dataclass(frozen=True)
class StateTransition:
    transition_id: str
    modality: Modality
    subject: str
    resource: str
    from_state: str
    to_state: str
    source: SourceSpan
    confidence: float = 0.85


@dataclass(frozen=True)
class ForbiddenState:
    state_id: str
    resource: str
    state: str
    source: SourceSpan
    confidence: float = 0.9


@dataclass(frozen=True)
class ConstraintEdge:
    source: str
    target: str
    relation: Relation
    rule_id: str
    span: SourceSpan
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class AdversarialPath:
    path_id: str
    category: str
    target_effect: str
    rule_ids: tuple[str, ...]
    spans: tuple[SourceSpan, ...]
    explanation: str
    hardening: str
    confidence: float


@dataclass
class ConstraintGraph:
    nodes: set[str] = field(default_factory=set)
    edges: list[ConstraintEdge] = field(default_factory=list)
    rules: list[Rule] = field(default_factory=list)
    transitions: list[StateTransition] = field(default_factory=list)
    forbidden_states: list[ForbiddenState] = field(default_factory=list)

    @classmethod
    def from_rules(
        cls,
        rules: Iterable[Rule],
        *,
        transitions: Iterable[StateTransition] = (),
        forbidden_states: Iterable[ForbiddenState] = (),
    ) -> "ConstraintGraph":
        graph = cls()
        for rule in rules:
            graph.add_rule(rule)
        for transition in transitions:
            graph.add_transition(transition)
        for forbidden in forbidden_states:
            graph.add_forbidden_state(forbidden)
        return graph

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        subject = f"actor:{rule.subject}"
        effect = f"effect:{rule.effect_key}"
        self.nodes.update((subject, effect))

        relation = {
            Modality.PERMIT: Relation.PERMITS,
            Modality.PROHIBIT: Relation.PROHIBITS,
            Modality.REQUIRE: Relation.REQUIRES,
            Modality.UNKNOWN: Relation.REQUIRES,
        }[rule.modality]
        self.edges.append(
            ConstraintEdge(
                source=subject,
                target=effect,
                relation=relation,
                rule_id=rule.rule_id,
                span=rule.source,
            )
        )

        if rule.indirect:
            route = f"route:delegate:{rule.rule_id}"
            self.nodes.add(route)
            self.edges.append(
                ConstraintEdge(
                    source=subject,
                    target=route,
                    relation=Relation.DELEGATES,
                    rule_id=rule.rule_id,
                    span=rule.source,
                    metadata={"delegated_actor": rule.delegated_actor or "unspecified"},
                )
            )
            self.edges.append(
                ConstraintEdge(
                    source=route,
                    target=effect,
                    relation=relation,
                    rule_id=rule.rule_id,
                    span=rule.source,
                )
            )

    def add_transition(self, transition: StateTransition) -> None:
        self.transitions.append(transition)
        source = f"state:{transition.resource}:{transition.from_state}"
        target = f"state:{transition.resource}:{transition.to_state}"
        self.nodes.update((source, target))
        relation = (
            Relation.PERMITS
            if transition.modality == Modality.PERMIT
            else Relation.PROHIBITS
        )
        self.edges.append(
            ConstraintEdge(
                source=source,
                target=target,
                relation=relation,
                rule_id=transition.transition_id,
                span=transition.source,
                metadata={"subject": transition.subject},
            )
        )

    def add_forbidden_state(self, forbidden: ForbiddenState) -> None:
        self.forbidden_states.append(forbidden)
        self.nodes.add(f"state:{forbidden.resource}:{forbidden.state}")

    def to_dict(self) -> dict[str, object]:
        return {
            "nodes": sorted(self.nodes),
            "rules": [
                {
                    "rule_id": rule.rule_id,
                    "modality": rule.modality.value,
                    "subject": rule.subject,
                    "action": rule.action,
                    "object": rule.object,
                    "effect_key": rule.effect_key,
                    "condition": rule.condition,
                    "exception": rule.exception,
                    "indirect": rule.indirect,
                    "delegated_actor": rule.delegated_actor,
                    "confidence": rule.confidence,
                    "source": {
                        "line_start": rule.source.line_start,
                        "line_end": rule.source.line_end,
                        "text": rule.source.text,
                    },
                }
                for rule in self.rules
            ],
            "transitions": [
                {
                    "transition_id": transition.transition_id,
                    "modality": transition.modality.value,
                    "subject": transition.subject,
                    "resource": transition.resource,
                    "from_state": transition.from_state,
                    "to_state": transition.to_state,
                    "confidence": transition.confidence,
                    "source": {
                        "line_start": transition.source.line_start,
                        "line_end": transition.source.line_end,
                        "text": transition.source.text,
                    },
                }
                for transition in self.transitions
            ],
            "forbidden_states": [
                {
                    "state_id": forbidden.state_id,
                    "resource": forbidden.resource,
                    "state": forbidden.state,
                    "confidence": forbidden.confidence,
                    "source": {
                        "line_start": forbidden.source.line_start,
                        "line_end": forbidden.source.line_end,
                        "text": forbidden.source.text,
                    },
                }
                for forbidden in self.forbidden_states
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "relation": edge.relation.value,
                    "rule_id": edge.rule_id,
                    "metadata": edge.metadata,
                    "span": {
                        "line_start": edge.span.line_start,
                        "line_end": edge.span.line_end,
                        "text": edge.span.text,
                    },
                }
                for edge in self.edges
            ],
            "paths": [
                {
                    "path_id": path.path_id,
                    "category": path.category,
                    "target_effect": path.target_effect,
                    "rule_ids": list(path.rule_ids),
                    "confidence": path.confidence,
                    "explanation": path.explanation,
                    "hardening": path.hardening,
                    "spans": [
                        {
                            "line_start": span.line_start,
                            "line_end": span.line_end,
                            "text": span.text,
                        }
                        for span in path.spans
                    ],
                }
                for path in self.search_literal_compliance_paths()
            ],
        }

    def search_literal_compliance_paths(
        self,
        *,
        max_transition_depth: int = 8,
    ) -> list[AdversarialPath]:
        paths: list[AdversarialPath] = []
        prohibited = [r for r in self.rules if r.modality == Modality.PROHIBIT]
        permissive = [r for r in self.rules if r.modality == Modality.PERMIT]

        for ban in prohibited:
            for allow in permissive:
                if ban.effect_key != allow.effect_key:
                    continue

                if allow.indirect and not ban.indirect:
                    paths.append(
                        AdversarialPath(
                            path_id="FRC-PATH-DELEGATE",
                            category="delegation_laundering",
                            target_effect=ban.effect_key,
                            rule_ids=(ban.rule_id, allow.rule_id),
                            spans=(ban.source, allow.source),
                            explanation=(
                                "The direct effect is prohibited, but a separate rule permits an "
                                "indirect or delegated route to the same normalized effect."
                            ),
                            hardening=(
                                "Bind the prohibition to the outcome: cover direct action, delegation, "
                                "authorization, requests, caused effects, and equivalent intermediated routes."
                            ),
                            confidence=min(ban.confidence, allow.confidence, 0.9),
                        )
                    )
                elif ban.subject == allow.subject:
                    paths.append(
                        AdversarialPath(
                            path_id="FRC-PATH-CONFLICT",
                            category="literal_permission_conflict",
                            target_effect=ban.effect_key,
                            rule_ids=(ban.rule_id, allow.rule_id),
                            spans=(ban.source, allow.source),
                            explanation=(
                                "The same actor is both prohibited and permitted to produce the same "
                                "normalized effect, with no graph-level precedence rule."
                            ),
                            hardening=(
                                "Add explicit precedence or narrow the permission with conditions that "
                                "cannot be read as superseding the prohibition."
                            ),
                            confidence=min(ban.confidence, allow.confidence, 0.92),
                        )
                    )
        paths.extend(
            self._search_state_compositions(max_transition_depth=max_transition_depth)
        )
        return _dedupe_paths(paths)

    def _search_state_compositions(
        self,
        *,
        max_transition_depth: int,
    ) -> list[AdversarialPath]:
        if max_transition_depth < 3:
            return []

        blocked = {
            (t.subject, t.resource, t.from_state, t.to_state)
            for t in self.transitions
            if t.modality == Modality.PROHIBIT
        }
        permitted = [
            t
            for t in self.transitions
            if t.modality == Modality.PERMIT
            and (t.subject, t.resource, t.from_state, t.to_state) not in blocked
        ]

        adjacency: dict[tuple[str, str], list[StateTransition]] = {}
        for transition in permitted:
            adjacency.setdefault(
                (transition.resource, transition.from_state), []
            ).append(transition)

        forbidden_by_state: dict[tuple[str, str], list[ForbiddenState]] = {}
        for forbidden in self.forbidden_states:
            forbidden_by_state.setdefault(
                (forbidden.resource, forbidden.state), []
            ).append(forbidden)

        paths: list[AdversarialPath] = []

        def walk(
            current: StateTransition,
            chain: tuple[StateTransition, ...],
            visited: frozenset[tuple[str, str]],
        ) -> None:
            target = (current.resource, current.to_state)
            if len(chain) >= 3:
                for forbidden in forbidden_by_state.get(target, ()):
                    paths.append(
                        AdversarialPath(
                            path_id="FRC-PATH-COMPOSE",
                            category="composition_gap",
                            target_effect=(
                                f"state:{forbidden.resource}:{forbidden.state}"
                            ),
                            rule_ids=tuple(
                                step.transition_id for step in chain
                            ) + (forbidden.state_id,),
                            spans=tuple(step.source for step in chain)
                            + (forbidden.source,),
                            explanation=(
                                "A sequence of at least three individually permitted "
                                "state transitions reaches a terminal state that is "
                                "explicitly prohibited."
                            ),
                            hardening=(
                                "Prohibit or gate at least one transition on this path, "
                                "then rerun analysis and require this exact composition "
                                "path to disappear."
                            ),
                            confidence=min(
                                forbidden.confidence,
                                *(step.confidence for step in chain),
                            ),
                        )
                    )

            if len(chain) >= max_transition_depth:
                return

            for nxt in adjacency.get(target, ()):
                next_target = (nxt.resource, nxt.to_state)
                if next_target in visited:
                    continue
                walk(
                    nxt,
                    chain + (nxt,),
                    visited | {next_target},
                )

        for transition in permitted:
            start = (transition.resource, transition.from_state)
            target = (transition.resource, transition.to_state)
            if target == start:
                continue
            walk(
                transition,
                (transition,),
                frozenset({start, target}),
            )

        return paths


def normalize_effect(action: str, obj: str) -> str:
    action = _normalize_words(action)
    obj = _normalize_words(obj)
    return f"{action}:{obj}".strip(":")


def _normalize_words(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9_ -]+", " ", value)
    value = re.sub(r"\b(the|a|an|their|its|your)\b", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _dedupe_paths(paths: list[AdversarialPath]) -> list[AdversarialPath]:
    seen: set[tuple[str, tuple[str, ...]]] = set()
    out: list[AdversarialPath] = []
    for path in paths:
        key = (path.category, path.rule_ids)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out
