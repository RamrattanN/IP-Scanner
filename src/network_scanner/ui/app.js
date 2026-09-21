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

let selectedScanId = null;

const cell = (value, sortValue = value) => {
  const td = document.createElement('td');
  td.textContent = value ?? '';
  td.dataset.sortValue = sortValue ?? '';
  return td;
};

const identityCell = (host) => {
  const td = document.createElement('td');
  const primary = document.createElement('span');
  primary.className = 'identity-primary';
  primary.textContent = host.name || 'Not advertised';
  td.appendChild(primary);
  td.dataset.sortValue = host.name || '';
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
  td.dataset.sortValue = confidence;
  return td;
};

const DEVICE_ICONS = {
  Computer: '<rect x="4" y="5" width="16" height="11" rx="1"></rect><path d="M8 20h8M12 16v4"></path>',
  Router: '<rect x="4" y="11" width="16" height="7" rx="2"></rect><path d="M8 14h.01M12 14h.01M16 14h.01M8 8a6 6 0 0 1 8 0M10 6a3 3 0 0 1 4 0"></path>',
  Printer: '<path d="M7 9V4h10v5M7 17H5a2 2 0 0 1-2-2v-4a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v4a2 2 0 0 1-2 2h-2M7 14h10v6H7z"></path>',
  TV: '<rect x="3" y="5" width="18" height="13" rx="2"></rect><path d="M8 22h8M12 18v4"></path>',
  Audio: '<rect x="6" y="3" width="12" height="18" rx="2"></rect><circle cx="12" cy="14" r="4"></circle><circle cx="12" cy="7" r="1"></circle>',
  NAS: '<rect x="5" y="3" width="14" height="8" rx="2"></rect><rect x="5" y="13" width="14" height="8" rx="2"></rect><path d="M9 7h.01M9 17h.01M13 7h3M13 17h3"></path>',
  Mobile: '<rect x="7" y="2" width="10" height="20" rx="2"></rect><path d="M11 18h2"></path>',
  IoT: '<path d="M9 18h6M10 22h4M8.5 14.5A6 6 0 1 1 15.5 14.5C14.5 15.3 14 16 14 18h-4c0-2-.5-2.7-1.5-3.5z"></path>',
  'Game Console': '<path d="M8 8h8a5 5 0 0 1 4.7 3.3l1 3.2a3 3 0 0 1-4.8 3.2L15 16h-6l-1.9 1.7a3 3 0 0 1-4.8-3.2l1-3.2A5 5 0 0 1 8 8zM7 11v4M5 13h4M16.5 12h.01M18.5 14h.01"></path>',
  'Network Device': '<rect x="3" y="8" width="18" height="9" rx="2"></rect><path d="M7 12h.01M10 12h.01M13 12h.01M6 21v-4M18 21v-4M12 8V4M9 4h6"></path>',
  Other: '<circle cx="12" cy="12" r="9"></circle><path d="M9.8 9a2.4 2.4 0 1 1 3.1 2.3c-.9.4-1.4 1-1.4 2M12 17h.01"></path>',
};

const deviceTypeCell = (host) => {
  const type = host.device_type || 'Other';
  const td = document.createElement('td');
  td.dataset.sortValue = type;
  td.setAttribute('aria-label', type);
  const icon = document.createElement('span');
  icon.className = 'device-type-icon';
  icon.title = type;
  const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', '0 0 24 24');
  svg.setAttribute('aria-hidden', 'true');
  svg.innerHTML = DEVICE_ICONS[type] || DEVICE_ICONS.Other;
  icon.appendChild(svg);
  td.appendChild(icon);
  return td;
};

const formatMac = (value) => {
  if (!value) return null;
  const parts = value.replaceAll('-', ':').split(':');
  if (parts.length !== 6 || parts.some((part) => !/^[0-9a-f]{1,2}$/i.test(part))) return value.toUpperCase();
  return parts.map((part) => part.padStart(2, '0').toUpperCase()).join(':');
};

const macVendorCell = (host) => {
  const td = document.createElement('td');
  const sharedVendor = host.notes?.shared_proxy_vendor;
  const vendor = host.mac_vendor || sharedVendor;
  td.dataset.sortValue = vendor || '';
  td.textContent = vendor || 'Not available';
  if (sharedVendor) {
    const secondary = document.createElement('span');
    secondary.className = 'identity-source';
    secondary.textContent = 'Shared/proxy responder';
    td.appendChild(secondary);
  }
  return td;
};

const ipv4SortValue = (value) => {
  const match = String(value).match(/(?:\d{1,3}\.){3}\d{1,3}/);
  if (!match) return Number.POSITIVE_INFINITY;
  return match[0].split('.').reduce((total, octet) => (total * 256) + Number(octet), 0);
};

