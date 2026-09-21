const historyBody = document.getElementById('history-body');
const historyEmpty = document.getElementById('history-empty');
const tableScroll = document.querySelector('.table-scroll');
const actionStatus = document.getElementById('action-status');
const scanButton = document.getElementById('btn-scan');
const customScanButton = document.getElementById('btn-scan-custom');
const clearButton = document.getElementById('btn-clear');
const helpButton = document.getElementById('btn-help');
const closeHelpButton = document.getElementById('btn-close-help');
const helpPanel = document.getElementById('help-panel');
const helpScrim = document.getElementById('help-scrim');

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

async function loadHistory() {
  const response = await fetch('/api/history');
  if (!response.ok) throw new Error('Scan history could not be loaded.');
  const data = await response.json();
  const scans = Array.isArray(data.scans) ? [...data.scans].reverse() : [];
  historyBody.replaceChildren();
  for (const scan of scans) {
    const row = document.createElement('tr');
    row.append(
      cell(scan.timestamp_utc), cell(scan.network_name), cell(scan.cidr),
      cell(durationLabel(scan.stats?.duration_ms)), cell(scan.stats?.hosts_up),
      cell(scan.stats?.website), cell(scan.stats?.upnp),
      cell(scan.stats?.bonjour), cell(scan.stats?.ipv6),
    );
    historyBody.appendChild(row);
  }
  historyEmpty.hidden = scans.length !== 0;
  tableScroll.hidden = scans.length === 0;
}

function setBusy(busy, message = '') {
  scanButton.disabled = busy;
  customScanButton.disabled = busy;
  clearButton.disabled = busy;
  actionStatus.textContent = message;
}

async function startScan(payload) {
  setBusy(true, 'Scanning the selected address range...');
  try {
    const response = await fetch('/api/start-scan', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'The scan could not be completed.');
    }
    await loadHistory();
    actionStatus.textContent = 'Scan completed.';
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
