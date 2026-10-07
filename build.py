#!/usr/bin/env python3
"""Builds mizantechnical.site from src/ and content/.

  python3 build.py                 rebuild every page, sitemap.xml and robots.txt
  python3 build.py --publish-next  move the next tips article from content/queue to
                                   content/published (dated today), then rebuild
  python3 build.py --check         rebuild, then run the SEO health check (exit 1 on errors)

The daily GitHub Action (.github/workflows/daily-seo.yml) runs
`--publish-next --check` and commits whatever changed.
"""
import datetime as dt
import hashlib
import html
import json
import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "content"))
import site_data as S  # noqa: E402
import chatbot  # noqa: E402
import i18n  # noqa: E402
from icons import icon  # noqa: E402

TODAY = dt.date.today().isoformat()
OUT = ROOT_DIR
GENERATED = []  # (path, lastmod, priority)
STATE_FILE = ROOT_DIR / "content/.build-state.json"
STATE = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}

e = html.escape
SVC = {s["slug"]: s for s in S.SERVICES}


def rel_root(path):
    depth = path.count("/") - (0 if path.endswith("/") else 0)
    return "../" * (depth - 1) if path != "/" else ""


def url(path):
    return S.DOMAIN + path


def wa_link(text):
    from urllib.parse import quote
    return f"{S.WA}?text={quote(text)}"


# ---------------------------------------------------------------- schema
def business_schema():
    return {
        "@context": "https://schema.org",
        "@type": ["HomeAndConstructionBusiness", "LocalBusiness"],
        "@id": S.DOMAIN + "/#business",
        "name": S.NAME,
        "alternateName": [S.ALT_NAME, "Mizan Technical", S.SLOGAN],
        "logo": S.DOMAIN + "/img/logo-192.png",
        "url": S.DOMAIN + "/",
        "telephone": [S.PHONE, S.PHONE2],
        "email": S.EMAIL,
        "image": S.IMG["panel"],
        "slogan": S.SLOGAN,
        "founder": {"@type": "Person", "name": S.OWNER, "jobTitle": S.OWNER_TITLE, "email": S.EMAIL, "knowsLanguage": S.LANGUAGES, "image": S.DOMAIN + "/img/mizan.jpg"},
        "address": {"@type": "PostalAddress", "streetAddress": S.ADDRESS["street"],
                    "addressLocality": S.ADDRESS["city"], "addressCountry": S.ADDRESS["country"]},
        "hasMap": S.MAPS,
        "knowsLanguage": S.LANGUAGES,
        "areaServed": [{"@type": "City", "name": "Dubai"}, {"@type": "Country", "name": "United Arab Emirates"}]
                      + [{"@type": "Place", "name": a["name"]} for a in S.AREAS],
        "sameAs": [S.FACEBOOK],
        "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["h1"],
                        "url": url(f"/{s['slug']}/")}} for s in S.SERVICES],
    }


def breadcrumb_schema(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)}
                                for i, (n, p) in enumerate(items)]}


def faq_schema(faq):
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q,
                            "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


# ---------------------------------------------------------------- layout
WA_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm4.5 12.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .1-1.3c0-.1-.2-.2-.5-.3Z"/></svg>'
LOGO = '<span class="logo-mark" aria-hidden="true"><svg viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0a2f4f"/><g transform="translate(-2 -3)"><path d="M9 47V15h7.5l5.5 15 5.5-15H35v32h-6.5V31l-4.5 12.5h-4L15.5 31v16z" fill="#ffffff"/><path d="M37 15h19v6.5h-6.2V47h-6.6V21.5H37z" fill="#ffffff"/><g class="gear" transform="translate(49 48)"><g><path d="M8.41,-1.82 L10.86,-1.72 L10.86,1.72 L8.41,1.82 L7.61,4.01 L9.43,5.67 L7.22,8.30 L5.27,6.80 L3.25,7.96 L3.58,10.40 L0.19,11.00 L-0.33,8.59 L-2.63,8.19 L-3.94,10.27 L-6.92,8.55 L-5.78,6.37 L-7.28,4.58 L-9.62,5.33 L-10.80,2.10 L-8.52,1.17 L-8.52,-1.17 L-10.80,-2.10 L-9.62,-5.33 L-7.28,-4.58 L-5.78,-6.37 L-6.92,-8.55 L-3.94,-10.27 L-2.63,-8.19 L-0.33,-8.59 L0.19,-11.00 L3.58,-10.40 L3.25,-7.96 L5.27,-6.80 L7.22,-8.30 L9.43,-5.67 L7.61,-4.01Z" fill="#ffd100" stroke="#0a2f4f" stroke-width="2.4" stroke-linejoin="round"/><circle r="3.6" fill="#0a2f4f"/></g></g></g></svg></span>'
PHONE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2"/></svg>'

