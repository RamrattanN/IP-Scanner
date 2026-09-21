const historyBody = document.getElementById('history-body');
const historyEmpty = document.getElementById('history-empty');
const historyScroll = document.querySelector('#history-table').closest('.table-scroll');
const actionStatus = document.getElementById('action-status');
const scanButton = document.getElementById('btn-scan');
const customScanButton = document.getElementById('btn-scan-custom');
const clearButton = document.getElementById('btn-clear');
const helpButton = document.getElementById('btn-help');
const closeHelpButton = document.getElementById('btn-close-help');
const helpPanel = document.getElementById('help-panel');
const helpScrim = document.getElementById('help-scrim');
const resultsSection = document.getElementById('results-section');
const resultsRange = document.getElementById('results-range');
const resultsBody = document.getElementById('results-body');
const resultsEmpty = document.getElementById('results-empty');
const resultsScroll = document.querySelector('#results-table').closest('.table-scroll');
const inventoryBody = document.getElementById('inventory-body');
const inventoryEmpty = document.getElementById('inventory-empty');
const inventoryScroll = document.getElementById('inventory-scroll');

let selectedScanId = null;

const cell = (value) => {
  const td = document.createElement('td');
  td.textContent = value ?? '';
  return td;
};

const identityCell = (host) => {
  const td = document.createElement('td');
  const primary = document.createElement('span');
  primary.className = 'identity-primary';
  primary.textContent = host.name || 'Not advertised';
  td.appendChild(primary);
  const source = host.names?.find((item) => item.value === host.name)?.source;
  if (source) {
    const secondary = document.createElement('span');
    secondary.className = 'identity-source';
    secondary.textContent = source;
    td.appendChild(secondary);
  }
  return td;
};

const confidenceCell = (value) => {
  const td = document.createElement('td');
  const badge = document.createElement('span');
  const confidence = value || 'Legacy';
  badge.className = `confidence confidence-${confidence.toLowerCase()}`;
  badge.textContent = confidence;
  td.appendChild(badge);
  return td;
};

const durationLabel = (milliseconds) => {
  if (!Number.isFinite(milliseconds)) return '';
  if (milliseconds < 1000) return `${milliseconds} ms`;
  return `${(milliseconds / 1000).toFixed(1)} s`;
};

const scanRange = (scan) => {
  const start = scan.range?.start;
  const end = scan.range?.end;
  return start && end ? `${start} through ${end}` : (scan.cidr || '');
};

function renderResults(scan) {
  if (!scan) {
    resultsSection.hidden = true;
    return;
  }
  resultsSection.hidden = false;
  resultsRange.textContent = `${scanRange(scan)}.  Select a history row to review that scan.`;
  document.getElementById('summary-requested').textContent = scan.stats?.addresses_requested ?? 'Not recorded';
  document.getElementById('summary-attempted').textContent = scan.stats?.addresses_attempted ?? 'Not recorded';
  document.getElementById('summary-confirmed').textContent = scan.stats?.confirmed_devices ?? 'Not recorded';
  document.getElementById('summary-observed').textContent = scan.stats?.observed_devices ?? 'Not recorded';
  document.getElementById('summary-errors').textContent = scan.stats?.probe_errors ?? 'Not recorded';

  const hosts = Array.isArray(scan.hosts) ? scan.hosts : [];
  resultsBody.replaceChildren();
  for (const host of hosts) {
    const row = document.createElement('tr');
    const evidence = Array.isArray(host.evidence) ? host.evidence.join(', ') : (host.flags?.P ? 'ICMP' : 'Legacy result');
    const services = Array.isArray(host.services) ? host.services.join(', ') : (host.flags?.W ? 'Web' : '');
    const product = [host.manufacturer, host.model].filter(Boolean).join(' ');
    const mac = host.mac || (host.notes?.shared_proxy_mac ? `Shared/proxy response (${host.notes.shared_proxy_mac})` : 'Not available');
    row.append(
      cell(host.ip), identityCell(host), cell(product || 'Not advertised'), cell(mac),
      confidenceCell(host.confidence), cell(evidence || 'Unknown'),
      cell(services || 'None detected'), cell(host.flags?.G ? 'Gateway' : ''),
    );
    resultsBody.appendChild(row);
  }
  resultsEmpty.hidden = hosts.length !== 0;
  resultsScroll.hidden = hosts.length === 0;
}

const inventoryIdentityCell = (device) => {
  const td = document.createElement('td');
  const primary = document.createElement('span');
  primary.className = 'identity-primary';
  primary.textContent = device.name || 'Not advertised';
  td.appendChild(primary);
  if (device.identity_basis) {
    const secondary = document.createElement('span');
    secondary.className = 'identity-source';
    secondary.textContent = device.identity_basis === 'mac' ? 'Reconciled by MAC' : 'Network and IP fallback';
    td.appendChild(secondary);
  }
  return td;
};

const inventoryActionCell = (device) => {
  const td = document.createElement('td');
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'button button-secondary button-small';
  button.textContent = device.user_label ? 'Edit label' : 'Add label';
  button.addEventListener('click', () => editInventoryLabel(device));
  td.appendChild(button);
  return td;
};

function renderInventory(data) {
  const devices = Array.isArray(data?.devices) ? data.devices : [];
  document.getElementById('inventory-total').textContent = devices.length;
  document.getElementById('inventory-labeled').textContent = devices.filter((device) => device.user_label).length;
  document.getElementById('inventory-repeat').textContent = devices.filter((device) => device.observation_count > 1).length;
  inventoryBody.replaceChildren();
  for (const device of devices) {
    const row = document.createElement('tr');
    const product = [device.manufacturer, device.model].filter(Boolean).join(' ');
    row.append(
      cell(device.user_label || 'Not labeled'), inventoryIdentityCell(device),
      cell(device.last_ip || 'Not available'), cell(device.mac || 'Not available'),
      cell(product || 'Not advertised'), cell(device.last_seen_utc || 'Not recorded'),
      cell(device.observation_count ?? 0), confidenceCell(device.confidence),
      inventoryActionCell(device),
    );
    inventoryBody.appendChild(row);
  }
  inventoryEmpty.hidden = devices.length !== 0;
  inventoryScroll.hidden = devices.length === 0;
}

