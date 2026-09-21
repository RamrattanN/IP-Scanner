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
        "Third-Party-Notices.md",
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

    assert "Discovery Experience Baseline 2026.09.21" in baseline
    assert "9cd37a98525acda67278d9902c6afcc28be638c4" in baseline
    assert "47d0bc66e7af4c979e5a3c281d70148ff5f7cddb" in baseline
    assert "Recovery Baseline 2026.09.21" in baseline
    assert "22f2b6ec1dbfe8661daf956bc985539f3ef5c03f" in baseline
    assert "not a production release" in baseline
    assert "## In Progress" in kanban
    assert "## In Review" in kanban
    assert "## Ready" in kanban
    assert "## Done" in kanban
    assert "## Blocked" in kanban
    assert "## Withdrawn" in kanban
    assert "Standalone Known Devices inventory" in kanban
    assert "2025-09-19" in roadmap
    assert "2026-09-21" in roadmap
    assert "Inventory candidate withdrawn" in roadmap
    assert "Result usability and visualization" in roadmap
    assert "Discovery Experience Baseline" in roadmap
    assert "Standalone desktop applications" in roadmap
    assert "| 1 | Standalone desktop applications |" in kanban
