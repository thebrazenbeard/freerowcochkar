"""FreeRowCochkar: literal-compliance and loophole auditing."""

from .analyzer import Analyzer, analyze
from .models import AnalysisReport, Finding, Severity

__all__ = ["Analyzer", "AnalysisReport", "Finding", "Severity", "analyze"]
__version__ = "0.1.0"
