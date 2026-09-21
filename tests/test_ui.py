from importlib.resources import files


def test_shared_ramrattan_network_tools_shell_is_packaged():
    ui = files("network_scanner").joinpath("ui")
    html = ui.joinpath("index.html").read_text(encoding="utf-8")
    css = ui.joinpath("styles.css").read_text(encoding="utf-8")

    assert "RAMRATTAN NETWORK TOOLS" in html
    assert "Ramrattan IP Scanner" in html
    assert 'id="btn-help"' in html
    assert 'id="help-panel"' in html
    assert 'id="summary-attempted"' in html
    assert 'id="results-body"' in html
    assert "#173f63" in css.lower()
    assert ui.joinpath("ramrattan-logo.png").is_file()
