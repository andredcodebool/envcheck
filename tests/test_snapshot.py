"""Tests for envcheck.snapshot."""
import json
from pathlib import Path

import pytest

from envcheck.snapshot import (
    SnapshotError,
    load_snapshot,
    list_snapshots,
    save_snapshot,
    latest_snapshot_path,
)

ENV_A = {"APP_HOST": "localhost", "APP_PORT": "8080"}
ENV_B = {"APP_HOST": "prod.example.com", "APP_PORT": "443", "APP_DEBUG": "false"}


def test_save_creates_file(tmp_path):
    p = save_snapshot(ENV_A, "web", snapshot_dir=str(tmp_path))
    assert p.exists()
    assert p.suffix == ".json"


def test_save_content_roundtrip(tmp_path):
    p = save_snapshot(ENV_A, "web", snapshot_dir=str(tmp_path))
    data = json.loads(p.read_text())
    assert data == ENV_A


def test_list_snapshots_empty(tmp_path):
    assert list_snapshots("nonexistent", snapshot_dir=str(tmp_path)) == []


def test_list_snapshots_ordered(tmp_path):
    save_snapshot(ENV_A, "svc", snapshot_dir=str(tmp_path))
    save_snapshot(ENV_B, "svc", snapshot_dir=str(tmp_path))
    snaps = list_snapshots("svc", snapshot_dir=str(tmp_path))
    assert len(snaps) == 2
    assert snaps[0] < snaps[1]


def test_load_snapshot_latest(tmp_path):
    save_snapshot(ENV_A, "svc", snapshot_dir=str(tmp_path))
    save_snapshot(ENV_B, "svc", snapshot_dir=str(tmp_path))
    loaded = load_snapshot("svc", snapshot_dir=str(tmp_path))
    assert loaded == ENV_B


def test_load_snapshot_by_index(tmp_path):
    save_snapshot(ENV_A, "svc", snapshot_dir=str(tmp_path))
    save_snapshot(ENV_B, "svc", snapshot_dir=str(tmp_path))
    loaded = load_snapshot("svc", snapshot_dir=str(tmp_path), index=0)
    assert loaded == ENV_A


def test_load_snapshot_missing_raises(tmp_path):
    with pytest.raises(SnapshotError, match="No snapshots"):
        load_snapshot("ghost", snapshot_dir=str(tmp_path))


def test_latest_snapshot_path_none(tmp_path):
    assert latest_snapshot_path("ghost", snapshot_dir=str(tmp_path)) is None


def test_latest_snapshot_path_returns_path(tmp_path):
    save_snapshot(ENV_A, "svc", snapshot_dir=str(tmp_path))
    p = latest_snapshot_path("svc", snapshot_dir=str(tmp_path))
    assert p is not None and p.exists()
