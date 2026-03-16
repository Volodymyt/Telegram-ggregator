"""Tests for the planning item lookup helper."""

from __future__ import annotations

import json
import subprocess
import textwrap
from pathlib import Path

import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "bin" / "find-planning-item"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


@pytest.fixture
def planning_repo(tmp_path: Path) -> Path:
    write_file(
        tmp_path / "docs/planning/active/README.md",
        """
        # Active Plans

        ```md
        Planning ID: 0001
        Status: Ready
        ```
        """,
    )
    write_file(
        tmp_path / "docs/planning/active/01_0001_foundations_ready/0001_foundations_ready.md",
        """
        # M0 Foundations Ready

        Planning ID: 0001
        Milestone: M0
        Status: Ready
        Last updated: 2026-03-16
        """,
    )
    write_file(
        tmp_path
        / "docs/planning/active/01_0001_foundations_ready/02_0007_config_login_contract/0007_config_login_contract.md",
        """
        # M0 Config and login contract

        Planning ID: 0007
        Status: Ready
        Last updated: 2026-03-16
        """,
    )
    write_file(
        tmp_path
        / "docs/planning/active/01_0001_foundations_ready/02_0007_config_login_contract/tasks/02_0009_yaml_contract_models.md",
        """
        # M0 Config and login contract: YAML contract models and file loading

        Planning ID: 0009
        Status: Ready
        Last updated: 2026-03-16
        """,
    )
    write_file(
        tmp_path / "docs/planning/archive/01_0101_archived_epic/0101_archived_epic.md",
        """
        # Archived Epic

        Planning ID: 0101
        Milestone: M0
        Status: Ready
        Last updated: 2026-03-16
        """,
    )
    write_file(
        tmp_path
        / "docs/planning/archive/01_0101_archived_epic/02_0102_archived_story/0102_archived_story.md",
        """
        # Archived Story

        Planning ID: 0102
        Status: Done
        Last updated: 2026-03-16
        """,
    )
    write_file(
        tmp_path / "docs/planning/backlog.md",
        """
        # Backlog

        - [Draft] Placeholder item without Planning ID
        """,
    )
    return tmp_path


def run_lookup(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(SCRIPT_PATH),
            "--repo-root",
            str(repo_root),
            *args,
        ],
        capture_output=True,
        check=False,
        text=True,
    )


def test_lookup_returns_json_for_task(planning_repo: Path) -> None:
    result = run_lookup(planning_repo, "--json", "9")

    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    assert payload["planning_id"] == "0009"
    assert payload["kind"] == "task"
    assert payload["location"] == "active"
    assert payload["status"] == "Ready"
    assert payload["path"].endswith("02_0009_yaml_contract_models.md")
    assert payload["parents"]["story"]["planning_id"] == "0007"
    assert payload["parents"]["epic"]["planning_id"] == "0001"


def test_lookup_returns_human_output(planning_repo: Path) -> None:
    result = run_lookup(planning_repo, "0102")

    assert result.returncode == 0, result.stderr
    assert "Planning ID: 0102" in result.stdout
    assert "Location: archive" in result.stdout
    assert "Kind: story" in result.stdout


def test_lookup_fails_when_item_is_missing(planning_repo: Path) -> None:
    result = run_lookup(planning_repo, "0099")

    assert result.returncode == 1
    assert "was not found" in result.stderr


def test_lookup_fails_for_duplicate_planning_id(planning_repo: Path) -> None:
    write_file(
        planning_repo / "docs/planning/archive/02_0009_duplicate_story/0009_duplicate_story.md",
        """
        # Duplicate Story

        Planning ID: 0009
        Status: Done
        Last updated: 2026-03-16
        """,
    )

    result = run_lookup(planning_repo, "0009")

    assert result.returncode == 1
    assert "duplicated across" in result.stderr


def test_lookup_fails_for_malformed_metadata(planning_repo: Path) -> None:
    write_file(
        planning_repo
        / "docs/planning/active/01_0001_foundations_ready/03_0012_storage_foundation/0012_storage_foundation.md",
        """
        # Broken Story

        Planning ID: 0012
        Last updated: 2026-03-16
        """,
    )

    result = run_lookup(planning_repo, "0012")

    assert result.returncode == 1
    assert "Missing status" in result.stderr


def test_lookup_ignores_non_canonical_template_files(planning_repo: Path) -> None:
    result = run_lookup(planning_repo, "--json", "0001")

    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout)
    assert payload["kind"] == "epic"
    assert payload["path"] == "docs/planning/active/01_0001_foundations_ready/0001_foundations_ready.md"