SCRIPT = """<script>
(function(){
  var f=document.getElementById('request');
  if(f){
    var send=document.getElementById('r-send');
    var v=function(id){return document.getElementById(id).value.trim()};
    var build=function(){
      var w=f.querySelector('input[name=when]:checked');
      var lines=['Hello Mizan, I need a technician.','','Service: '+v('r-svc'),
        'Location: '+(v('r-loc')||'(I will share my location pin)'),'When: '+(w?w.value:'')];
      if(v('r-msg'))lines.push('Problem: '+v('r-msg'));
      if(v('r-name'))lines.push('Name: '+v('r-name'));
      if(v('r-phone'))lines.push('Phone: '+v('r-phone'));
      send.href='https://wa.me/971529622078?text='+encodeURIComponent(lines.join('\\n'));
    };
    f.addEventListener('input',build);f.addEventListener('change',build);
    f.addEventListener('submit',function(e){e.preventDefault()});build();
    send.addEventListener('click',function(){
      var to=f.getAttribute('data-email');if(!to)return;
      var w=f.querySelector('input[name=when]:checked');
      try{fetch('https://formsubmit.co/ajax/'+to,{method:'POST',keepalive:true,
        headers:{'Content-Type':'application/json','Accept':'application/json'},
        body:JSON.stringify({_subject:'New website request: '+v('r-svc'),_template:'table',_captcha:'false',
          name:v('r-name'),phone:v('r-phone'),service:v('r-svc'),location:v('r-loc'),
          problem:v('r-msg'),when:w?w.value:'',page:location.href})});}catch(err){}
    });
  }
  [].forEach.call(document.querySelectorAll('.car'),function(c){
    var t=c.querySelector('.car-track'),rtl=getComputedStyle(c).direction==='rtl';
    function go(d){t.scrollBy({left:d*(rtl?-1:1)*t.clientWidth*0.9,behavior:'smooth'})}
    c.querySelector('.prev').addEventListener('click',function(){go(-1)});
    c.querySelector('.next').addEventListener('click',function(){go(1)});
  });
  var y=document.getElementById('yr');if(y)y.textContent=new Date().getFullYear();
})();
</script>"""


def lang_switch(r, cur="en"):
    links = [("en", "EN", "English", r or "./")] + [(k, v["short"], v["name"], f"{r}{k}/") for k, v in i18n.LANGS.items()]
    return ('<nav class="langsw" aria-label="Language">' + "".join(
        f'<a href="{h}" hreflang="{k}" lang="{k}" title="{n}"{" aria-current=\"true\"" if k == cur else ""}>{lab}</a>'
        for k, lab, n, h in links) + "</nav>")


def hreflang_links():
    alts = [("en", "/"), ("x-default", "/")] + [(k, f"/{k}/") for k in i18n.LANGS]
    return "\n".join(f'<link rel="alternate" hreflang="{k}" href="{url(p)}">' for k, p in alts)


def layout(path, title, desc, body, schemas=(), og_image=None, priority="0.6", lastmod=TODAY):
    r = rel_root(path)
    home = r or "./"
    nav_prefix = "" if path == "/" else home
    ld = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
                   for s in schemas)
    services_links = "".join(f'<li><a href="{r}{s["slug"]}/">{e(s["short"])}</a></li>' for s in S.SERVICES)
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url(path)}">
{hreflang_links() if path == "/" else ""}
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{e(S.NAME)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url(path)}">
<meta property="og:image" content="{e(og_image or S.IMG['panel'])}">
<meta property="og:locale" content="en_AE">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="AE-DU">
<meta name="geo.placename" content="Dubai">
<meta name="theme-color" content="#0a2f4f">
<link rel="icon" href="{r}favicon.ico" sizes="48x48">
<link rel="icon" href="{r}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="{r}assets/site.css">
{ld}
</head>
<body>
<div class="hazard" aria-hidden="true"></div>
<header class="top">
  <div class="wrap">
    <a class="logo" href="{home}" aria-label="{e(S.NAME)} home">{LOGO}<span><b>Mizan Technical</b><small>{e(S.NAME)} · {e(S.ALT_NAME)}</small></span></a>
    <nav class="nav" aria-label="Main">
      <a href="{nav_prefix}#services">Services</a>
      <a href="{nav_prefix}#areas">Areas</a>
      <a href="{r}gallery/">Work</a>
      <a href="{r}tips/">Tips</a>
      <a href="{nav_prefix}#request">Hire Mizan</a>
    </nav>
    {lang_switch(r)}
    <a class="btn btn-navy" href="tel:{S.PHONE}">{PHONE_ICON}<span>Call Mizan</span></a>
  </div>
