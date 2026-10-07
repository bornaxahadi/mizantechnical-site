/* Mizan's website assistant.
   Scripted helper: NOT connected to any AI service. It matches what the
   visitor types against ready answers in assets/chat-kb.json (built from the
   site's own content by build.py) and hands the conversation to Mizan on
   WhatsApp or by phone. */
(function () {
  var WA = "971529622078", TEL = "+971529622078";
  var me = document.currentScript;
  var I = window.MTM_I18N || {}, IC = I.chips || {};
  function tr(c) { return IC[c] || c; }
  var ROOT = me && me.src ? new URL("..", me.src).href : "./";
  var KB = window.MTM_KB || null, loading = null;
  var ctx = { svc: "", area: "", said: [] };
  var SVC_NAMES = {
    "cctv-installation-dubai": "CCTV", "structured-cabling-dubai": "Network & CCTV cabling",
    "wifi-networking-dubai": "Wi-Fi & networking", "access-control-biometric-dubai": "Access control & biometric",
    "pabx-intercom-ip-phone-dubai": "PABX, intercom & IP phones", "it-support-computer-repair-dubai": "IT support & computers",
    "electrician-dubai": "Electrical", "sound-system-installation-dubai": "Sound systems",
    "handyman-maintenance-dubai": "Handyman & maintenance"
  };
  var CHIP_SVC = { "CCTV": "cctv", "Cabling": "cabling", "Wi-Fi": "wifi", "Electrical": "electrician",
    "Access control": "access control", "Intercom / PABX": "pabx", "Computer": "computer" };
  var AREAS = ["bur dubai", "al fahidi", "al raffa", "deira", "karama", "al barsha", "barsha", "business bay", "jumeirah",
    "marina", "jlt", "al quoz", "mirdif", "sharjah", "downtown", "jvc", "silicon oasis", "satwa", "mankhool",
    "international city", "discovery gardens", "palm", "arabian ranches", "motor city", "sports city", "nahda", "qusais",
    "muhaisnah", "rashidiya", "oud metha", "tecom", "barsha heights", "al nahda", "ajman", "abu dhabi"];
  var SYN = { "wi-fi": "wifi", "wi fi": "wifi", "e-mail": "email", "camera": "cctv", "cameras": "cctv", "cams": "cctv", "cam": "cctv", "cameraa": "cctv",
    "cctvs": "cctv", "cabling": "cable", "cables": "cable", "prices": "price", "pricing": "price", "costs": "cost",
    "rates": "rate", "fixing": "fix", "fixed": "fix", "repairing": "repair", "repairs": "repair", "installing": "install",
    "installed": "install", "installation": "install", "lights": "light", "sockets": "socket", "speakers": "speaker",
    "computers": "computer", "laptops": "laptop", "routers": "router", "phones": "phone", "telephones": "telephone",
    "tripping": "trip", "trips": "trip", "tripped": "trip", "recording": "record", "records": "record",
    "working": "work", "works": "work", "broke": "broken", "plz": "please", "pls": "please", "u": "you", "ur": "your",
    "fibre": "fiber", "nvr/dvr": "nvr dvr", "cctv-camera": "cctv camera", "cctv camera": "cctv" };
  var STOP = " a an the i im i'm my me mine is are am was be been to for of in on at and or do does did you your can could would will shall please with it its we our us have has had want wanna need needs this that there these those from what whats how there just also some any get got about into by as so if then than very really one ";

  function norm(s) {
    s = (" " + String(s).toLowerCase() + " ").replace(/&/g, " and ").replace(/wi-fi|wi fi/g, "wifi").replace(/[^a-z0-9؀-ۿ ]+/g, " ");
    var out = [];
    s.split(/\s+/).forEach(function (t) {
      if (!t) return;
      t = SYN[t] || t;
      t.split(" ").forEach(function (w) {
        if (w.length > 4 && w.slice(-1) === "s" && w.slice(-2) !== "ss") w = w.slice(0, -1);
        if (STOP.indexOf(" " + w + " ") === -1) out.push(w);
      });
    });
    return out;
  }
  function lev(a, b) {
    if (Math.abs(a.length - b.length) > 2) return 9;
    var p = [], i, j;
    for (j = 0; j <= b.length; j++) p[j] = j;
    for (i = 1; i <= a.length; i++) {
      var prev = p[0]; p[0] = i;
      for (j = 1; j <= b.length; j++) {
        var tmp = p[j];
        p[j] = Math.min(p[j] + 1, p[j - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
        prev = tmp;
      }
    }
    return p[b.length];
  }
  function has(tokens, w) {
    for (var i = 0; i < tokens.length; i++) {
      var t = tokens[i];
      if (t === w) return true;
      var L = Math.min(t.length, w.length);
      if (L >= 6 && lev(t, w) <= (L >= 9 ? 2 : 1)) return true;
    }
    return false;
  }
  var IDF = {}, GREET = " hello hi hey hii salam assalamualaikum good morning evening afternoon dear sir bro brother ";
  function prep() {
    var df = {};
    KB.forEach(function (e) {
      e._p = e.k.map(norm).filter(function (p) { return p.length; });
      var seen = {};
      e._p.forEach(function (p) { p.forEach(function (w) { seen[w] = 1; }); });
      e._t = Object.keys(seen);
      e._t.forEach(function (w) { df[w] = (df[w] || 0) + 1; });
    });
    Object.keys(df).forEach(function (w) { IDF[w] = Math.log(1 + KB.length / df[w]); });
  }
  function best(text) {
    var tk = norm(text), top = null, topScore = 0;
    var rest = tk.filter(function (w) { return GREET.indexOf(" " + w + " ") === -1; });
    if (rest.length && rest.length < tk.length) tk = rest;
    if (!tk.length) return null;
    KB.forEach(function (e) {
      var ph = 0;
      e._p.forEach(function (p) {
        var full = 0, got = 0, m = 0;
        p.forEach(function (w) { var x = IDF[w] || 1; full += x; if (has(tk, w)) { got += x; m++; } });
        var s = m === p.length ? full + (p.length > 1 ? 1 : 0) : (p.length >= 3 && m >= p.length - 1 && m >= 2 ? got * 0.7 : 0);
        if (s > ph) ph = s;
      });
      if (!ph) return;
      var cov = 0;
      tk.forEach(function (w) { if (has(e._t, w)) cov += IDF[w] || 1; });
      var sc = ph + 0.5 * cov;
      if (e.s && e.s === ctx.svc) sc += 0.6;
      if (e.p) sc += 1.5;
      if (e.g && tk.length > 1) sc *= 0.4;
      if (sc > topScore) { topScore = sc; top = e; }
    });
    return topScore >= 1.5 ? top : null;
  }
  function detectArea(text) {
    var t = " " + String(text).toLowerCase() + " ";
    for (var i = 0; i < AREAS.length; i++) if (t.indexOf(AREAS[i]) !== -1) return AREAS[i].replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return "";
  }
  function waText() {
    var l = ["Hello Mizan, I'm contacting you from your website chat."];
    if (ctx.svc) l.push("Service: " + SVC_NAMES[ctx.svc]);
    if (ctx.area) l.push("Area: " + ctx.area);
    if (ctx.said.length) { l.push("", "My messages:"); ctx.said.slice(-6).forEach(function (s) { l.push("- " + s); }); }
    else l.push("", "I need a technician. My location: ");
    return l.join("\n");
  }
  function waLink() { return "https://wa.me/" + WA + "?text=" + encodeURIComponent(waText()); }

  /* ---------------------------------------------------------------- UI */
  var box, log, input, fab;
  function el(tag, cls, html) { var x = document.createElement(tag); if (cls) x.className = cls; if (html != null) x.innerHTML = html; return x; }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function scroll() { log.scrollTop = log.scrollHeight; }
  function say(who, html) { var m = el("div", "mc-msg " + who, html); log.appendChild(m); scroll(); return m; }
  function chips(list) {
    if (!list || !list.length) return;
    var row = el("div", "mc-chips");
    list.forEach(function (c) {
      var b = el("button", "mc-chip", esc(tr(c))); b.type = "button";
      if (c === "Send to WhatsApp" || c === "Get a quote on WhatsApp") b.className += " wa";
      b.addEventListener("click", function () { chip(c); });
      row.appendChild(b);
    });
    log.appendChild(row); scroll();
  }
  function handoff(note) {
    var m = say("bot", esc(note || "Here's everything from this chat, ready to send:") +
      '<div class="mc-hand"><a class="mc-wa" target="_blank" rel="noopener" href="' + waLink() + '">' + esc(I.wa || "Send to Mizan on WhatsApp") + '</a>' +
      '<a class="mc-call" href="tel:' + TEL + '">' + esc(I.call || "Call") + ' +971 52 962 2078</a></div>');
    return m;
  }
  function chip(c) {
    if (c === "Send to WhatsApp" || c === "Get a quote on WhatsApp") { say("me", esc(tr(c))); window.open(waLink(), "_blank", "noopener"); handoff("Opening WhatsApp with your messages filled in. If it didn't open, use these buttons:"); return; }
    if (c === "Call Mizan") { location.href = "tel:" + TEL; return; }
    if (c === "Tips") { location.href = ROOT + "tips/"; return; }
    if (c === "Price") return ask("how much " + (ctx.svc ? SVC_NAMES[ctx.svc] : ""), tr(c));
    if (c === "Book a visit") return ask("book " + (ctx.svc ? SVC_NAMES[ctx.svc] : "visit"), tr(c));
    if (CHIP_SVC[c]) return ask(CHIP_SVC[c], tr(c));
    ask(c, tr(c));
  }
  function answer(text) {
    var a = detectArea(text); if (a) ctx.area = a;
    var e = best(text);
    if (!e) {
      say("bot", "I'm not sure I understood that. I'm an automatic assistant with ready answers, so Mizan can answer better himself. Pick a topic or send this chat to him:");
      chips(["CCTV", "Cabling", "Wi-Fi", "Electrical", "Send to WhatsApp"]);
      return;
    }
    if (e.s) ctx.svc = e.s;
    var html = esc(e.a);
    if (e.l) html += '<a class="mc-more" href="' + ROOT + e.l.replace(/^\//, "") + '">More about this →</a>';
    say("bot", html);
    chips(e.c);
  }
  function ask(text, shown) {
    text = String(text).trim(); if (!text) return;
    say("me", esc(shown || text));
    if (!shown || shown === text) ctx.said.push(text.slice(0, 160));
    var t = say("bot mc-typing", "<i></i><i></i><i></i>");
    ensure().then(function () {
      setTimeout(function () { t.remove(); answer(text); }, 450);
    });
  }
  function ensure() {
    if (KB) { if (!KB[0]._p) prep(); return Promise.resolve(); }
    if (!loading) loading = fetch(ROOT + "assets/chat-kb.json").then(function (r) { return r.json(); }).then(function (d) { KB = d; prep(); })
      .catch(function () { KB = [{ k: ["x"], a: "Sorry, the assistant couldn't load. Please WhatsApp Mizan on +971 52 962 2078.", s: "", c: ["Send to WhatsApp"], l: "" }]; prep(); });
    return loading;
  }
  function open() {
    box.hidden = false; fab.setAttribute("aria-expanded", "true"); document.body.classList.add("mc-open");
    if (!log.childNodes.length) {
      say("bot", esc(I.hello || "Hi! I'm Mizan's website assistant. I can answer questions about his services, areas and how to book. What do you need fixed?"));
      chips(["I have a problem", "Contact me", "CCTV", "Cabling", "Price", "Areas covered"]);
    }
    ensure();
    setTimeout(function () { input.focus(); }, 50);
  }
  function close() { box.hidden = true; fab.setAttribute("aria-expanded", "false"); document.body.classList.remove("mc-open"); fab.focus(); }
  function mount() {
    var logo = document.querySelector(".logo-mark");
    fab = el("button", "mc-fab", (logo ? logo.outerHTML : "") + "<span>" + esc(I.fab || "Ask Mizan") + "</span>");
    fab.type = "button"; fab.setAttribute("aria-label", "Open chat assistant"); fab.setAttribute("aria-expanded", "false"); fab.setAttribute("aria-controls", "mc-box");
    box = el("section", "mc-box");
    box.id = "mc-box"; box.hidden = true; box.setAttribute("role", "dialog"); box.setAttribute("aria-label", "Chat with Mizan's assistant");
    box.innerHTML = '<header class="mc-head">' + (logo ? logo.outerHTML : "") +
      '<div><b>' + esc(I.title || "Mizan Assistant") + '</b><small>' + esc(I.sub || "Automatic helper · instant answers") + '</small></div>' +
      '<button type="button" class="mc-x" aria-label="Close chat">×</button></header>' +
      '<div class="mc-log" aria-live="polite"></div>' +
      '<form class="mc-form"><input type="text" placeholder="' + esc(I.ph || "Type your question…") + '" aria-label="Your question" maxlength="300" autocomplete="off">' +
      '<button type="submit" aria-label="Send">➤</button></form>' +
      (I.note ? '<p class="mc-note"><a target="_blank" rel="noopener" href="https://wa.me/' + WA + '">' + esc(I.note) + '</a></p>' :
      '<p class="mc-note">Automatic assistant, not a live person. <a target="_blank" rel="noopener" href="https://wa.me/' + WA + '">WhatsApp Mizan</a> for a real reply.</p>');
    document.body.appendChild(box); document.body.appendChild(fab);
    log = box.querySelector(".mc-log"); input = box.querySelector("input");
    box.querySelector(".mc-wa, .mc-note a").addEventListener("click", function (ev) { ev.currentTarget.href = waLink(); });
    fab.addEventListener("click", function () { box.hidden ? open() : close(); });
    box.querySelector(".mc-x").addEventListener("click", close);
    box.addEventListener("keydown", function (ev) { if (ev.key === "Escape") close(); });
    box.querySelector("form").addEventListener("submit", function (ev) { ev.preventDefault(); var v = input.value; input.value = ""; ask(v); });
  }
  window.MTMChat = { ask: function (t) { return ensure().then(function () { return best(t); }); }, norm: norm };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount); else mount();
})();
