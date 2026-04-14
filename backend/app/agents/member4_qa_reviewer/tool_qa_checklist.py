from typing import List


def generate_qa_checklist(issue_text: str) -> List[str]:
    """
    Generate a basic QA checklist for validating a proposed fix.

    Args:
        issue_text: Original issue description.

    Returns:
        A list of QA validation steps.
    """
    return [
        "Verify the original issue can be reproduced before the fix.",
        "Apply the proposed fix and verify the original issue no longer occurs.",
        "Test related user flow for regressions.",
        "Test edge cases and invalid inputs.",
        f"Confirm expected behavior matches the issue context: {issue_text[:120]}",
    ]