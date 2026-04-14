"""Sanity: Alembic is wired and has a single head (no DB required)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_alembic_single_head() -> None:
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "heads"],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert r.returncode == 0, r.stderr
    lines = [ln.strip() for ln in r.stdout.strip().splitlines() if ln.strip()]
    assert len(lines) == 1, f"expected single head, got: {lines!r}"
    assert "20250409120000" in lines[0]
