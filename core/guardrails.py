import re
from typing import Tuple

# ------------------------------------------------------------------
# Input guard — prompt injection keywords
# ------------------------------------------------------------------

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    # Chinese
    re.compile(r"忽略(?:上述|以上|前面).*", re.IGNORECASE),
    re.compile(r"忘记.*(?:你是|身份|角色)", re.IGNORECASE),
    re.compile(r"你是(?:什么|谁|哪个).*模型", re.IGNORECASE),
    re.compile(r"请(?:忽略|无视|忘记).*", re.IGNORECASE),
    # English
    re.compile(r"ignore\s+(?:all\s+)?(?:above|previous|prior)", re.IGNORECASE),
    re.compile(r"forget\s+(?:you\s+are|your\s+role|your\s+identity)", re.IGNORECASE),
    re.compile(r"(?:you\s+are|you're)\s+(?:a\s+)?(?:large\s+)?language\s+model", re.IGNORECASE),
    re.compile(r"system\s*(?:prompt|message|instruction)", re.IGNORECASE),
    re.compile(r"(?:new\s+)?instruction[s]?\s*:", re.IGNORECASE),
    # Role / persona hijacking
    re.compile(r"act\s+as\s+if\s+you\s+are", re.IGNORECASE),
    re.compile(r"pretend\s+(?:you\s+are|to\s+be)", re.IGNORECASE),
]


def input_guard(text: str) -> Tuple[str, bool]:
    """Detect and neutralise prompt-injection attempts.

    Scans *text* for known injection keywords (Chinese and English).
    When a match is found the offending portion is stripped from the
    returned string and the second element of the tuple is set to
    ``True``.

    Args:
        text: The raw user input.

    Returns:
        A ``(cleaned_text, flagged)`` pair.  *cleaned_text* has the
        matched portion removed; *flagged* is ``True`` if any
        injection pattern matched.
    """
    if not text:
        return text, False

    original = text
    flagged = False

    for pattern in _INJECTION_PATTERNS:
        match = pattern.search(text)
        if match:
            flagged = True
            # Remove the matched portion from the text
            text = pattern.sub("", text).strip()

    # Collapse repeated whitespace left after removal
    cleaned = re.sub(r"\s+", " ", text).strip()

    return cleaned, flagged


# ------------------------------------------------------------------
# Output guard — redaction patterns
# ------------------------------------------------------------------

_REDACT_PATTERNS: list[re.Pattern[str]] = [
    # IPv4 addresses
    re.compile(
        r"\b(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}"
        r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\b",
    ),
    # Basic IPv6 addresses (simplified — one or two colons)
    re.compile(
        r"\b(?:[0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}\b",
    ),
    # SQL fragments — common DML / DDL keywords followed by content
    re.compile(
        r"(?i)\b(SELECT\s+.+?\s+FROM|INSERT\s+INTO|UPDATE\s+.+?\s+SET|"
        r"DELETE\s+FROM|DROP\s+(?:TABLE|DATABASE|INDEX)|"
        r"ALTER\s+(?:TABLE|DATABASE)|CREATE\s+(?:TABLE|DATABASE|INDEX)|"
        r"TRUNCATE\s+(?:TABLE|DATABASE))\b.*?(?:;|$)",
    ),
    # Email addresses
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    # Phone numbers (simple international pattern)
    re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
    # Port numbers commonly used in URLs / config
    re.compile(r":(\d{4,5})\b"),
]


def output_guard(text: str) -> str:
    """Redact sensitive patterns from the generated output.

    The following are replaced with ``[REDACTED]``:

    * IPv4 and IPv6 addresses
    * SQL statements (SELECT, INSERT, UPDATE, DELETE, DROP, …)
    * Email addresses
    * Phone numbers
    * Port numbers (4-5 digits)

    Args:
        text: The raw LLM output.

    Returns:
        The output with all matched patterns replaced by
        ``[REDACTED]``.
    """
    if not text:
        return text

    result = text
    for pattern in _REDACT_PATTERNS:
        result = pattern.sub("[REDACTED]", result)

    return result
