"""FreeRowCochkar: literal-compliance and loophole auditing."""

from .analyzer import Analyzer, analyze
from .constraints import AdversarialPath, ConstraintGraph, ForbiddenState, Modality, Relation, Rule, StateTransition
from .models import AnalysisReport, Finding, Severity
from .rules import extract_rules, extract_state_model

__all__ = [
    "AdversarialPath",
    "Analyzer",
    "AnalysisReport",
    "ConstraintGraph",
    "ForbiddenState",
    "Finding",
    "Modality",
    "Relation",
    "Rule",
    "Severity",
    "StateTransition",
    "analyze",
    "extract_rules",
    "extract_state_model",
]
__version__ = "0.1.0"
