from typing import Dict


def parse_bug_report(report_text: str) -> Dict[str, str]:
    """
    Parse a raw bug report into a basic structured dictionary.

    Args:
        report_text: Raw user-provided bug report.

    Returns:
        A structured dictionary with extracted bug report fields.
    """
    text = report_text.strip()

    severity = "medium"
    lowered = text.lower()

    if any(word in lowered for word in ["crash", "data loss", "security", "fatal"]):
        severity = "high"
    elif any(word in lowered for word in ["minor", "typo", "alignment", "ui issue"]):
        severity = "low"

    return {
        "original_report": text,
        "severity": severity,
        "suspected_module": "unknown",
        "issue_type": "bug_report",
    }