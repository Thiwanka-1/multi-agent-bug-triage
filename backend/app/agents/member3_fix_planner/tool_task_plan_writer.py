from typing import List


def build_fix_steps(relevant_files: List[str]) -> List[str]:
    """
    Build a basic ordered fix plan using the list of relevant files.

    Args:
        relevant_files: Files suspected to be related to the issue.

    Returns:
        A list of ordered fix steps.
    """
    steps = ["Reproduce the issue locally and confirm the failure conditions."]

    for idx, file in enumerate(relevant_files, start=1):
        steps.append(f"Inspect and update file {idx}: {file}")

    steps.append("Run regression checks after implementing the fix.")
    return steps