</header>

<main id="top">
{body}
</main>

<div class="hazard" aria-hidden="true"></div>
<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a class="logo" href="{home}">{LOGO}<span><b>Mizan Technical</b><small>{e(S.NAME)} · {e(S.ALT_NAME)}</small></span></a>
        <p class="tagline">Professional • Reliable • Affordable. Technical service and maintenance for homes and offices in Dubai and across the UAE.</p>
        <ul style="margin-top:14px">
          <li>Phone / WhatsApp: <strong style="user-select:all">{S.PHONE_PRETTY}</strong></li>
          <li>Second line: <a href="tel:{S.PHONE2}">{S.PHONE2_PRETTY}</a></li>
          <li>Email: <a href="mailto:{S.EMAIL}">{S.EMAIL}</a></li>
          <li>We speak: {" · ".join(S.LANGUAGES)}</li>
          <li>{e(S.ADDRESS['street'])}, Dubai, UAE</li>
        </ul>
        <a class="qr" href="{S.WA}" target="_blank" rel="noopener"><img src="{r}img/whatsapp-qr.svg" alt="QR code to chat with Mizan on WhatsApp" width="96" height="96" loading="lazy"><span>Scan to chat<br>on WhatsApp</span></a>
      </div>
      <div>
        <h4>Services</h4>
        <ul>{services_links}</ul>
      </div>
      <div>
        <h4>Links</h4>
        <ul>
          <li><a href="{r}gallery/">Work gallery</a></li>
          <li><a href="{r}tips/">Tips &amp; guides</a></li>
          <li><a href="{S.MAPS}" target="_blank" rel="noopener">Google Maps</a></li>
          <li><a href="{S.REVIEW}" target="_blank" rel="noopener">Leave a Google review</a></li>
          <li><a href="{S.FACEBOOK}" target="_blank" rel="noopener">Facebook</a></li>
          <li><a href="{S.WA}" target="_blank" rel="noopener">WhatsApp</a></li>
        </ul>
      </div>
    </div>
    <div class="legal"><span>© <span id="yr">2026</span> {e(S.NAME)} · {e(S.ALT_NAME)}</span><span>mizantechnical.site</span></div>
  </div>
</footer>

<nav class="hirebar" aria-label="Quick contact">
  <a class="btn btn-navy" href="tel:{S.PHONE}">Call</a>
  <a class="btn btn-wa" href="{S.WA}" target="_blank" rel="noopener">WhatsApp</a>
</nav>
{SCRIPT}
<script src="{r}assets/chat.js" defer></script>
</body>
</html>
"""
    write(path, page)
    register(path, page, priority, lastmod)


def register(path, page, priority, lastmod=TODAY):
    digest = hashlib.sha1(page.encode()).hexdigest()
    old = STATE.get(path)
    if old and old["hash"] == digest:
        lastmod = old["lastmod"]  # unchanged page keeps its date
    elif old is None and path.startswith("/tips/") and path != "/tips/":
        pass  # article date
    STATE[path] = {"hash": digest, "lastmod": lastmod}
    GENERATED.append((path, lastmod, priority))


def write(path, text):
    f = OUT / (path.strip("/") + "/index.html" if path != "/" else "index.html")
    if path.endswith(".html"):
        f = OUT / path.strip("/")
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- blocks
def crumbs(r, items):
    parts = [f'<a href="{r or "./"}">Home</a>']
    for name, href in items[:-1]:
        parts.append(f'<a href="{href}">{e(name)}</a>')
    parts.append(f'<span aria-current="page">{e(items[-1][0])}</span>')
    return '<nav class="crumbs wrap" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"


def img_src(r, v):
    return v if v.startswith("http") else r + v


def img_abs(v):
    return v if v.startswith("http") else S.DOMAIN + "/" + v


def page_hero(h1, text, image, alt, wa_text):
    return f"""<section class="hero"><div class="wrap"><div class="page-hero">
  <div class="ph"><img src="{image}" alt="{e(alt)}" fetchpriority="high"></div>
  <span class="kicker" style="color:var(--amber)">{e(S.SLOGAN)}</span>
  <h1>{e(h1)}</h1>
  <p>{e(text)}</p>
  <div class="btns">
    <a class="btn btn-wa" href="{wa_link(wa_text)}" target="_blank" rel="noopener">{WA_ICON}WhatsApp Mizan</a>
    <a class="btn btn-white" href="tel:{S.PHONE}">Call {S.PHONE_PRETTY}</a>
  </div>
