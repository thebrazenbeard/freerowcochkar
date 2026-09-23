"""FreeRowCochkar: literal-compliance and loophole auditing."""

from .analyzer import Analyzer, analyze
from .constraints import AdversarialPath, ConstraintGraph, Modality, Relation, Rule
from .models import AnalysisReport, Finding, Severity
from .rules import extract_rules

__all__ = [
    "AdversarialPath",
    "Analyzer",
    "AnalysisReport",
    "ConstraintGraph",
    "Finding",
    "Modality",
    "Relation",
    "Rule",
    "Severity",
    "analyze",
    "extract_rules",
]
__version__ = "0.1.0"
