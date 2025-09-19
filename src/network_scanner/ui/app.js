async function loadHistory() {
  const res = await fetch('/api/history');
  const data = await res.json();
  const body = document.getElementById('history-body');
  body.innerHTML = '';
  for (const scan of data.scans) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${scan.timestamp_utc}</td>
      <td>${scan.network_name}</td>
      <td>${scan.cidr}</td>
      <td>${scan.stats?.duration_ms ?? ''}</td>
      <td>${scan.stats?.hosts_up ?? ''}</td>
      <td>${scan.stats?.website ?? ''}</td>
      <td>${scan.stats?.upnp ?? ''}</td>
      <td>${scan.stats?.bonjour ?? ''}</td>
      <td>${scan.stats?.ipv6 ?? ''}</td>
    `;
    body.appendChild(tr);
  }
}

document.getElementById('btn-scan').addEventListener('click', async () => {
  await fetch('/api/start-scan', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({}) });
  await loadHistory();
});

document.getElementById('btn-scan-custom').addEventListener('click', async () => {
  const start_ip = prompt('Start IP', '');
  const end_ip = prompt('End IP', '');
  if (!start_ip || !end_ip) return;
  await fetch('/api/start-scan', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ start_ip, end_ip }) });
  await loadHistory();
});

document.getElementById('btn-clear').addEventListener('click', async () => {
  const ok = confirm('Are you sure (Y/N)'.replace('(Y/N)', 'Y/N'));
  if (!ok) return;
  await fetch('/api/clear-history', { method: 'POST' });
  await loadHistory();
});

loadHistory();