</div></div></section>"""


def side_card(r, wa_text):
    return f"""<aside class="side">
  <div class="card">
    <span class="kicker">Hire Mizan</span>
    <h3>Send your location and the problem</h3>
    <p>We reply on WhatsApp, agree a time and a price, then come and fix it.</p>
    <a class="btn btn-wa" href="{wa_link(wa_text)}" target="_blank" rel="noopener">{WA_ICON}WhatsApp now</a>
    <a class="btn btn-line" href="tel:{S.PHONE}">Call {S.PHONE_PRETTY}</a>
  </div>
</aside>"""


def directory(r, exclude=None):
    svc = "".join(f'<li><a href="{r}{s["slug"]}/">{e(s["short"])} in Dubai</a></li>'
                  for s in S.SERVICES if s["slug"] != exclude)
    areas = "".join(f'<li><a href="{r}areas/{a["slug"]}/">{e(a["name"])}</a></li>'
                    for a in S.AREAS if a["slug"] != exclude)
    return f"""<section class="sec" id="areas" style="padding-top:0"><div class="wrap dir">
  <div class="card"><span class="kicker">All services</span><h2 style="font-size:clamp(1.8rem,3.4vw,2.4rem)">What we fix</h2><ul class="linklist">{svc}</ul></div>
  <div class="card"><span class="kicker">Areas we cover</span><h2 style="font-size:clamp(1.8rem,3.4vw,2.4rem)">Dubai &amp; across the UAE</h2><ul class="linklist">{areas}</ul></div>
</div></section>"""


def faq_block(faq):
    items = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq)
    return f'<h2>Questions people ask</h2><div class="faq">{items}</div>'


def related_tips(r, service_slug):
    tips = [t for t in published_tips() if t.get("service") == service_slug]
    if not tips:
        return ""
    li = "".join(f'<li><a href="{r}tips/{t["slug"]}/">{e(t["title"])}</a></li>' for t in tips)
    return f"<h2>Helpful guides</h2><ul>{li}</ul>"


# ---------------------------------------------------------------- pages
# ---------------------------------------------------------------- work photos
def picture(r, stem, alt, attrs='loading="lazy"'):
    return (f'<picture><source srcset="{r}img/{stem}.webp" type="image/webp">'
            f'<img src="{r}img/{stem}.jpg" alt="{e(alt)}" {attrs}></picture>')


def carousel(r):
    items = "".join(f'<li><a href="{r}gallery/#{stem}">{picture(r, stem, alt)}<span>{e(cap)}</span></a></li>'
                    for stem, alt, cap, _ in S.GALLERY)
    return f"""      <div class="car">
        <button class="car-btn prev" type="button" aria-label="Previous photos">&#8249;</button>
        <ul class="car-track" tabindex="0" aria-label="Photos of Mizan's work">{items}</ul>
        <button class="car-btn next" type="button" aria-label="Next photos">&#8250;</button>
      </div>
      <p class="car-more"><a class="btn btn-navy" href="{r}gallery/">See all our work</a></p>"""


GALLERY_JS = """<script>
(function(){
  var figs=[].slice.call(document.querySelectorAll('.gal figure')),dlg=document.getElementById('lb'),cur=0;
  [].forEach.call(document.querySelectorAll('.gal-filter button'),function(b){
    b.addEventListener('click',function(){
      [].forEach.call(document.querySelectorAll('.gal-filter button'),function(x){x.setAttribute('aria-pressed',x===b)});
      figs.forEach(function(f){f.hidden=!(b.dataset.cat==='all'||f.dataset.cat===b.dataset.cat)});
    });
  });
  function vis(){return figs.filter(function(f){return !f.hidden})}
  function show(i){var v=vis();if(!v.length)return;cur=(i+v.length)%v.length;
    var f=v[cur],img=f.querySelector('img'),big=dlg.querySelector('img');big.src=img.currentSrc||img.src;big.alt=img.alt;
    dlg.querySelector('p').textContent=f.querySelector('figcaption').textContent;history.replaceState(null,'','#'+f.id);}
  figs.forEach(function(f){f.querySelector('button').addEventListener('click',function(){show(vis().indexOf(f));dlg.showModal();});});
  dlg.querySelector('.lb-x').addEventListener('click',function(){dlg.close()});
  dlg.querySelector('.lb-prev').addEventListener('click',function(){show(cur-1)});
  dlg.querySelector('.lb-next').addEventListener('click',function(){show(cur+1)});
  dlg.addEventListener('click',function(ev){if(ev.target===dlg)dlg.close()});
  dlg.addEventListener('keydown',function(ev){if(ev.key==='ArrowRight')show(cur+1);if(ev.key==='ArrowLeft')show(cur-1)});
  var h=location.hash.slice(1),t=h&&document.getElementById(h);
  if(t&&t.matches('.gal figure')){t.scrollIntoView({block:'center'});t.querySelector('button').focus({preventScroll:true});}
})();
</script>"""


def build_gallery():
    path = "/gallery/"
    r = rel_root(path)
    cats = []
    for g in S.GALLERY:
        if g[3] not in cats:
            cats.append(g[3])
    filters = '<button type="button" data-cat="all" aria-pressed="true">All</button>' + "".join(
        f'<button type="button" data-cat="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in cats)
    figs = "".join(f'<figure id="{stem}" data-cat="{e(cat)}"><button type="button" aria-label="Enlarge: {e(cap)}">'
                   f'{picture(r, stem, alt)}</button><figcaption>{e(cap)}</figcaption></figure>'
                   for stem, alt, cap, cat in S.GALLERY)
    wa = wa_link("Hello Mizan, I saw your work on your website and need a technician. My location: ")
    content = f"""{crumbs(r, [('Our work', path)])}
