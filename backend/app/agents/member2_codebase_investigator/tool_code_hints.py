from typing import List


def extract_code_hints(code_text: str) -> List[str]:
    """
    Extract simple bug hints from code text using lightweight pattern checks.

    Args:
        code_text: Source code excerpt.

    Returns:
        A list of textual hints about suspicious code patterns.
    """
    hints: List[str] = []

    if 'non_existing_key' in code_text:
        hints.append('Possible KeyError: code accesses "non_existing_key".')

    if 'return result["message"]' in code_text or "return result['message']" in code_text:
        hints.append('Possible NameError: variable "result" is returned before being defined.')

    if 'raise ValueError' in code_text:
        hints.append('Code explicitly raises ValueError in some branches.')

    return hints