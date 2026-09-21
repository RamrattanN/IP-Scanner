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
const historyChart = document.getElementById('history-chart');
const historyChartEmpty = document.getElementById('history-chart-empty');
const historyChartTooltip = document.getElementById('history-chart-tooltip');
const historyChartTypeInputs = [...document.querySelectorAll('input[name="history-chart-type"]')];
const deviceTypeChart = document.getElementById('device-type-chart');
const deviceTypeChartEmpty = document.getElementById('device-type-chart-empty');
const deviceTypeChartTooltip = document.getElementById('device-type-chart-tooltip');
const deviceTypeLegend = document.getElementById('device-type-legend');

let selectedScanId = null;
let chartScans = [];
let historyChartType = localStorage.getItem('ip-scanner-history-chart-type') || 'line';
if (!['bar', 'line'].includes(historyChartType)) historyChartType = 'line';

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

const DEVICE_TYPE_COLORS = {
  Router: '#173f63',
  'Network Device': '#2f78b8',
  Computer: '#27a9c2',
  'Game Console': '#6c63b7',
  Printer: '#63b5a4',
  TV: '#d27c3f',
  Audio: '#9b6b9e',
  NAS: '#5e7b96',
  Mobile: '#8aae4f',
  IoT: '#c2a23a',
  Other: '#8794a0',
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

const SVG_NS = 'http://www.w3.org/2000/svg';

const svgElement = (name, attributes = {}, text = null) => {
  const element = document.createElementNS(SVG_NS, name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  if (text !== null) element.textContent = text;
  return element;
};

const hideChartTooltip = (tooltip) => {
  tooltip.hidden = true;
  tooltip.setAttribute('aria-hidden', 'true');
};

const showChartTooltip = (tooltip, stage, heading, metric, event, mark) => {
  const title = document.createElement('strong');
  title.textContent = heading;
  const value = document.createElement('span');
  value.textContent = metric;
  tooltip.replaceChildren(title, value);
  tooltip.hidden = false;
  tooltip.setAttribute('aria-hidden', 'false');

  const stageBounds = stage.getBoundingClientRect();
  const markBounds = mark.getBoundingClientRect();
  const pointerX = Number.isFinite(event?.clientX) ? event.clientX : markBounds.left + (markBounds.width / 2);
  const pointerY = Number.isFinite(event?.clientY) ? event.clientY : markBounds.top;
  const halfWidth = (tooltip.offsetWidth / 2) + 6;
  const x = Math.min(Math.max(pointerX - stageBounds.left, halfWidth), stageBounds.width - halfWidth);
  const y = Math.max(pointerY - stageBounds.top - 10, tooltip.offsetHeight + 6);
  tooltip.style.left = `${x}px`;
  tooltip.style.top = `${y}px`;
};

const attachChartTooltip = (mark, tooltip, heading, metric) => {
  const stage = tooltip.closest('.chart-stage');
  const show = (event) => showChartTooltip(tooltip, stage, heading, metric, event, mark);
  mark.addEventListener('pointerenter', show);
  mark.addEventListener('pointermove', show);
  mark.addEventListener('pointerleave', () => hideChartTooltip(tooltip));
  mark.addEventListener('focus', show);
  mark.addEventListener('blur', () => hideChartTooltip(tooltip));
};

const scanDeviceCount = (scan) => {
  const total = Number(scan.stats?.hosts_up);
  if (Number.isFinite(total)) return total;
  const confirmed = Number(scan.stats?.confirmed_devices);
  const observed = Number(scan.stats?.observed_devices);
  if (Number.isFinite(confirmed) || Number.isFinite(observed)) {
    return (Number.isFinite(confirmed) ? confirmed : 0) + (Number.isFinite(observed) ? observed : 0);
  }
  return Array.isArray(scan.hosts) ? scan.hosts.length : 0;
};

const chartTimestamp = (value) => {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value || 'Unknown time';
  return date.toLocaleString(undefined, {
    month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit',
  });
};

const niceChartScale = (maximum) => {
  const rawStep = Math.max(1, maximum) / 4;
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const normalized = rawStep / magnitude;
  const factor = normalized <= 1 ? 1 : (normalized <= 2 ? 2 : (normalized <= 5 ? 5 : 10));
  const step = Math.max(1, factor * magnitude);
  return {step, maximum: Math.max(step, Math.ceil(maximum / step) * step)};
};

function renderHistoryChart() {
  hideChartTooltip(historyChartTooltip);
  historyChart.replaceChildren();
  historyChartTypeInputs.forEach((input) => { input.checked = input.value === historyChartType; });
  if (!chartScans.length) {
    historyChart.hidden = true;
    historyChartEmpty.hidden = false;
    return;
  }
  historyChart.hidden = false;
  historyChartEmpty.hidden = true;

  const width = 760;
  const height = 320;
  const margin = {top: 18, right: 24, bottom: 66, left: 62};
  const plotWidth = width - margin.left - margin.right;
  const plotHeight = height - margin.top - margin.bottom;
  const values = chartScans.map(scanDeviceCount);
  const scale = niceChartScale(Math.max(...values));
  const x = (index) => {
    if (chartScans.length === 1) return margin.left + (plotWidth / 2);
    if (historyChartType === 'bar') {
      return margin.left + (((index + .5) / chartScans.length) * plotWidth);
    }
    return margin.left + ((index / (chartScans.length - 1)) * plotWidth);
  };
  const y = (value) => margin.top + plotHeight - ((value / scale.maximum) * plotHeight);

  for (let value = 0; value <= scale.maximum; value += scale.step) {
    const yPosition = y(value);
    historyChart.append(
      svgElement('line', {x1: margin.left, y1: yPosition, x2: width - margin.right, y2: yPosition, class: 'chart-grid'}),
      svgElement('text', {x: margin.left - 10, y: yPosition + 4, 'text-anchor': 'end', class: 'chart-label'}, String(value)),
    );
  }
  historyChart.append(
    svgElement('line', {x1: margin.left, y1: margin.top, x2: margin.left, y2: margin.top + plotHeight, class: 'chart-axis'}),
    svgElement('line', {x1: margin.left, y1: margin.top + plotHeight, x2: width - margin.right, y2: margin.top + plotHeight, class: 'chart-axis'}),
    svgElement('text', {x: 16, y: margin.top + (plotHeight / 2), transform: `rotate(-90 16 ${margin.top + (plotHeight / 2)})`, 'text-anchor': 'middle', class: 'chart-axis-title'}, 'Devices found'),
    svgElement('text', {x: margin.left + (plotWidth / 2), y: height - 8, 'text-anchor': 'middle', class: 'chart-axis-title'}, 'Scan time (local)'),
  );

  const labelCount = Math.min(5, chartScans.length);
  const labelIndexes = new Set(Array.from({length: labelCount}, (_, index) => (
    labelCount === 1 ? 0 : Math.round(index * (chartScans.length - 1) / (labelCount - 1))
  )));
  labelIndexes.forEach((index) => {
    historyChart.append(svgElement('text', {
      x: x(index), y: margin.top + plotHeight + 24, 'text-anchor': 'middle', class: 'chart-label',
    }, chartTimestamp(chartScans[index].timestamp_utc)));
  });

  if (historyChartType === 'line' && chartScans.length > 1) {
    const path = values.map((value, index) => `${index ? 'L' : 'M'} ${x(index)} ${y(value)}`).join(' ');
    historyChart.append(svgElement('path', {d: path, class: 'chart-line'}));
  }

  values.forEach((value, index) => {
    const time = chartTimestamp(chartScans[index].timestamp_utc);
    const metric = `${value} device${value === 1 ? '' : 's'} found`;
    const accessibleLabel = `${time}: ${metric}`;
    let mark;
    if (historyChartType === 'bar') {
      const slotWidth = plotWidth / Math.max(values.length, 1);
      const barWidth = Math.max(2, Math.min(42, slotWidth * .66));
      mark = svgElement('rect', {
        x: x(index) - (barWidth / 2), y: y(value), width: barWidth,
        height: Math.max(1, margin.top + plotHeight - y(value)), class: 'chart-bar',
        tabindex: '0', role: 'img', 'aria-label': accessibleLabel,
      });
    } else {
      mark = svgElement('circle', {
        cx: x(index), cy: y(value), r: 5.5, class: 'chart-point',
        tabindex: '0', role: 'img', 'aria-label': accessibleLabel,
      });
    }
    mark.appendChild(svgElement('title', {}, accessibleLabel));
    attachChartTooltip(mark, historyChartTooltip, time, metric);
    historyChart.appendChild(mark);
  });
  historyChart.setAttribute(
    'aria-label',
    `Device discovery history with ${chartScans.length} scans. Latest result: ${values[values.length - 1]} devices found.`,
  );
}

const polarPoint = (centerX, centerY, radius, angle) => {
  const radians = ((angle - 90) * Math.PI) / 180;
  return {x: centerX + (radius * Math.cos(radians)), y: centerY + (radius * Math.sin(radians))};
};

const pieSlicePath = (centerX, centerY, radius, startAngle, endAngle) => {
  const start = polarPoint(centerX, centerY, radius, endAngle);
  const end = polarPoint(centerX, centerY, radius, startAngle);
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  return `M ${centerX} ${centerY} L ${start.x} ${start.y} A ${radius} ${radius} 0 ${largeArc} 0 ${end.x} ${end.y} Z`;
};

function renderDeviceTypeChart(scan) {
  hideChartTooltip(deviceTypeChartTooltip);
  deviceTypeChart.replaceChildren();
  deviceTypeLegend.replaceChildren();
  const hosts = Array.isArray(scan?.hosts) ? scan.hosts : [];
  const counts = new Map();
  hosts.forEach((host) => {
    const type = host.device_type || 'Other';
    counts.set(type, (counts.get(type) || 0) + 1);
  });
  const entries = [...counts.entries()].sort((left, right) => right[1] - left[1]);
  const total = hosts.length;
  if (!total) {
    deviceTypeChart.hidden = true;
    deviceTypeChartEmpty.hidden = false;
    return;
  }
  deviceTypeChart.hidden = false;
  deviceTypeChartEmpty.hidden = true;
  const centerX = 150;
  const centerY = 128;
  const radius = 102;
  let angle = 0;
  entries.forEach(([type, count]) => {
    const sweep = (count / total) * 360;
    const color = DEVICE_TYPE_COLORS[type] || DEVICE_TYPE_COLORS.Other;
    const metric = `${count} device${count === 1 ? '' : 's'}`;
    const label = `${type}: ${metric}`;
    const slice = entries.length === 1
      ? svgElement('circle', {cx: centerX, cy: centerY, r: radius, fill: color, class: 'pie-slice'})
      : svgElement('path', {d: pieSlicePath(centerX, centerY, radius, angle, angle + sweep), fill: color, class: 'pie-slice'});
    slice.setAttribute('tabindex', '0');
    slice.setAttribute('role', 'img');
    slice.setAttribute('aria-label', label);
    slice.appendChild(svgElement('title', {}, label));
    attachChartTooltip(slice, deviceTypeChartTooltip, type, metric);
    deviceTypeChart.appendChild(slice);
    angle += sweep;

    const item = document.createElement('li');
    const icon = document.createElement('span');
    icon.className = 'type-chart-icon';
    icon.style.color = color;
    icon.setAttribute('aria-hidden', 'true');
    const iconSvg = document.createElementNS(SVG_NS, 'svg');
    iconSvg.setAttribute('viewBox', '0 0 24 24');
    iconSvg.innerHTML = DEVICE_ICONS[type] || DEVICE_ICONS.Other;
    icon.appendChild(iconSvg);
    const name = document.createElement('span');
    name.className = 'type-chart-name';
    name.textContent = type;
    name.title = type;
    const amount = document.createElement('span');
    amount.className = 'type-chart-count';
    amount.textContent = count;
    item.append(icon, name, amount);
    deviceTypeLegend.appendChild(item);
  });
  deviceTypeChart.setAttribute('aria-label', `Latest scan device types. ${total} devices across ${entries.length} categories.`);
}

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
  const savedScans = Array.isArray(data.scans) ? data.scans : [];
  chartScans = [...savedScans].sort((left, right) => {
    const difference = Date.parse(left.timestamp_utc) - Date.parse(right.timestamp_utc);
    return Number.isFinite(difference) ? difference : 0;
  });
  renderHistoryChart();
  const scans = [...savedScans].reverse();
  renderDeviceTypeChart(scans[0]);
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

historyChartTypeInputs.forEach((input) => {
  input.addEventListener('change', () => {
    if (!input.checked) return;
    historyChartType = input.value;
    localStorage.setItem('ip-scanner-history-chart-type', historyChartType);
    renderHistoryChart();
  });
});

makeSortable('history-table');
makeSortable('results-table');

loadHistory().catch((error) => {
  actionStatus.textContent = error.message;
  historyEmpty.hidden = false;
});
