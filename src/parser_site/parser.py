"""Core parsing utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(r"https?://[^\s,]+")
# International-friendly phone matcher with optional extension suffix.
# Examples: +7 (999) 123-45-67, 8 999 123 45 67, +1-202-555-0182,
# 0044 20 7946 0958, +49 (30) 1234-567 ext. 89
_PHONE_RE = re.compile(
    r"(?:\+|00)?\d[\d\s().-]{7,}\d(?:\s*(?:ext\.?|x|доб\.?|#)\s*\d{1,6})?",
    re.IGNORECASE,
)

_TRAILING_PUNCTUATION = ".,;:!?)]}\"'"
_EXTENSION_RE = re.compile(r"(?:\s*(?:ext\.?|x|доб\.?|#)\s*\d{1,6})$", re.IGNORECASE)


@dataclass(frozen=True)
class ParseResult:
    emails: list[str]
    urls: list[str]
    phones: list[str]


def _dedupe_keep_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _clean_url(url: str) -> str:
    return url.rstrip(_TRAILING_PUNCTUATION)


def _clean_email(email: str) -> str:
    return email.strip().lower().rstrip(_TRAILING_PUNCTUATION)


def _normalize_phone(phone: str) -> str:
    stripped = _EXTENSION_RE.sub("", phone.strip())
    has_plus = stripped.startswith("+")
    has_00_prefix = stripped.startswith("00")

    digits = re.sub(r"\D", "", stripped)
    if not digits:
        return ""

    if has_plus:
        return f"+{digits}"
    if has_00_prefix and len(digits) > 2:
        return f"+{digits[2:]}"
    return digits


def parse_contacts(text: str) -> ParseResult:
    """Extract emails, HTTP/HTTPS URLs and phone numbers from text."""
    raw_emails = [_clean_email(item) for item in _EMAIL_RE.findall(text)]
    raw_urls = [_clean_url(item) for item in _URL_RE.findall(text)]
    raw_phones = [_normalize_phone(item) for item in _PHONE_RE.findall(text)]

    emails = _dedupe_keep_order([item for item in raw_emails if item])
    urls = _dedupe_keep_order([item for item in raw_urls if item])

    # E.164 max length is 15 digits; min threshold prevents short-number noise.
    phones = _dedupe_keep_order(
        [item for item in raw_phones if 10 <= len(item.lstrip("+")) <= 15]
    )

    return ParseResult(emails=emails, urls=urls, phones=phones)
