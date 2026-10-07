"""Full site test. Run from the repo root after `python3 build.py --check`.

Static checks: every built page, internal links, images, JSON-LD, sitemap,
robots, favicons, phone/WhatsApp/email links.
Browser checks (needs `pip install playwright` + Chromium): no horizontal
scroll on phone and desktop, logo animation running, request form builds the
right WhatsApp message and posts the right FormSubmit payload (intercepted,
nothing is sent).
"""
import json, re, sys, threading, functools, http.server, socketserver
from pathlib import Path
from urllib.parse import urlparse, unquote, parse_qs

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "content"))
import site_data as S  # noqa: E402

fails, passes = [], []
def check(ok, msg):
    (passes if ok else fails).append(msg)

pages = sorted(p for p in ROOT.rglob("index.html") if not any(x in p.parts for x in ("src", "tests", ".git")))
pages.append(ROOT / "404.html")
skip_hosts = {"wa.me", "www.google.com", "search.google.com", "www.facebook.com", "fonts.googleapis.com", "fonts.gstatic.com", "images.unsplash.com", "formsubmit.co", "schema.org", "mizantechnical.site", "claude.ai"}

for page in pages:
    html = page.read_text()
    rel = page.relative_to(ROOT)
    refs = [(a, v) for a, v in re.findall(r'(href|src)="([^"]+)"', html)]
    refs += [("srcset", x.strip().split(" ")[0]) for v in re.findall(r'srcset="([^"]+)"', html) for x in v.split(", ")]
    for attr, url in refs:
        u = urlparse(url)
        if u.scheme in ("http", "https"):
            check(u.hostname in skip_hosts, f"{rel}: unexpected external {url}")
            continue
        if u.scheme in ("tel", "mailto") or url.startswith("#") or url.startswith("data:"):
            continue
        target = ((ROOT / unquote(u.path).lstrip("/")) if u.path.startswith("/") else (page.parent / unquote(u.path))).resolve()
        if url.endswith("/") or target.is_dir():
            target = target / "index.html"
        check(target.exists(), f"{rel}: broken {attr} {url}")
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except Exception as ex:
            check(False, f"{rel}: bad JSON-LD {ex}")
    for t in re.findall(r'href="tel:([^"]+)"', html):
        check(t in (S.PHONE, S.PHONE2), f"{rel}: unknown tel {t}")
    for w in re.findall(r'href="https://wa\.me/([0-9]+)', html):
        check(w == S.PHONE.lstrip("+"), f"{rel}: wrong WhatsApp number {w}")
    for m in re.findall(r'href="mailto:([^"]+)"', html):
        check(m == S.EMAIL, f"{rel}: wrong email {m}")
    if page.name == "index.html":
        check(html.count("<h1") == 1, f"{rel}: needs exactly one h1")
        check('rel="canonical"' in html, f"{rel}: canonical")
        check('favicon.svg' in html and 'favicon.ico' in html, f"{rel}: favicon links")
check(not [f for f in fails if "broken" in f], f"internal links and images on {len(pages)} pages")

sm = (ROOT / "sitemap.xml").read_text()
locs = re.findall(r"<loc>(.*?)</loc>", sm)
for loc in locs:
    p = urlparse(loc).path
    check((ROOT / p.lstrip("/") / "index.html").exists() or (ROOT / p.lstrip("/")).is_file(), f"sitemap entry missing page {loc}")
check(len(locs) == len(pages) - 1, f"sitemap lists {len(locs)} of {len(pages)-1} pages")
check("Sitemap: https://mizantechnical.site/sitemap.xml" in (ROOT / "robots.txt").read_text(), "robots.txt points to sitemap")
for f in ("favicon.ico", "favicon.svg", "apple-touch-icon.png", "CNAME", ".nojekyll"):
    check((ROOT / f).exists(), f"{f} present")
check((ROOT / "CNAME").read_text().strip() == "mizantechnical.site", "CNAME is mizantechnical.site")

import xml.dom.minidom
for svg in ROOT.glob("**/*.svg"):
    if "node_modules" in svg.parts or ".git" in svg.parts:
        continue
    try:
        xml.dom.minidom.parse(str(svg)); ok = True
    except Exception:
        ok = False
    check(ok, f"{svg.relative_to(ROOT)} is valid SVG")

# ---------------------------------------------------------------- speed and alt text
for page in pages:
    html = page.read_text()
    rel = page.relative_to(ROOT)
    check("fonts.googleapis.com" not in html, f"{rel}: fonts are self-hosted")
    for img in re.findall(r"<img [^>]*>", html):
        if 'src="data:,"' in img:
            continue  # photo viewer placeholder, filled by script
        alt = re.search(r'alt="([^"]*)"', img)
        check(alt and len(alt.group(1)) >= 8, f"{rel}: descriptive alt text on {img[:80]}")
        if "fetchpriority" not in img and "img/whatsapp-qr" not in img:
            check('loading="lazy"' in img, f"{rel}: below-the-fold image is lazy {img[:80]}")
        if "/img/" in img or 'src="img/' in img or 'src="../img/' in img or 'src="../../img/' in img:
            check('width="' in img and 'height="' in img, f"{rel}: image has width and height {img[:80]}")
    for m in re.finditer(r"<img [^>]*src=\"(?:\.\./)*img/(?:v/)?[\w-]+\.jpg\"", html):
        start = html.rfind("<picture>", 0, m.start())
        check(start != -1 and 'type="image/avif"' in html[start:m.start()], f"{rel}: photo served as AVIF/WebP")
