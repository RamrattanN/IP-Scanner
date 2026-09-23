from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_recovery_documentation_set_is_complete_and_linked():
    expected = {
        "README.md",
        "Current-Baseline.md",
        "Desktop-Packaging.md",
        "Recovery-Baseline.md",
        "Discovery-Confidence.md",
        "UX-Guidelines.md",
        "KANBAN.md",
        "ROADMAP.md",
        "Third-Party-Notices.md",
        "WIKI.md",
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

    assert "Ramrattan IP Scanner v1.1.1" in baseline
    assert "7ee0d6544309b011d9bddc3f59013935edde6e02" in baseline
    assert "v1.1.0 Desktop Application Release" in baseline
    assert "owner-accepted unsigned desktop release" in baseline.lower()
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
    assert "IP Scanner v1.1.0 desktop release" in kanban
    assert "IP Scanner v1.1.1 maintenance release" in kanban
    assert "236 packaged probe errors" in roadmap


def test_wiki_home_tracks_current_release_and_delivery_sources():
    wiki = (ROOT / "docs" / "WIKI.md").read_text(encoding="utf-8")
    assert "v1.1.1 - Desktop Discovery Maintenance Release" in wiki
    assert "/releases/tag/v1.1.1" in wiki
    assert "/blob/main/docs/KANBAN.md" in wiki
    assert "/blob/main/docs/ROADMAP.md" in wiki
    assert "repository documents are the canonical" in wiki.lower()


def test_desktop_packaging_documents_all_three_targets():
    packaging = (ROOT / "docs" / "Desktop-Packaging.md").read_text(encoding="utf-8")
    assert "IP-Scanner-macOS-Intel-1.1.1.dmg" in packaging
    assert "IP-Scanner-macOS-Apple-Silicon-1.1.1.dmg" in packaging
    assert "IP-Scanner-Windows-x64-1.1.1.exe" in packaging
    assert "Automatic scans" in packaging
    assert "rollback" in packaging.lower()
