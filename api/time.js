// Точний час для годинника в HUD. Сервери Vercel синхронізовані з NTP; браузер не може ходити на NTP напряму (UDP),
// тому сторінка кілька разів запитує цю функцію і рахує зсув свого годинника з поправкою на половину затримки, як NTP.
export default function handler(req, res) {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Content-Type', 'application/json; charset=utf-8');
  res.status(200).json({ t: Date.now() });
}
