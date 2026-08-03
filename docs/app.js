async function load() {
  try {
    const res = await fetch('dashboard-data.json');
    const data = await res.json();
    const summary = document.getElementById('summary');
    summary.innerText = `Latest snapshots: ${data.latest.length} · Changes: ${data.changes.length} · Clearance candidates: ${data.clearance.length}`;

    const cl = document.getElementById('clearance');
    data.clearance.slice(0,20).forEach(c=>{
      const li = document.createElement('li');
      li.innerText = `${c.sku} — ${c.name} — score ${c.clearance_score} — ${c.discount_percent}% off`;
      cl.appendChild(li);
    });

    const changes = document.getElementById('changes');
    data.changes.slice(-50).reverse().forEach(e=>{
      const li = document.createElement('li');
      li.innerText = `${e.timestamp} — ${e.event} — ${e.sku} @ ${e.store} (${e.old} → ${e.new})`;
      changes.appendChild(li);
    });
  } catch (err) {
    document.getElementById('summary').innerText = 'Failed to load dashboard data';
    console.error(err);
  }
}
load();
