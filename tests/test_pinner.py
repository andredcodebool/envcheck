"""Tests for envcheck.pinner."""
from __future__ import annotations

import json
import pytest
from pathlib import Path

from envcheck.pinner import (
    PinError,
    PinReport,
    compare_pin,
    format_pin_report,
    list_pins,
    load_pin,
    save_pin,
)


@pytest.fixture()
def pin_dir(tmp_path: Path) -> Path:
    return tmp_path / "pins"


ENV = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}


def test_save_creates_file(pin_dir: Path) -> None:
    path = save_pin(ENV, "base", pin_dir)
    assert path.exists()
    assert path.name == "base.pin.json"


def test_save_content_roundtrip(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    loaded = load_pin("base", pin_dir)
    assert loaded == ENV


def test_load_missing_raises(pin_dir: Path) -> None:
    with pytest.raises(PinError, match="not found"):
        load_pin("ghost", pin_dir)


def test_load_corrupt_raises(pin_dir: Path) -> None:
    pin_dir.mkdir(parents=True)
    (pin_dir / "bad.pin.json").write_text("not json", encoding="utf-8")
    with pytest.raises(PinError, match="Corrupt"):
        load_pin("bad", pin_dir)


def test_list_pins_empty(pin_dir: Path) -> None:
    assert list_pins(pin_dir) == []


def test_list_pins_sorted(pin_dir: Path) -> None:
    for name in ("prod", "staging", "dev"):
        save_pin(ENV, name, pin_dir)
    assert list_pins(pin_dir) == ["dev", "prod", "staging"]


def test_compare_pin_clean(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    report = compare_pin(ENV, "base", pin_dir)
    assert report.clean is True
    assert report.drifted == []
    assert report.new_keys == []
    assert report.removed_keys == []


def test_compare_pin_changed_value(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    updated = {**ENV, "PORT": "9999"}
    report = compare_pin(updated, "base", pin_dir)
    assert report.clean is False
    assert "PORT" in report.drifted


def test_compare_pin_new_key(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    updated = {**ENV, "NEW_VAR": "hello"}
    report = compare_pin(updated, "base", pin_dir)
    assert "NEW_VAR" in report.new_keys


def test_compare_pin_removed_key(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    reduced = {k: v for k, v in ENV.items() if k != "DEBUG"}
    report = compare_pin(reduced, "base", pin_dir)
    assert "DEBUG" in report.removed_keys


def test_format_pin_report_clean(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    report = compare_pin(ENV, "base", pin_dir)
    text = format_pin_report(report)
    assert "No drift" in text


def test_format_pin_report_shows_sections(pin_dir: Path) -> None:
    save_pin(ENV, "base", pin_dir)
    updated = {**ENV, "PORT": "9999", "EXTRA": "1"}
    report = compare_pin(updated, "base", pin_dir)
    text = format_pin_report(report)
    assert "Changed" in text
    assert "PORT" in text
    assert "New keys" in text
    assert "EXTRA" in text
