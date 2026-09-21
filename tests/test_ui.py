from importlib.resources import files


def test_shared_ramrattan_network_tools_shell_is_packaged():
    ui = files("network_scanner").joinpath("ui")
    html = ui.joinpath("index.html").read_text(encoding="utf-8")
    css = ui.joinpath("styles.css").read_text(encoding="utf-8")
    javascript = ui.joinpath("app.js").read_text(encoding="utf-8")

    assert "RAMRATTAN NETWORK TOOLS" in html
    assert "Ramrattan IP Scanner" in html
    assert 'id="btn-help"' in html
    assert 'id="help-panel"' in html
    assert 'id="summary-attempted"' in html
    assert 'id="summary-confirmed"' in html
    assert 'id="summary-observed"' in html
    assert 'id="results-body"' in html
    assert "inclusive starting and ending IPv4 addresses" in html
    assert "Why some values are unknown" in html
    assert "MAC status" in html
    assert "Shared/proxy response" in javascript
    assert "Sort and interpret MAC details" in html
    assert "data-sort-type" in html
    assert "DEVICE_ICONS" in javascript
    assert "makeSortable('history-table')" in javascript
    assert "makeSortable('results-table')" in javascript
    assert "not an exhaustive port scan" in html
    assert "/app.js?v=" in html
    assert "Known devices" not in html
    assert "/api/inventory" not in javascript
    assert "#173f63" in css.lower()
    assert ui.joinpath("ramrattan-logo.png").is_file()