for page in pages[:-1]:
    check('class="qr-code"' in page.read_text() and "M2," in page.read_text(), f"{page.relative_to(ROOT)}: WhatsApp QR code is inline")
check(len((ROOT / "assets/site.min.css").read_text()) < len((ROOT / "assets/site.css").read_text()), "CSS is minified")

# ---------------------------------------------------------------- languages
LANG_DIR = {"ar": "rtl", "ur": "rtl", "hi": "ltr"}
en_home = (ROOT / "index.html").read_text(encoding="utf-8")
for code in ["en"] + list(LANG_DIR):
    check(f'hreflang="{code}"' in en_home, f"home links the {code} version (hreflang)")
check('hreflang="x-default"' in en_home, "home has an x-default hreflang")
for code, d in LANG_DIR.items():
    s = (ROOT / code / "index.html").read_text(encoding="utf-8")
    check(f'<html lang="{code}" dir="{d}">' in s, f"/{code}/ has lang={code} dir={d}")
    check(f'<link rel="canonical" href="https://mizantechnical.site/{code}/">' in s, f"/{code}/ canonical points to itself")
    check(s.count('rel="alternate" hreflang=') == 5, f"/{code}/ carries all hreflang links")
    check("Will Fix It." not in s and "Send a request" not in s, f"/{code}/ headline and form are translated")
    check("+971 52 962 2078" in s and "MTM Group Tech" in s, f"/{code}/ keeps the phone number and brand name")
    check('<option value="CCTV &amp; security">' in s, f"/{code}/ form still sends the English service name")
    check("window.MTM_I18N=" in s, f"/{code}/ chat buttons are translated")
for pg in pages[:-1]:  # 404.html is a bare page
    check('class="langsw"' in pg.read_text(encoding="utf-8"), f"language switcher on {pg.relative_to(ROOT)}")

# ---------------------------------------------------------------- browser
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