<section class="sec" style="padding-top:10px"><div class="wrap">
  <div class="head"><div><span class="kicker">Our work</span><h1 style="font-family:var(--display);text-transform:uppercase;font-size:clamp(2.6rem,6vw,4.4rem);font-weight:400">Jobs Mizan has done in Dubai</h1></div>
  <p>Real photos from Mizan's own jobs: network and CCTV cabling, racks, intercoms, access control and electrical boards in offices, shops, villas and warehouses. Tap a photo to see it bigger.</p></div>
  <div class="gal-filter" role="group" aria-label="Filter photos">{filters}</div>
  <div class="gal">{figs}</div>
  <p class="car-more"><a class="btn btn-wa" href="{wa}" target="_blank" rel="noopener">WhatsApp Mizan about your job</a></p>
</div></section>
<dialog id="lb" class="lb" aria-label="Photo viewer"><img src="data:," alt=""><p></p>
  <button type="button" class="lb-prev" aria-label="Previous photo">&#8249;</button><button type="button" class="lb-next" aria-label="Next photo">&#8250;</button>
  <button type="button" class="lb-x" aria-label="Close">&times;</button></dialog>
{directory(r)}
{GALLERY_JS}"""
    layout(path, "Our Work | CCTV, Cabling & Electrical Jobs in Dubai",
           "Photos of real jobs by Mizan and MTM Group Tech in Dubai: network and CCTV cabling, server racks, door intercoms, access control and electrical boards.",
           content, priority="0.7", og_image=S.DOMAIN + "/img/work-rack-dressing.jpg",
           schemas=[breadcrumb_schema([("Home", "/"), ("Our work", path)]),
                    {"@context": "https://schema.org", "@type": "ImageGallery", "name": "MTM Group Tech work in Dubai",
                     "image": [{"@type": "ImageObject", "contentUrl": f"{S.DOMAIN}/img/{g[0]}.jpg", "caption": g[2]} for g in S.GALLERY]}])


def build_home():
    body = (ROOT_DIR / "src/home.html").read_text(encoding="utf-8")
    body = re.sub(r"\{\{ICON:(\w+)\}\}", lambda m: icon(m.group(1)), body)
    body = body.replace("{{ROOT}}", "").replace("{{EMAIL}}", e(S.EMAIL)).replace("{{DIRECTORY}}", directory("")).replace("{{CAROUSEL}}", carousel(""))
    layout("/", "CCTV & Network Cabling in Dubai | Mizan Will Fix It",
           "MTM Group Tech: CCTV installation, network and CCTV cabling, access control, PABX, IT support and electrical work in Dubai. WhatsApp +971 52 962 2078.",
           body, schemas=[business_schema(), {"@context": "https://schema.org", "@type": "WebSite",
                                              "name": S.NAME, "url": S.DOMAIN + "/"}],
           priority="1.0")


def build_service(s):
    path = f"/{s['slug']}/"
    r = rel_root(path)
    wa = f"Hello Mizan, I need {s['short'].lower()} in Dubai. My location: "
    bullets = "".join(f"<li>{e(b)}</li>" for b in s["bullets"])
    body_secs = "".join(f"<h2>{e(h)}</h2><p>{e(p)}</p>" for h, p in s["body"])
    content = f"""{crumbs(r, [(s['short'], path)])}
{page_hero(s['h1'], s['intro'], img_src(r, S.IMG[s['img']]), s['h1'], wa)}
<section class="sec"><div class="wrap split">
  <article class="prose">
    <h2>What we do</h2>
    <ul>{bullets}</ul>
    {body_secs}
    <h2>How to book</h2>
    <p>Send your location and a short description or photo of the job on WhatsApp to {S.PHONE_PRETTY}. We reply, agree a visit time and a price with you, then come and do the work. We cover Bur Dubai, Deira, Al Barsha, Business Bay, Jumeirah and the rest of Dubai, plus Sharjah and other emirates.</p>
    {faq_block(s['faq'])}
    {related_tips(r, s['slug'])}
  </article>
  {side_card(r, wa)}
