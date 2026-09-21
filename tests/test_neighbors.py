from network_scanner.neighbors import neighbor_command, parse_neighbor_table


def test_neighbor_command_is_platform_specific():
    assert neighbor_command("darwin") == ["arp", "-an"]
    assert neighbor_command("linux") == ["arp", "-an"]
    assert neighbor_command("win32") == ["arp", "-a"]


def test_parses_macos_and_windows_neighbor_entries():
    output = """
? (192.168.2.1) at 0:1c:42:aa:bb:cc on en0 ifscope [ethernet]
  192.168.2.25          aa-bb-cc-dd-ee-ff     dynamic
? (192.168.2.99) at (incomplete) on en0 ifscope [ethernet]
"""
    assert parse_neighbor_table(output) == {
        "192.168.2.1": "00:1C:42:AA:BB:CC",
        "192.168.2.25": "AA:BB:CC:DD:EE:FF",
    }
