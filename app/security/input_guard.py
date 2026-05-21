import re
import logging

logger = logging.getLogger(__name__)

# Patterns that indicate prompt injection attempts
_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"ignore\s+above",
    r"disregard\s+(all\s+)?(previous|above)",
    r"you\s+are\s+now\s+(?:a|an)\s+(?!customer|client|user)",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"\[\s*INST\s*\]",
    r"pretend\s+you\s+are\s+(?!looking|shopping|browsing)",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def check_input(message: str) -> bool:
    """Returns True if the message appears safe, False if it looks like injection."""
    for pattern in _COMPILED:
        if pattern.search(message):
            logger.warning(f"Input guard triggered: pattern={pattern.pattern}")
            return False
    return True
