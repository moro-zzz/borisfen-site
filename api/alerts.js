// Стан повітряної тривоги в м. Київ для HUD на головній.
// Serverless-функція Vercel: браузер не може ходити на джерела напряму (немає CORS), тому проксіюємо
// і кешуємо відповідь на 30 с на edge. Джерела: карта Вадима Клименка (основне), ubilling (резерв).
const SOURCES = [
  {
    name: 'vadimklimenko',
    url: 'https://vadimklimenko.com/map/statuses.json',
    pick(d) {
      const s = d && d.states && d.states['м. Київ'];
      if (!s) return null;
      return { alert: !!s.enabled, since: s.enabled ? s.enabled_at : s.disabled_at };
    }
  },
  {
    name: 'ubilling',
    url: 'https://ubilling.net.ua/aerialalerts/?json=true',
    pick(d) {
      const s = d && d.states && d.states['м. Київ'];
      if (!s) return null;
      return { alert: !!s.alertnow, since: s.changed && !s.changed.startsWith('1970') ? s.changed : null };
    }
  }
];

async function fetchJson(url, ms) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    const r = await fetch(url, { signal: ctrl.signal, headers: { 'User-Agent': 'borisfen-site/1.0 (+https://borisfen-site.vercel.app)' } });
    if (!r.ok) throw new Error('HTTP ' + r.status);
    return await r.json();
  } finally { clearTimeout(timer); }
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  for (const src of SOURCES) {
    try {
      const data = src.pick(await fetchJson(src.url, 6000));
      if (data) {
        res.setHeader('Cache-Control', 'public, s-maxage=30, stale-while-revalidate=120');
        res.status(200).json({ region: 'м. Київ', alert: data.alert, since: data.since || null, source: src.name, at: new Date().toISOString() });
        return;
      }
    } catch (e) { /* пробуємо наступне джерело */ }
  }
  res.setHeader('Cache-Control', 'no-store');
  res.status(503).json({ region: 'м. Київ', alert: null, error: 'sources unavailable' });
}
