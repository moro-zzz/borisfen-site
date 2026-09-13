# -*- coding: utf-8 -*-
"""Сторінка «Наші моделі»: генерує modeli.html з tools/models.json.
Фото беруться з галереї: "photo": "розділ/імʼя-файлу" без розширення -> img/gallery/<розділ>/<імʼя>.jpg
Запуск з папки aeroclub-site: python tools/build_models.py"""
import json, re, io, sys, html, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

models = json.load(open('tools/models.json', encoding='utf-8'))
# ті, що літають, першими; далі «у майстерні», потім проєкти
ORDER = {'літає': 0, 'літають': 0, 'у майстерні': 1, 'проєкт у роботі': 2}
models.sort(key=lambda m: ORDER.get(m.get('status', '').lower(), 3))
idx = open('index.html', encoding='utf-8').read()
LOGO = re.search(r'<svg class="logo__mark".*?</svg>', idx, re.S).group(0)
NAV = re.search(r'<nav class="nav".*?</nav>', idx, re.S).group(0)
NAV = re.sub(r' is-active', '', NAV).replace('href="#', 'href="index.html#')
NAV = NAV.replace('<a href="modeli.html" class="nav__link">', '<a href="modeli.html" class="nav__link is-active">')
e = lambda s: html.escape(s, quote=True)

def card(m):
    photo = f'img/gallery/{m["photo"]}.jpg' if m.get('photo') else None
    thumb = f'img/gallery/{m["photo"]}-thumb.jpg' if m.get('photo') else None
    if not photo or not os.path.exists(photo):
        media = '<div class="model__nophoto"><span>Фото зʼявиться після першого польоту</span></div>'
    else:
        media = f'<a href="{photo}" class="model__photo glightbox" data-gallery="models" data-glightbox="title: {e(m["name"])}"><img src="{photo}" alt="{e(m["name"])}" loading="lazy"></a>'
    specs = ''.join(f'<tr><th>{e(k)}</th><td>{e(v)}</td></tr>' for k, v in m.get('specs', []))
    equipment = ''.join(f'<li>{e(t)}</li>' for t in m.get('equipment', []))
    files = ''.join(f'<li><a href="{e(f["url"])}" target="_blank" rel="noopener">{e(f["label"])}</a></li>' for f in m.get('files', []))
    return f'''
    <article class="model" id="{m["id"]}">
      <div class="model__media">{media}</div>
      <div class="model__body">
        <p class="model__type">{e(m["type"])} · <span class="model__status">{e(m["status"])}</span></p>
        <h2 class="model__name">{e(m["name"])}</h2>
        <p class="model__summary">{e(m["summary"])}</p>
        {f'<table class="model__specs"><tbody>{specs}</tbody></table>' if specs else ''}
        {f'<h3>Комплектація</h3><ul class="ticks">{equipment}</ul>' if equipment else ''}
        {f'<h3>Історія прототипу</h3><p class="model__history">{e(m["history"])}</p>' if m.get('history') else ''}
        {f'<h3>Файли</h3><ul class="model__files">{files}</ul>' if files else ''}
        {f'<p class="small">{e(m["credit"])}</p>' if m.get('credit') else ''}
      </div>
    </article>'''

toc = ''.join(f'<a href="#{m["id"]}" class="models__chip">{e(m["name"])}</a>' for m in models)

page = f'''<!DOCTYPE html>
<html lang="uk">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Наші моделі — Борисфен</title>
  <meta name="description" content="Моделі авіамодельного клубу «Борисфен»: тренери, пілотажні, копії. Характеристики, комплектація, креслення.">
  <link rel="icon" type="image/svg+xml" href="img/logo-mark.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/glightbox/3.3.0/css/glightbox.min.css">
  <link rel="stylesheet" href="style.css?v=202609132153">
  <script defer src="/_vercel/insights/script.js"></script>
</head>
<body class="page">

  <header class="header">
    <div class="container header__inner">
      <a href="index.html" class="logo" aria-label="Борисфен, на головну">
        {LOGO}
        <span class="logo__text">БОРИС<span>ФЕН</span></span>
      </a>
      {NAV}
      <button class="burger" aria-label="Відкрити меню" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </header>

  <section class="page-hero">
    <div class="container">
      <p class="page-hero__kicker">Наші моделі</p>
      <h1 class="page-hero__title">Що літає в клубі</h1>
      <p class="page-hero__lead">Тренери, пілотажні моделі, копії та експерименти: характеристики, комплектація і файли для тих, хто хоче повторити. Список поповнюється з кожною новою моделлю в майстерні.</p>
      <div class="models__chips">{toc}</div>
    </div>
  </section>

  <main class="container prose models">
    {''.join(card(m) for m in models)}

    <section class="cta">
      <h2>Хочете побудувати свою?</h2>
      <p>На початковому рівні кожен збирає тренувальну модель під керівництвом інструктора, а далі обирає власний проєкт.</p>
      <a href="navchannya.html" class="btn">Навчальна програма</a>
    </section>
  </main>

  <footer class="footer">
    <div class="container footer__inner">
      <span>© Авіамодельний клуб «Борисфен»</span>
      <a href="index.html">На головну</a>
    </div>
  </footer>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/glightbox/3.3.0/js/glightbox.min.js"></script>
  <script>
    GLightbox({{ selector: '.glightbox', touchNavigation: true, loop: true }});
    (function () {{
      const burger = document.querySelector('.burger'), nav = document.querySelector('.nav');
      if (!burger || !nav) return;
      const toggle = (open) => {{ nav.classList.toggle('is-open', open); burger.classList.toggle('is-open', open); burger.setAttribute('aria-expanded', open); document.body.classList.toggle('menu-open', open); }};
      burger.addEventListener('click', () => toggle(!nav.classList.contains('is-open')));
      nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => toggle(false)));
      document.addEventListener('keydown', e => {{ if (e.key === 'Escape') toggle(false); }});
    }})();
  </script>
</body>
</html>
'''
open('modeli.html', 'w', encoding='utf-8').write(page)
print(f'ok: modeli.html, {len(models)} моделей')