</div></section>
{directory(r, exclude=s['slug'])}"""
    layout(path, s["title"], s["desc"], content, og_image=img_abs(S.IMG[s["img"]]), priority="0.9",
           schemas=[business_schema(), breadcrumb_schema([("Home", "/"), (s["short"], path)]),
                    {"@context": "https://schema.org", "@type": "Service", "name": s["h1"],
                     "serviceType": s["short"], "description": s["desc"],
                     "provider": {"@id": S.DOMAIN + "/#business"},
                     "areaServed": {"@type": "City", "name": "Dubai"}, "url": url(path)},
                    faq_schema(s["faq"])])


def build_area(a):
    path = f"/areas/{a['slug']}/"
    r = rel_root(path)
    wa = f"Hello Mizan, I need a technician in {a['name']}. The job: "
    cards = "".join(f'<li><a href="{r}{s["slug"]}/">{e(s["short"])} in {e(a["name"])}</a></li>' for s in S.SERVICES)
    content = f"""{crumbs(r, [('Areas', '../../#areas'), (a['name'], path)])}
{page_hero(f"Technician in {a['name']}", a['blurb'], S.IMG['dubai'], f"{a['name']}, Dubai", wa)}
<section class="sec"><div class="wrap split">
  <article class="prose">
    <h2>Services in {e(a['name'])}</h2>
    <p>{e(S.NAME)} sends technicians to homes, shops and offices in {e(a['name'])} for:</p>
    <ul class="linklist">{cards}</ul>
    <h2>Book a visit in {e(a['name'])}</h2>
    <p>Send your exact location pin and what needs fixing on WhatsApp to {S.PHONE_PRETTY}. We confirm the time and the price before we come.</p>
  </article>
  {side_card(r, wa)}
</div></section>
{directory(r, exclude=a['slug'])}"""
    layout(path, f"Technician in {a['name']} | CCTV, Electrical & Repairs",
           f"Need a technician in {a['name']}? CCTV, Wi-Fi, access control, PABX, IT support, electrical and maintenance by MTM Group Tech. WhatsApp {S.PHONE_PRETTY}.",
           content, priority="0.7",
           schemas=[business_schema(), breadcrumb_schema([("Home", "/"), (a["name"], path)])])


def published_tips():
    tips = [json.loads(p.read_text()) for p in sorted((ROOT_DIR / "content/published").glob("*.json"))]
    return sorted(tips, key=lambda t: (t["date"], t["slug"]), reverse=True)


def render_body(blocks):
    out = []
    for kind, text in blocks:
        out.append(f"<{kind}>{e(text)}</{kind}>")
    return "".join(out)


def build_tips():
    tips = published_tips()
    path = "/tips/"
    r = rel_root(path)
    cards = "".join(f'<a class="post" href="{t["slug"]}/"><time datetime="{t["date"]}">{t["date"]}</time>'
                    f'<h3>{e(t["title"])}</h3><p>{e(t["description"])}</p></a>' for t in tips)
    content = f"""{crumbs(r, [('Tips', path)])}
<section class="sec" style="padding-top:10px"><div class="wrap">
  <div class="head"><div><span class="kicker">Tips &amp; guides</span><h1 style="font-family:var(--display);text-transform:uppercase;font-size:clamp(2.6rem,6vw,4.4rem);font-weight:400">Fix-it guides from Mizan</h1></div>
  <p>Practical answers to the problems we see every week in Dubai homes and offices. A new guide is added regularly.</p></div>
  <div class="posts">{cards}</div>
</div></section>
{directory(r)}"""
    layout(path, "Tips & Guides | CCTV, Wi-Fi & Electrical Help in Dubai",
           "Practical guides on CCTV, Wi-Fi, electrical faults and office tech for Dubai homes and businesses, from MTM Group Tech.",
           content, priority="0.6", lastmod=tips[0]["date"] if tips else TODAY,
           schemas=[breadcrumb_schema([("Home", "/"), ("Tips", path)])])
    for t in tips:
        p = f"/tips/{t['slug']}/"
        rr = rel_root(p)
        svc = SVC.get(t.get("service"))
        wa = f"Hello Mizan, I read your guide \"{t['title']}\" and need help. My location: "
        svc_link = (f'<p><strong>Need it fixed?</strong> See our <a href="{rr}{svc["slug"]}/">{e(svc["short"].lower())} service in Dubai</a> or message Mizan on WhatsApp.</p>' if svc else "")
        content = f"""{crumbs(rr, [('Tips', '../'), (t['title'], p)])}
