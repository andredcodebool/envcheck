"""CLI sub-commands for audit log inspection."""
from __future__ import annotations

from pathlib import Path

import click

from envcheck.audit import DEFAULT_AUDIT_DIR, list_entries


@click.group("audit")
def audit_group():
    """Inspect past envcheck audit records."""


@audit_group.command("list")
@click.option(
    "--dir",
    "audit_dir",
    default=str(DEFAULT_AUDIT_DIR),
    show_default=True,
    help="Directory containing audit records.",
)
@click.option("--profile", default=None, help="Filter by profile name.")
@click.option("--failed", is_flag=True, default=False, help="Show only failed runs.")
def list_cmd(audit_dir: str, profile: str | None, failed: bool):
    """List recorded audit entries."""
    entries = list_entries(audit_dir=Path(audit_dir))
    if profile:
        entries = [e for e in entries if e.profile == profile]
    if failed:
        entries = [e for e in entries if not e.passed]
    if not entries:
        click.echo("No audit entries found.")
        return
    for e in entries:
        status = click.style("PASS", fg="green") if e.passed else click.style("FAIL", fg="red")
        missing_info = f"  missing={e.missing}" if e.missing else ""
        click.echo(f"[{e.timestamp}] {e.profile:20s} {status}{missing_info}")


@audit_group.command("clear")
@click.option(
    "--dir",
    "audit_dir",
    default=str(DEFAULT_AUDIT_DIR),
    show_default=True,
)
@click.confirmation_option(prompt="Delete all audit records?")
def clear_cmd(audit_dir: str):
    """Remove all audit records."""
    d = Path(audit_dir)
    removed = 0
    if d.exists():
        for f in d.glob("*.json"):
            f.unlink()
            removed += 1
    click.echo(f"Removed {removed} audit record(s).")