async function loadInventory() {
  const response = await fetch('/api/inventory');
  if (!response.ok) throw new Error('Device inventory could not be loaded.');
  renderInventory(await response.json());
}

async function editInventoryLabel(device) {
  const label = window.prompt(
    'Device label.  Leave blank to remove the current label.',
    device.user_label || '',
  );
  if (label === null) return;
  actionStatus.textContent = 'Saving device label...';
  try {
    const response = await fetch(`/api/inventory/${encodeURIComponent(device.id)}`, {
      method: 'PATCH', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({label}),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'The device label could not be saved.');
    }
    await loadInventory();
    actionStatus.textContent = label.trim() ? 'Device label saved.' : 'Device label removed.';
  } catch (error) {
    actionStatus.textContent = error.message;
  }
}

function selectScan(scan, row) {
  selectedScanId = scan.id;
  document.querySelectorAll('.history-row').forEach((item) => item.classList.remove('is-selected'));
  row.classList.add('is-selected');
  renderResults(scan);
}

async function loadHistory() {
  const response = await fetch('/api/history');
  if (!response.ok) throw new Error('Scan history could not be loaded.');
  const data = await response.json();
  const scans = Array.isArray(data.scans) ? [...data.scans].reverse() : [];
  historyBody.replaceChildren();
  let selected = null;
  for (const scan of scans) {
    const row = document.createElement('tr');
    row.className = 'history-row';
    row.tabIndex = 0;
    row.setAttribute('aria-label', `Review scan from ${scan.timestamp_utc}`);
    row.append(
      cell(scan.timestamp_utc), cell(scan.network_name), cell(scanRange(scan)),
      cell(durationLabel(scan.stats?.duration_ms)), cell(scan.stats?.addresses_requested ?? 'Not recorded'),
      cell(scan.stats?.addresses_attempted ?? 'Not recorded'),
      cell(scan.stats?.confirmed_devices ?? 'Not recorded'),
      cell(scan.stats?.observed_devices ?? 'Not recorded'), cell(scan.stats?.website),
    );
    row.addEventListener('click', () => selectScan(scan, row));
    row.addEventListener('keydown', (event) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        selectScan(scan, row);
      }
    });
    historyBody.appendChild(row);
    if (!selected && (scan.id === selectedScanId || selectedScanId === null)) selected = {scan, row};
  }
  historyEmpty.hidden = scans.length !== 0;
  historyScroll.hidden = scans.length === 0;
  if (selected) selectScan(selected.scan, selected.row);
  else renderResults(null);
}

function setBusy(busy, message = '') {
  scanButton.disabled = busy;
  customScanButton.disabled = busy;
  clearButton.disabled = busy;
  actionStatus.textContent = message;
}

async function startScan(payload) {
  setBusy(true, 'Interrogating every address in the selected range...');
  try {
    const response = await fetch('/api/start-scan', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'The scan could not be completed.');
    }
    const result = await response.json();
    selectedScanId = result.scan_id;
    await Promise.all([loadHistory(), loadInventory()]);
    const stats = result.stats || {};
    const exclusions = (stats.proxy_arp_ignored || 0) + (stats.reserved_ignored || 0);
    actionStatus.textContent = `Scan completed.  Attempted ${stats.addresses_attempted} of ${stats.addresses_requested} addresses.  Confirmed ${stats.confirmed_devices} devices and retained ${stats.observed_devices} ARP-only observations.  Excluded ${exclusions} proxy or reserved artifacts.`;
  } catch (error) {
    actionStatus.textContent = error.message;
  } finally {
    setBusy(false, actionStatus.textContent);
  }
}

scanButton.addEventListener('click', () => startScan({}));
customScanButton.addEventListener('click', () => {
  const startIp = window.prompt('Starting IPv4 address');
  if (!startIp) return;
  const endIp = window.prompt('Ending IPv4 address');
  if (!endIp) return;
  startScan({start_ip: startIp.trim(), end_ip: endIp.trim()});
});

clearButton.addEventListener('click', async () => {
  if (!window.confirm('Clear all locally stored scan history?')) return;
  setBusy(true, 'Clearing scan history...');
  try {
    const response = await fetch('/api/clear-history', {method: 'POST'});
    if (!response.ok) throw new Error('Scan history could not be cleared.');
    selectedScanId = null;
    await loadHistory();
    actionStatus.textContent = 'Scan history cleared.';
  } catch (error) {
    actionStatus.textContent = error.message;
  } finally {
    setBusy(false, actionStatus.textContent);
  }
});

function setHelpPanel(open) {
  helpPanel.classList.toggle('is-open', open);
  helpPanel.setAttribute('aria-hidden', String(!open));
  helpButton.setAttribute('aria-expanded', String(open));
  helpScrim.hidden = !open;
  if (open) closeHelpButton.focus();
  else helpButton.focus();
}

helpButton.addEventListener('click', () => setHelpPanel(true));
closeHelpButton.addEventListener('click', () => setHelpPanel(false));
helpScrim.addEventListener('click', () => setHelpPanel(false));
document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape' && helpPanel.classList.contains('is-open')) setHelpPanel(false);
});

Promise.all([loadHistory(), loadInventory()]).catch((error) => {
  actionStatus.textContent = error.message;
  historyEmpty.hidden = false;
});