<section class="sec" style="padding-top:10px"><div class="wrap split">
  <article class="prose">
    <time datetime="{t['date']}" style="color:var(--muted)">{t['date']}</time>
    <h1 style="font-family:var(--display);text-transform:uppercase;font-size:clamp(2.2rem,5vw,3.6rem);font-weight:400">{e(t['title'])}</h1>
    {render_body(t['body'])}
    {svc_link}
  </article>
  {side_card(rr, wa)}
</div></section>"""
        layout(p, f"{t['title']} | MTM Group Tech Dubai", t["description"], content, priority="0.5",
               lastmod=t["date"],
               schemas=[{"@context": "https://schema.org", "@type": "Article", "headline": t["title"],
                         "description": t["description"], "datePublished": t["date"], "dateModified": t["date"],
                         "author": {"@type": "Person", "name": S.OWNER},
                         "publisher": {"@id": S.DOMAIN + "/#business"}, "mainEntityOfPage": url(p)},
                        breadcrumb_schema([("Home", "/"), ("Tips", "/tips/"), (t["title"], p)])])


def build_404():
    (OUT / "404.html").write_text(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Page not found | {e(S.NAME)}</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="/assets/site.css"></head><body><main class="wrap" style="padding-block:80px;display:grid;gap:18px">
<h1 style="font-family:Anton,Impact,sans-serif;text-transform:uppercase;font-size:3rem">This page is broken. Mizan can't fix this one.</h1>
<p>But he can fix almost everything else. <a href="/">Go to the home page</a> or WhatsApp <strong>{S.PHONE_PRETTY}</strong>.</p></main><script src="/assets/chat.js" defer></script></body></html>
""", encoding="utf-8")


REL_URL = re.compile(r'((?:href|src)=")(?!https?:|#|tel:|mailto:|data:|/|\./")([^"]*)"')


def build_home_lang(code):
    L = i18n.LANGS[code]
    idx = ["ar", "ur", "hi"].index(code)
    page = (OUT / "index.html").read_text(encoding="utf-8")
    page = page.replace('<html lang="en">', f'<html lang="{code}" dir="{L["dir"]}">', 1)
    page = re.sub(r"<title>.*?</title>", f"<title>{e(L['title'])}</title>", page, count=1)
    page = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*"', lambda m: m.group(1) + e(L["desc"]) + '"', page)
    page = re.sub(r'(<meta property="og:title" content=")[^"]*"', lambda m: m.group(1) + e(L["title"]) + '"', page)
    page = page.replace(f'<link rel="canonical" href="{url("/")}">', f'<link rel="canonical" href="{url("/" + code + "/")}">')
    page = page.replace(f'<meta property="og:url" content="{url("/")}">', f'<meta property="og:url" content="{url("/" + code + "/")}">')
    page = page.replace('content="en_AE"', f'content="{L["locale"]}"')
    # relative links and images move one folder down
    page = REL_URL.sub(lambda m: m.group(1) + "../" + m.group(2) + '"', page)
    page = re.sub(r'srcset="([^"]+)"', lambda m: 'srcset="' + ", ".join(
        x if x.startswith(("http", "/")) else "../" + x for x in m.group(1).split(", ")) + '"', page)
    page = re.sub(r'<nav class="langsw".*?</nav>', lang_switch("../", code), page, count=1, flags=re.S)
    # form options keep the English value so Mizan's WhatsApp message stays readable
    page = re.sub(r"<option>(.*?)</option>", lambda m: f'<option value="{m.group(1)}">{m.group(1)}</option>', page)
    for en in sorted(i18n.T, key=len, reverse=True):
        tr = i18n.T[en][idx]
        x = re.escape(html.escape(en, quote=False))
        page = re.sub(r"(>\s*)" + x + r"(\s*<)", lambda m: m.group(1) + html.escape(tr, quote=False) + m.group(2), page)
        page = re.sub(r'((?:alt|placeholder|aria-label|title)=")' + x + '"', lambda m: m.group(1) + e(tr) + '"', page)
    if L["dir"] == "rtl":  # keep phone numbers reading left to right inside Arabic/Urdu text
        parts = re.split(r"(<script.*?</script>|<head>.*?</head>)", page, flags=re.S)
        page = "".join(x if x.startswith(("<script", "<head>")) else re.sub(
            r">([^<]*)<", lambda m: ">" + re.sub(r"\u200e?(\+971 5\d \d{3} \d{4})", r'<bdi dir="ltr">\1</bdi>', m.group(1)) + "<", x)
            for x in parts)
    font = "Noto+Sans+Arabic:wght@400;500;600;700;800" if L["dir"] == "rtl" else "Hind:wght@400;500;600;700"
    page = page.replace('<link rel="stylesheet" href="../assets/site.css">',
                        f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={font}&display=swap">\n'
                        '<link rel="stylesheet" href="../assets/site.css">', 1)
    chat = dict(i18n.CHAT[code], chips={k: v[idx] for k, v in i18n.CHIPS.items()})
    page = page.replace('<script src="../assets/chat.js" defer></script>',
                        f"<script>window.MTM_I18N={json.dumps(chat, ensure_ascii=False)}</script>\n"
                        '<script src="../assets/chat.js" defer></script>', 1)
    write(f"/{code}/", page)
    register(f"/{code}/", page, "0.9")


