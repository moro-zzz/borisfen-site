# -*- coding: utf-8 -*-
"""QA сайту «Борисфен». Запуск: python docs/tools/qa.py [https://borisfen-site.vercel.app]
Перевіряє: сторінки відкриваються, усі локальні посилання/картинки/скрипти віддають 200,
на кожній сторінці є title, description, favicon, меню однакове, у галереї є фото, PDF програми доступний,
немає посилань на #якорі, яких не існує."""
import re, sys, io, html
from urllib.parse import urljoin, urlparse, urldefrag, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = (sys.argv[1] if len(sys.argv) > 1 else 'https://borisfen-site.vercel.app').rstrip('/') + '/'
LOCAL = 'localhost' in BASE or '127.0.0.1' in BASE
PAGES = ['', 'navchannya.html', 'batkam.html'] if LOCAL else ['', 'navchannya', 'batkam']  # cleanUrls лише на Vercel
UA = {'User-Agent': 'BorysfenQA/1.0'}
problems, checked = [], 0

def get(url, method='GET'):
    url = quote(url, safe=':/?#&=%')
    req = Request(url, headers=UA, method=method)
    try:
        with urlopen(req, timeout=20) as r:
            return r.status, r.headers.get('content-type', ''), (r.read() if method == 'GET' else b'')
    except HTTPError as e:
        return e.code, '', b''
    except URLError as e:
        return 0, str(e), b''

def fail(msg): problems.append(msg); print('  ✗', msg)
def ok(msg): print('  ✓', msg)

print(f'QA {BASE}')
menus = {}
for p in PAGES:
    url = BASE + p
    print(f'\n[{url}]')
    st, ct, body = get(url)
    checked += 1
    if st != 200: fail(f'сторінка {url}: HTTP {st}'); continue
    doc = body.decode('utf-8', 'replace')
    ok(f'HTTP 200, {len(body)//1024} KB')
    # мета
    if not re.search(r'<title>[^<]{5,}</title>', doc): fail('немає <title>')
    if 'name="description"' not in doc: fail('немає meta description')
    if 'rel="icon"' not in doc: fail('немає favicon')
    if 'lang="uk"' not in doc: fail('немає lang="uk"')
    # меню
    nav = re.findall(r'<a href="([^"]+)" class="nav__link[^"]*">([^<]+)</a>', doc)
    menus[p] = [t for _, t in nav]
    # якорі
    ids = set(re.findall(r'id="([^"]+)"', doc))
    for href, _ in nav:
        if '#' in href:
            page, frag = href.split('#', 1)
            if frag and (page in ('', 'index.html') and p == '') and frag not in ids:
                fail(f'пункт меню веде на #{frag}, але такого блоку на головній немає')
    # ресурси
    assets = set(re.findall(r'(?:src|href)="([^"]+)"', doc))
    for a in assets:
        a = html.unescape(a)
        if a.startswith(('#', 'mailto:', 'tel:', 'data:', 'javascript:')): continue
        full = urljoin(url, urldefrag(a)[0])
        if urlparse(full).netloc != urlparse(BASE).netloc: continue  # зовнішні не перевіряємо
        st2, _, _ = get(full, 'HEAD')
        if st2 != 200:
            st2, _, _ = get(full)  # деякі CDN не люблять HEAD
        checked += 1
        if st2 != 200: fail(f'{a} -> HTTP {st2}')
    ok(f'локальних ресурсів перевірено: {len(assets)}')
    # специфічні перевірки
    if p == '':
        n = doc.count('class="gallery__item"')
        if n < 1: fail('на головній немає фото в галереї')
        else: ok(f'галерея: {n} фото')
        if 'hero__plane' not in doc: fail('немає моделі в hero')
        if 'GLightbox(' not in doc: fail('лайтбокс не ініціалізовано')
    if p.startswith('navchannya'):
        if 'navchalna-programa-borysfen.pdf' not in doc: fail('немає посилання на PDF програми')
        if doc.count('class="tabs__panel') < 3: fail('менше 3 рівнів навчання')
        m = re.findall(r'<tfoot><tr><td>Разом</td><td>(\d+)</td><td>(\d+)</td><td>(\d+)</td>', doc)
        for tot, th, pr in m:
            if int(th) + int(pr) != int(tot): fail(f'у плані теорія+практика ≠ усього ({th}+{pr}≠{tot})')
        ok(f'рівнів: {doc.count("class=\"tabs__panel")}, суми годин у нормі')
    if p.startswith('batkam'):
        for must in ['Що відбувається під час повітряної тривоги', 'Як підтримати дитину вдома']:
            if must not in doc: fail(f'на сторінці «Батькам» немає розділу «{must}»')
        for mustnot in ['Куди звернутися по допомогу', 'Джерела']:
            if mustnot in doc: fail(f'на сторінці «Батькам» зайвий розділ «{mustnot}»')

# однаковість меню
sets = {p: tuple(m) for p, m in menus.items()}
if len(set(sets.values())) > 1:
    fail('меню відрізняється між сторінками: ' + '; '.join(f'{p or "index"}: {", ".join(m)}' for p, m in menus.items()))
else:
    ok('меню однакове на всіх сторінках: ' + ', '.join(next(iter(menus.values()))))

# PDF
st, ct, body = get(BASE + 'files/navchalna-programa-borysfen.pdf')
if st != 200 or 'pdf' not in ct: fail(f'PDF програми: HTTP {st} {ct}')
elif len(body) < 50_000: fail('PDF програми підозріло малий')
else: ok(f'PDF програми: {len(body)//1024} KB')
# те, чого на сайті бути не має (лише на продакшні; локальний http.server роздає все)
for secret in ([] if LOCAL else ['docs/00-параметри-клубу.md', 'foto/claude.jpg', '.vercel/project.json']):
    st, _, _ = get(BASE + secret, 'HEAD')
    if st == 200: fail(f'на сайт потрапив внутрішній файл: {secret}')
ok('внутрішні файли (docs, foto, .vercel) недоступні')

print(f'\nПеревірок: {checked}. Проблем: {len(problems)}')
sys.exit(1 if problems else 0)
