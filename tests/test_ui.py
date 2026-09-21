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
    assert 'id="history-chart"' in html
    assert 'id="device-type-chart"' in html
    assert 'id="history-chart-tooltip"' in html
    assert 'id="device-type-chart-tooltip"' in html
    assert 'name="history-chart-type"' in html
    assert 'value="area"' in html
    assert 'id="device-summary-card"' in html
    assert 'id="device-summary-grid"' in html
    assert 'id="latest-device-total"' in html
    assert 'id="history-device-type-legend"' not in html
    assert 'id="device-type-legend"' not in html
    assert "Devices found over time" in html
    assert "Device types" in html
    assert "inclusive starting and ending IPv4 addresses" in html
    assert "Why some values are unknown" in html
    assert "MAC status" in html
    assert "MAC vendor" in html
    assert "Shared/proxy response" in javascript
    assert "Sort and interpret MAC details" in html
    assert "data-sort-type" in html
    assert "DEVICE_ICONS" in javascript
    assert "Game Console" in javascript
    assert "Network Device" in javascript
    assert "Shared/proxy responder" in javascript
    assert "makeSortable('history-table')" in javascript
    assert "makeSortable('results-table')" in javascript
    assert "renderHistoryChart" in javascript
    assert "renderDeviceTypeChart" in javascript
    assert "renderDeviceTypeChart(scans[0])" in javascript
    assert "scanDeviceCount" in javascript
    assert "scanTypeBreakdown" in javascript
    assert "renderDeviceSummary" in javascript
    assert "renderDeviceSummary(scans[0], historicalTypes)" in javascript
    assert "Unclassified" in javascript
    assert "chart-area" in javascript
    assert "activateChartScan" in javascript
    assert "ip-scanner-history-chart-type" in javascript
    assert "Scan time (local)" in javascript
    assert "DEVICE_TYPE_COLORS" in javascript
    assert "Other: '#9fc8e8'" in javascript
    assert "icon.style.color = color" in javascript
    assert "device-summary-icon" in javascript
    assert "DEVICE_ICONS[type] || DEVICE_ICONS.Other" in javascript
    assert "attachChartTooltip" in javascript
    assert "pointerenter" in javascript
    assert "pointermove" in javascript
    assert "role=\"tooltip\"" in html
    assert "not an exhaustive port scan" in html
    assert "/app.js?v=" in html
    assert "Known devices" not in html
    assert "/api/inventory" not in javascript
    assert "#173f63" in css.lower()
    assert ui.joinpath("ramrattan-logo.png").is_file()
