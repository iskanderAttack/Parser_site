import random
import string
import time

from parser_site.parser import parse_contacts


def test_parse_contacts_extracts_emails_urls_and_phones() -> None:
    text = """
    Пишите на Alpha@example.com и beta@example.com.
    Документация: https://docs.example.com, зеркало: http://mirror.example.com/path.
    Телефоны: +7 (999) 123-45-67, 8 999 123 45 67
    """
    result = parse_contacts(text)

    assert result.emails == ["alpha@example.com", "beta@example.com"]
    assert result.urls == ["https://docs.example.com", "http://mirror.example.com/path"]
    assert result.phones == ["+79991234567", "89991234567"]


def test_parse_contacts_removes_duplicates_preserving_order() -> None:
    text = (
        "repeat@example.com REPEAT@example.com "
        "https://site.com, https://site.com "
        "+1-202-555-0182 +1 (202) 555-0182"
    )
    result = parse_contacts(text)

    assert result.emails == ["repeat@example.com"]
    assert result.urls == ["https://site.com"]
    assert result.phones == ["+12025550182"]


def test_parse_contacts_ignores_short_number_like_fragments() -> None:
    text = "IDs: 12345, 6789 and normal phone +49 170 1234567"
    result = parse_contacts(text)

    assert result.phones == ["+491701234567"]


def test_parse_contacts_strips_trailing_punctuation_from_urls_and_email() -> None:
    text = "Contact: Demo@Example.com), visit https://example.com/docs)."
    result = parse_contacts(text)

    assert result.emails == ["demo@example.com"]
    assert result.urls == ["https://example.com/docs"]


def test_parse_contacts_handles_urls_with_query_and_brackets() -> None:
    text = "Useful link (https://example.com/path?q=1&v=test), another: https://x.io/a(b)c)."
    result = parse_contacts(text)

    assert result.urls == ["https://example.com/path?q=1&v=test", "https://x.io/a(b)c"]


def test_parse_contacts_supports_plus_tag_email_and_noisy_text() -> None:
    text = "### Reach me at Name.Surname+alerts@Example.co.uk!!! random ~~symbols~~ and words"
    result = parse_contacts(text)

    assert result.emails == ["name.surname+alerts@example.co.uk"]


def test_parse_contacts_fuzz_does_not_crash_and_returns_normalized_shapes() -> None:
    rng = random.Random(42)
    alphabet = string.ascii_letters + string.digits + " _-+@:/().,!?#"

    for _ in range(150):
        length = rng.randint(0, 300)
        noise = "".join(rng.choice(alphabet) for _ in range(length))
        text = f"{noise} test@example.com https://example.com +1 (202) 555-0182"

        result = parse_contacts(text)

        assert "test@example.com" in result.emails
        assert "https://example.com" in result.urls
        assert "+12025550182" in result.phones
        assert all(email == email.lower() for email in result.emails)
        assert all(url == url.rstrip('.,;:!?)]}\\"\'') for url in result.urls)


def test_parse_contacts_large_input_performance_smoke() -> None:
    chunk = "Contact a@example.com https://example.com/path +1 (202) 555-0182 noise text. "
    large_text = chunk * 12000

    start = time.perf_counter()
    result = parse_contacts(large_text)
    elapsed = time.perf_counter() - start

    assert result.emails == ["a@example.com"]
    assert result.urls == ["https://example.com/path"]
    assert result.phones == ["+12025550182"]
    assert elapsed < 5.0


def test_parse_contacts_handles_multiple_phone_locales_and_extensions() -> None:
    text = (
        "UK: 0044 20 7946 0958, "
        "DE: +49 (30) 1234-567 ext. 89, "
        "RU: +7 (495) 123-45-67 доб. 12"
    )
    result = parse_contacts(text)

    assert result.phones == ["+442079460958", "+49301234567", "+74951234567"]


def test_parse_contacts_filters_too_long_digit_sequences() -> None:
    text = "noise 12345678901234567890 and valid +33 1 42 68 53 00"
    result = parse_contacts(text)

    assert result.phones == ["+33142685300"]
