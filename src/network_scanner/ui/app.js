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

const cell = (value) => {
  const td = document.createElement('td');
  td.textContent = value ?? '';
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
  document.getElementById('summary-devices').textContent = scan.stats?.hosts_up ?? scan.hosts?.length ?? 0;
  document.getElementById('summary-errors').textContent = scan.stats?.probe_errors ?? 'Not recorded';

  const hosts = Array.isArray(scan.hosts) ? scan.hosts : [];
  resultsBody.replaceChildren();
  for (const host of hosts) {
    const row = document.createElement('tr');
    const evidence = Array.isArray(host.evidence) ? host.evidence.join(', ') : (host.flags?.P ? 'ICMP' : 'Legacy result');
    const services = Array.isArray(host.services) ? host.services.join(', ') : (host.flags?.W ? 'Web' : '');
    row.append(
      cell(host.ip), cell(host.name || 'Unknown'), cell(host.mac || 'Unknown'),
      cell(evidence || 'Unknown'), cell(services || 'None detected'),
      cell(host.flags?.G ? 'Gateway' : ''),
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
      cell(scan.stats?.addresses_attempted ?? 'Not recorded'), cell(scan.stats?.hosts_up),
      cell(scan.stats?.ping_replies ?? 'Not recorded'), cell(scan.stats?.website),
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
    actionStatus.textContent = `Scan completed.  Attempted ${stats.addresses_attempted} of ${stats.addresses_requested} addresses and discovered ${stats.hosts_up} devices.`;
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

loadHistory().catch((error) => {
  actionStatus.textContent = error.message;
  historyEmpty.hidden = false;
});