function compareSortValues(left, right, type) {
  if (type === 'number') {
    const a = Number(left);
    const b = Number(right);
    return (Number.isFinite(a) ? a : Number.POSITIVE_INFINITY) - (Number.isFinite(b) ? b : Number.POSITIVE_INFINITY);
  }
  if (type === 'date') {
    const a = Date.parse(left);
    const b = Date.parse(right);
    return (Number.isFinite(a) ? a : Number.POSITIVE_INFINITY) - (Number.isFinite(b) ? b : Number.POSITIVE_INFINITY);
  }
  if (type === 'ip') return ipv4SortValue(left) - ipv4SortValue(right);
  return String(left).localeCompare(String(right), undefined, {numeric: true, sensitivity: 'base'});
}

function makeSortable(tableId) {
  const table = document.getElementById(tableId);
  const headers = [...table.querySelectorAll('thead th')];
  headers.forEach((header, columnIndex) => {
    const button = header.querySelector('.sort-button');
    if (!button) return;
    button.addEventListener('click', () => {
      const descending = header.getAttribute('aria-sort') === 'ascending';
      headers.forEach((item) => item.removeAttribute('aria-sort'));
      header.setAttribute('aria-sort', descending ? 'descending' : 'ascending');
      const direction = descending ? -1 : 1;
      const rows = [...table.tBodies[0].rows].map((row, originalIndex) => ({row, originalIndex}));
      rows.sort((a, b) => {
        const left = a.row.cells[columnIndex]?.dataset.sortValue ?? '';
        const right = b.row.cells[columnIndex]?.dataset.sortValue ?? '';
        return (compareSortValues(left, right, button.dataset.sortType) * direction)
          || (a.originalIndex - b.originalIndex);
      });
      rows.forEach(({row}) => table.tBodies[0].appendChild(row));
    });
  });
}

function resetTableSort(tableId) {
  document.querySelectorAll(`#${tableId} thead th`).forEach((header) => {
    header.removeAttribute('aria-sort');
  });
}

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
  resetTableSort('results-table');
  resultsBody.replaceChildren();
  for (const host of hosts) {
    const row = document.createElement('tr');
    const evidence = Array.isArray(host.evidence) ? host.evidence.join(', ') : (host.flags?.P ? 'ICMP' : 'Legacy result');
    const services = Array.isArray(host.services) ? host.services.join(', ') : (host.flags?.W ? 'Web' : '');
    const product = [host.manufacturer, host.model].filter(Boolean).join(' ');
    const sharedMac = formatMac(host.notes?.shared_proxy_mac);
    const mac = formatMac(host.mac) || sharedMac;
    const macStatus = sharedMac ? 'Shared/proxy response' : (mac ? 'Observed' : 'Not available');
    row.append(
      deviceTypeCell(host), cell(host.ip), identityCell(host), cell(product || 'Not advertised'),
      cell(mac || 'Not available'), macVendorCell(host), cell(macStatus), confidenceCell(host.confidence), cell(evidence || 'Unknown'),
      cell(services || 'None detected'), cell(host.flags?.G ? 'Gateway' : ''),
    );
    resultsBody.appendChild(row);
  }
  resultsEmpty.hidden = hosts.length !== 0;
  resultsScroll.hidden = hosts.length === 0;
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
  resetTableSort('history-table');
  historyBody.replaceChildren();
  let selected = null;
  for (const scan of scans) {
    const row = document.createElement('tr');
    row.className = 'history-row';
    row.tabIndex = 0;
    row.setAttribute('aria-label', `Review scan from ${scan.timestamp_utc}`);
    row.append(
      cell(scan.timestamp_utc), cell(scan.network_name), cell(scanRange(scan)),
      cell(durationLabel(scan.stats?.duration_ms), scan.stats?.duration_ms),
      cell(scan.stats?.addresses_requested ?? 'Not recorded', scan.stats?.addresses_requested),
      cell(scan.stats?.addresses_attempted ?? 'Not recorded', scan.stats?.addresses_attempted),
      cell(scan.stats?.confirmed_devices ?? 'Not recorded', scan.stats?.confirmed_devices),
      cell(scan.stats?.observed_devices ?? 'Not recorded', scan.stats?.observed_devices),
      cell(scan.stats?.website ?? 'Not recorded', scan.stats?.website),
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
    await loadHistory();
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

makeSortable('history-table');
makeSortable('results-table');

loadHistory().catch((error) => {
  actionStatus.textContent = error.message;
  historyEmpty.hidden = false;
});