def build_sitemap():
    rows = "".join(f"<url><loc>{url(p)}</loc><lastmod>{lm}</lastmod><priority>{pr}</priority></url>\n"
                   for p, lm, pr in GENERATED)
    (OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     f"{rows}</urlset>\n", encoding="utf-8")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {S.DOMAIN}/sitemap.xml\n", encoding="utf-8")


def publish_next():
    queue = sorted((ROOT_DIR / "content/queue").glob("*.json"))
    if not queue:
        print("Queue empty: nothing new to publish today.")
        return
    q = queue[0]
    d = json.loads(q.read_text())
    d["date"] = TODAY
    (ROOT_DIR / "content/published" / q.name).write_text(json.dumps(d, indent=1))
    q.unlink()
    print(f"Published: {d['title']}")


# ---------------------------------------------------------------- SEO check
def seo_check():
    errors, warns = [], []
    pages = [p for p in OUT.rglob("index.html") if ".git" not in p.parts and "node_modules" not in p.parts]
    titles = {}
    for f in pages:
        s = f.read_text(encoding="utf-8")
        name = str(f.relative_to(OUT))
        t = re.search(r"<title>(.*?)</title>", s, re.S)
        d = re.search(r'<meta name="description" content="(.*?)">', s)
        if not t:
            errors.append(f"{name}: missing <title>")
        else:
            tl = len(html.unescape(t.group(1)))
            if tl > 70 or tl < 25:
                warns.append(f"{name}: title is {tl} chars (aim for 25-70)")
            titles.setdefault(t.group(1), []).append(name)
        if not d:
            errors.append(f"{name}: missing meta description")
        else:
            dl = len(html.unescape(d.group(1)))
            if dl > 170 or dl < 70:
                warns.append(f"{name}: description is {dl} chars (aim for 70-170)")
        if len(re.findall(r"<h1[ >]", s)) != 1:
            errors.append(f"{name}: should have exactly one <h1>")
        if 'rel="canonical"' not in s:
            errors.append(f"{name}: missing canonical link")
        for img in re.findall(r"<img [^>]*>", s):
            if 'alt="' not in img:
                errors.append(f"{name}: image without alt text")
        for ld in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                json.loads(ld)
            except ValueError:
                errors.append(f"{name}: invalid JSON-LD")
        for href in re.findall(r'href="([^"#]*?)(?:#[^"]*)?"', s):
            if not href or href.startswith(("http", "tel:", "mailto:", "/")):
                continue
            target = (f.parent / href).resolve()
            if href.endswith("/") or target.is_dir():
                target = target / "index.html"
            if not target.exists():
                errors.append(f"{name}: broken link {href}")
    for t, names in titles.items():
        if len(names) > 1:
            errors.append(f"duplicate title on {', '.join(names)}")
    sm = (OUT / "sitemap.xml").read_text()
    if sm.count("<url>") != len(pages):
        warns.append(f"sitemap lists {sm.count('<url>')} URLs, site has {len(pages)} pages")
    print(f"SEO check: {len(pages)} pages, {len(errors)} errors, {len(warns)} warnings")
    for x in errors:
        print("  ERROR", x)
    for x in warns:
        print("  warn ", x)
    return not errors


def main():
    if "--publish-next" in sys.argv:
        publish_next()
    build_gallery()
    build_home()
    for code in i18n.LANGS:
        build_home_lang(code)
    for s in S.SERVICES:
        build_service(s)
    for a in S.AREAS:
        build_area(a)
    build_tips()
    build_404()
    build_sitemap()
    (ROOT_DIR / "assets/chat-kb.json").write_text(json.dumps(chatbot.build_kb(), ensure_ascii=False, separators=(",", ":")))
    STATE_FILE.write_text(json.dumps(STATE, indent=1, sort_keys=True))
    print(f"Built {len(GENERATED)} pages.")
    if "--check" in sys.argv and not seo_check():
        sys.exit(1)


if __name__ == "__main__":
    main()
