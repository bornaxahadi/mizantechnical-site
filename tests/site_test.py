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
    for attr, url in re.findall(r'(href|src|srcset)="([^"]+)"', html):
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
        b.close()
    srv.shutdown()
else:
    print("Note: playwright not installed, browser checks skipped")

print(f"PASS {len(passes)}  FAIL {len(fails)}")
for f in fails:
    print("FAIL:", f)
sys.exit(1 if fails else 0)
