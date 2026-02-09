import json

import pytest

from parser_site import cli


def test_cli_only_flag_filters_output(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "parser_site.cli",
            "mail a@example.com and https://example.com and +1 202 555 0182",
            "--only",
            "emails",
            "--only",
            "phones",
        ],
    )

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "emails": ["a@example.com"],
        "phones": ["+12025550182"],
    }


def test_cli_reads_file_input(tmp_path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("team@example.com", encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["parser_site.cli", "--file", str(input_file)])

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 0
    assert json.loads(captured.out) == {
        "emails": ["team@example.com"],
        "urls": [],
        "phones": [],
    }


def test_cli_rejects_missing_file(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["parser_site.cli", "--file", "missing.txt"])

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Input file not found" in captured.err


def test_cli_rejects_empty_input(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr("sys.argv", ["parser_site.cli", "   "])

    exit_code = cli.main()
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Input text is empty" in captured.err


def test_cli_rejects_conflicting_text_and_file(tmp_path, capsys: pytest.CaptureFixture[str]) -> None:
    input_file = tmp_path / "input.txt"
    input_file.write_text("ignored@example.com", encoding="utf-8")

    exit_code = cli.main(["inline text", "--file", str(input_file)])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "Use either positional text or --file, not both" in captured.err
