"""Export environment check results to various formats (JSON, CSV)."""
from __future__ import annotations

import csv
import io
import json
from typing import List

from envcheck.checker import CheckResult


def result_to_dict(result: CheckResult) -> dict:
    """Convert a CheckResult to a plain dictionary."""
    return {
        "ok": result.ok,
        "missing": sorted(result.missing),
        "extra": sorted(result.extra),
        "total_required": result.total_required,
        "total_present": result.total_present,
    }


def export_json(results: List[CheckResult], labels: List[str] | None = None) -> str:
    """Serialize a list of CheckResults to a JSON string."""
    labels = labels or [f"env_{i}" for i in range(len(results))]
    payload = [
        {"label": label, **result_to_dict(r)}
        for label, r in zip(labels, results)
    ]
    return json.dumps(payload, indent=2)


def export_csv(results: List[CheckResult], labels: List[str] | None = None) -> str:
    """Serialize a list of CheckResults to a CSV string."""
    labels = labels or [f"env_{i}" for i in range(len(results))]
    buf = io.StringIO()
    fieldnames = ["label", "ok", "missing", "extra", "total_required", "total_present"]
    writer = csv.DictWriter(buf, fieldnames=fieldnames)
    writer.writeheader()
    for label, r in zip(labels, results):
        d = result_to_dict(r)
        writer.writerow({
            "label": label,
            "ok": d["ok"],
            "missing": ";".join(d["missing"]),
            "extra": ";".join(d["extra"]),
            "total_required": d["total_required"],
            "total_present": d["total_present"],
        })
    return buf.getvalue()