if sync_playwright:
    Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}/"
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for name, vp in (("phone", {"width": 375, "height": 800}), ("desktop", {"width": 1280, "height": 900})):
            ctx = b.new_context(viewport=vp)
            ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
            pg = ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            for page in pages:
                path = "/".join(page.relative_to(ROOT).parts[:-1])
                url = base + (path + "/" if path else "") + ("404.html" if page.name == "404.html" else "")
                pg.goto(url)
                sw = pg.evaluate("document.documentElement.scrollWidth")
                check(sw <= vp["width"], f"{name} {url[len(base)-1:]}: no sideways scroll (width {sw})")
            check(not errs, f"{name}: no JavaScript errors {errs[:2]}")
            ctx.close()
        # logo animation + form
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        posted, opened = [], []
        ctx.route("https://formsubmit.co/**", lambda r: (posted.append(r.request), r.fulfill(status=200, body='{"success":"true"}', content_type="application/json")))
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1|formsubmit).*"), lambda r: r.abort())
        pg = ctx.new_page()
        ctx.on("request", lambda r: opened.append(r.url) if "wa.me" in r.url or "whatsapp" in r.url else None)
        pg.goto(base)
        anim = pg.evaluate("getComputedStyle(document.querySelector('.logo-mark .gear g')).animationName")
        check(anim not in ("none", ""), f"logo gear animation running ({anim})")
        pg.fill("#r-name", "Test Customer")
        pg.select_option("#r-svc", index=0)
        pg.fill("#r-phone", "0501234567")
        pg.fill("#r-loc", "Al Barsha 1")
        pg.fill("#r-msg", "Two cameras not recording")
        pg.click("#r-send")
        pg.wait_for_timeout(1500)
        wa = opened[0] if opened else ""
        check(wa.startswith("https://wa.me/971529622078") or "api.whatsapp.com" in wa or "whatsapp" in wa, f"form opens WhatsApp ({wa[:60]})")
        txt = unquote(wa)
        check(all(x in txt for x in ("Test Customer", "0501234567", "Al Barsha 1", "Two cameras")), "WhatsApp message has name, phone, location, problem")
        check(len(posted) == 1 and posted[0].url.endswith("/ajax/" + S.EMAIL), f"form posts once to FormSubmit for {S.EMAIL}")
        if posted:
            body = posted[0].post_data or ""
            check("Test Customer" in body and "0501234567" in body, "FormSubmit payload has the customer details")
        # chat assistant: answers, hand-off summary, size of knowledge base
        kb = json.loads((ROOT / "assets/chat-kb.json").read_text())
        check(len(kb) >= 500, f"chat assistant has {len(kb)} ready answers")
        cases = {"my camera not recording": "recorder stops recording", "breaker keeps tripping": "breaker that keeps tripping",
                 "do you speak hindi": "Hindi", "where are you located": "Al Fahidi", "how much for cctv": "agrees the price",
                 "need cat6 cabling for office": "cat6", "contact me": "WhatsApp", "are you a bot": "automatic assistant"}
        for q, want in cases.items():
            got = pg.evaluate("q=>MTMChat.ask(q).then(e=>e?e.a:'')", q)
            check(want.lower() in got.lower(), f"chat answers '{q}' ({got[:50]})")
        check(pg.evaluate("q=>MTMChat.ask(q).then(e=>!e)", "zzqx blorf") , "chat falls back when it doesn't understand")
        pg.click(".mc-fab"); pg.fill(".mc-form input", "cctv not recording in Deira"); pg.press(".mc-form input", "Enter")
        pg.wait_for_timeout(1200)
        pg.click(".mc-log .mc-chip.wa >> nth=-1"); pg.wait_for_timeout(800)
        last = unquote(opened[-1]) if opened else ""
        check("Service: CCTV" in last and "Area: Deira" in last and "cctv not recording in Deira" in last, "chat hands off to WhatsApp with service, area and messages")
        ctx.close()
        # work carousel on the home page and the gallery viewer
        ctx = b.new_context(viewport={"width": 1280, "height": 900})
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
        pg = ctx.new_page(); pg.goto(base)
        n = pg.locator(".car-track li").count()
        check(n >= 10, f"home carousel shows {n} work photos")
        pg.locator(".car").scroll_into_view_if_needed()
        x0 = pg.evaluate("document.querySelector('.car-track').scrollLeft")
        pg.click(".car-btn.next"); pg.wait_for_timeout(900)
        check(pg.evaluate("document.querySelector('.car-track').scrollLeft") > x0, "carousel next button scrolls")
        stems = pg.eval_on_selector_all(".car-track img", "els=>els.map(e=>e.getAttribute('src'))")
        check(len(stems) == len(set(stems)), "carousel has no duplicate photos")
        pg.goto(base + "gallery/")
        pg.click(".gal figure >> nth=2 >> button"); pg.wait_for_timeout(300)
        check(pg.evaluate("document.getElementById('lb').open"), "gallery photo opens the viewer")
        cap1 = pg.inner_text("#lb p"); pg.click(".lb-next"); pg.wait_for_timeout(200)
        check(pg.inner_text("#lb p") != cap1, "viewer next button moves to another photo")
        pg.keyboard.press("Escape"); pg.click(".gal-filter button >> text=Electrical"); pg.wait_for_timeout(200)
        vis = pg.evaluate("[...document.querySelectorAll('.gal figure')].filter(f=>!f.hidden).map(f=>f.dataset.cat)")
        check(vis and set(vis) == {"Electrical"}, "gallery filter shows only that category")
        ctx.close()
        # phone: languages sit in a dropdown, not an inline bar
        ctx = b.new_context(viewport={"width": 375, "height": 800})
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
        pg = ctx.new_page(); pg.goto(base)
        check(not pg.is_visible(".langwrap .langsw") and pg.is_visible(".langdd summary"), "phone shows the language dropdown instead of the bar")
        pg.click(".langdd summary"); pg.wait_for_timeout(150)
        check(pg.is_visible(".langdd nav a[lang=ar]"), "language dropdown opens with Arabic in it")
        pg.click("h1"); pg.wait_for_timeout(150)
        check(not pg.is_visible(".langdd nav a[lang=ar]"), "language dropdown closes on outside tap")
        ctx.close()
        # Arabic page: translated chat buttons still ask the English question
        ctx = b.new_context(viewport={"width": 375, "height": 800})
        ctx.route(re.compile(r"^https?://(?!127\.0\.0\.1).*"), lambda r: r.abort())
        pg = ctx.new_page()
        pg.goto(base + "ar/"); pg.click(".mc-fab"); pg.wait_for_timeout(500)
        check("اسأل ميزان" in pg.inner_text(".mc-fab") and "مرحبًا" in pg.inner_text(".mc-log"), "Arabic chat greets in Arabic")
        pg.click(".mc-log .mc-chip >> text=كاميرات المراقبة"); pg.wait_for_timeout(1200)
        check("CCTV" in pg.inner_text(".mc-log .mc-msg.bot >> nth=-1"), "Arabic CCTV button gets the CCTV answer")
        ctx.close()
        b.close()
    srv.shutdown()
else:
    print("Note: playwright not installed, browser checks skipped")

print(f"PASS {len(passes)}  FAIL {len(fails)}")
for f in fails:
    print("FAIL:", f)
sys.exit(1 if fails else 0)
