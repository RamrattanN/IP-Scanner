from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_recovery_documentation_set_is_complete_and_linked():
    expected = {
        "README.md",
        "Current-Baseline.md",
        "Recovery-Baseline.md",
        "Discovery-Confidence.md",
        "UX-Guidelines.md",
        "KANBAN.md",
        "ROADMAP.md",
    }
    docs = ROOT / "docs"
    assert expected <= {path.name for path in docs.glob("*.md")}

    index = (docs / "README.md").read_text(encoding="utf-8")
    for name in expected - {"README.md"}:
        assert f"]({name})" in index


def test_current_baseline_distinguishes_available_and_planned_work():
    baseline = (ROOT / "docs" / "Current-Baseline.md").read_text(encoding="utf-8")
    kanban = (ROOT / "docs" / "KANBAN.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")

    assert "Inventory Baseline Candidate 2026.09.21" in baseline
    assert "7b1602dfc4123e5159e54e3b6a7347f7741e8d2e" in baseline
    assert "not a production release" in baseline
    assert "device inventory" in baseline
    assert "## In Progress" in kanban
    assert "## In Review" in kanban
    assert "## Ready" in kanban
    assert "## Done" in kanban
    assert "## Blocked" in kanban
    assert "2025-09-19" in roadmap
    assert "2026-09-21" in roadmap
    assert "Persistent inventory implementation" in roadmap
