"""Knowledge base for the website chat assistant.

The assistant is NOT connected to any AI service. It is a scripted helper that
matches what a visitor types against the ready answers below, all built from
the site's own content (site_data.py and the published tips). Keep answers
factual: no prices, opening hours, warranties or response times unless the
owner confirms them.

`build_kb()` returns a list of entries: {"k": [keyword phrases], "a": answer,
"s": service slug or "", "c": quick-reply chips, "l": link path or ""}.
"""
import json
from pathlib import Path

import site_data as S

ASK = "Send your location and a photo of the job on WhatsApp and Mizan will confirm the visit and the price."

# Short spoken names visitors use for each service, plus typical problems.
SVC = {
    "cctv-installation-dubai": {
        "names": ["cctv", "camera", "security camera", "surveillance", "ip camera", "nvr", "dvr", "hikvision", "dahua"],
        "problems": [
            (["camera no picture", "cctv no video", "camera black screen", "no signal camera"], "A camera with no picture is usually a power, cable or connector fault, sometimes the camera itself. Mizan checks the power supply, cable and recorder channel and replaces only what is faulty."),
            (["cctv not recording", "dvr not recording", "nvr not recording", "no recording"], "When a recorder stops recording it is usually the hard disk (full, failed or not formatted) or the recording schedule. Mizan can check the disk health and settings and get it recording again."),
            (["hard disk full", "hdd error", "disk error", "recorder beeping", "dvr beeping"], "Beeping and disk errors usually mean the hard disk failed, is missing or is not set to overwrite. Send a photo of the error on the recorder screen and Mizan will tell you what is needed."),
            (["cctv app not working", "camera offline phone", "cannot see camera on phone", "remote view not working", "mobile view"], "If the app says the device is offline, the recorder has usually lost its internet connection, often after a router change. Mizan can reconnect it and set up the app again on your phone."),
            (["forgot dvr password", "nvr password reset", "camera password forgot"], "Forgotten recorder passwords can usually be reset with the right procedure for the brand. Send a photo of the recorder label on WhatsApp and Mizan will advise."),
            (["night vision", "night vision not working", "camera dark at night", "ir not working"], "Dark night images usually mean the infrared lights have failed, the camera is dirty or it faces a reflective surface. Mizan can clean, adjust or replace the camera."),
            (["camera blurry", "cctv blurry", "camera foggy"], "Blurry pictures are often a dirty or fogged lens, wrong focus, or moisture inside the housing. A cleaning and refocus usually fixes it."),
            (["add more cameras", "extra camera", "upgrade cctv", "replace old cameras"], "Yes. Mizan can add cameras to your existing system or upgrade old analog cameras to HD or IP, using your recorder where it is compatible."),
            (["camera for shop", "cctv for shop", "cctv for store", "cctv for restaurant"], "For shops Mizan usually covers the entrance, cash counter, stock area and back door, and sets up live view on your phone."),
            (["camera for villa", "cctv for home", "cctv for house", "cctv for apartment", "home camera"], "For homes Mizan usually covers the main gate, entrances and parking, with night vision and live view on your phone."),
            (["cctv for warehouse", "cctv for factory", "cctv for office"], "Warehouses and offices need wide coverage of entries, loading areas and stock. Mizan plans camera positions with you before quoting."),
            (["how long recording kept", "footage stored days", "how many days recording"], "It depends on the hard disk size, number of cameras and quality. Mizan sizes the disk for the number of days you need, for example two weeks or a month."),
            (["wifi camera", "wireless camera", "wired or wireless camera"], "Wired cameras are the most reliable and are Mizan's first choice. Wi-Fi cameras are fine where a cable cannot reach, if the signal there is strong."),
        ],
    },
    "structured-cabling-dubai": {
        "names": ["cabling", "structured cabling", "cable", "network cable", "cat6", "cat6a", "lan cable", "data cable", "utp", "fibre", "fiber", "patch panel", "rack", "data point"],
        "problems": [
            (["new office cabling", "cable new office", "fit out cabling", "office fit-out"], "For a new office Mizan plans every data point, runs Cat6 in conduit or trunking back to one rack, terminates on a patch panel, then tests and labels each run."),
            (["messy cables", "rack is a mess", "tidy rack", "cable management"], "Mizan traces, tests, labels and tidies messy racks so your network and cameras are easier to look after."),
            (["data point not working", "network point dead", "lan port not working", "ethernet socket not working"], "A dead data point is usually a loose termination or damaged cable. Mizan tests the run and re-terminates or replaces it."),
            (["cable testing", "test network cables", "cable certification"], "Every cable run Mizan installs is tested and labelled at both ends before the job is finished."),
            (["fibre between floors", "fiber optic", "fibre backbone"], "Yes, Mizan does fibre optic cabling between floors and buildings, where Cat6 runs would be too long."),
            (["cctv cable", "camera cabling", "poe cable"], "Mizan runs CCTV cabling for IP (PoE) and HD analog cameras, with sealed outdoor joints and proper connectors."),
        ],
    },
    "wifi-networking-dubai": {
        "names": ["wifi", "wi-fi", "internet", "router", "network", "mesh", "access point", "switch", "vlan", "vpn", "lan", "wan"],
        "problems": [
            (["weak wifi", "wifi not reaching", "no wifi upstairs", "wifi dead zone", "wifi signal bad"], "Weak Wi-Fi in villas and big apartments usually needs a cabled access point or a mesh system, not a stronger router. Mizan can check the coverage and fix it."),
            (["slow internet", "internet very slow", "wifi slow"], "Slow internet can be the line, the router, Wi-Fi interference or too many devices. Mizan checks each one and fixes what is within the home or office network."),
            (["no internet", "internet not working", "router not working", "router lights red"], "If the provider's line is working, router settings, cables or a faulty switch are common causes. Mizan can troubleshoot and reconfigure it."),
            (["router setup", "configure router", "new router"], "Yes, Mizan sets up routers, switches and Wi-Fi, including passwords, guest networks and connecting CCTV and printers."),
            (["guest wifi", "separate network", "vlan setup"], "Mizan can set up a separate guest Wi-Fi or VLANs so visitors are kept off your office computers, printers and CCTV."),
            (["vpn setup", "vpn", "vpn for office", "remote access office", "work from home access"], "Mizan sets up and troubleshoots VPNs so you can reach the office network securely from outside."),
        ],
    },
    "access-control-biometric-dubai": {
        "names": ["access control", "biometric", "fingerprint", "face recognition", "door access", "card access", "keypad", "magnetic lock", "maglock", "time attendance", "attendance machine", "zkteco"],
        "problems": [
            (["fingerprint not reading", "fingerprint not working", "biometric not working"], "Fingerprint readers often fail from dirty sensors, worn fingerprints or lost settings. Mizan can clean, re-enrol users or repair the reader."),
            (["door not opening card", "access card not working", "keypad not working"], "Card and keypad problems are usually the reader, the lock power supply or the programming. Mizan can test and fix each part."),
            (["magnetic lock not holding", "door lock not working", "maglock problem"], "A magnetic lock that will not hold usually has a power or alignment issue. Mizan checks the lock, plate and power supply."),
            (["attendance report", "time attendance report", "attendance software"], "Mizan installs time-attendance systems and helps with reports and software setup."),
            (["add new employee fingerprint", "enrol users", "delete user access"], "Mizan can enrol new users, remove old ones and re-program existing access systems."),
        ],
    },
    "pabx-intercom-ip-phone-dubai": {
        "names": ["pabx", "pbx", "telephone system", "ip phone", "voip", "intercom", "video intercom", "door phone", "extension", "telephone"],
        "problems": [
            (["extension not working", "phone extension dead", "no dial tone"], "A dead extension is usually wiring, a port on the PABX or the handset. Mizan finds the fault and fixes it."),
            (["intercom not ringing", "door bell intercom not working", "video intercom no picture"], "Intercom faults are usually wiring, the power supply or the outdoor station. Mizan can repair or replace the faulty part."),
            (["ip phone not registering", "voip not working", "sip phone problem"], "IP phones that will not register usually have network or account settings problems. Mizan can configure them."),
            (["move extensions", "add extension", "new phone line office"], "Mizan wires and programs new extensions and moves existing ones."),
            (["gate intercom", "villa intercom"], "Yes, Mizan installs gate and villa intercoms, including the outdoor station at the gate and indoor screens."),
        ],
    },
    "it-support-computer-repair-dubai": {
        "names": ["computer", "laptop", "pc", "it support", "printer", "scanner", "email", "virus", "windows", "software", "server"],
        "problems": [
            (["computer slow", "laptop slow", "pc very slow"], "Slow computers usually need a clean-up, updates, a virus check or sometimes an SSD upgrade. Mizan can check it on site or remotely."),
            (["virus", "virus on pc", "computer virus", "laptop virus", "malware", "pop ups"], "Mizan can remove viruses and unwanted software and set up protection."),
            (["laptop not turning on", "computer not booting", "pc not starting"], "A computer that will not start can be power, storage or Windows problems. Mizan can diagnose it and tell you whether repair is worth it."),
            (["printer not printing", "printer offline", "scanner setup"], "Mizan sets up printers and scanners on the network and fixes printers that show offline."),
            (["email setup", "outlook not working", "email not working"], "Mizan sets up email on computers and phones and fixes common Outlook problems."),
            (["shared folder", "file sharing office", "nas"], "Mizan can set up shared folders and office file sharing over the network."),
            (["remote support", "remote help", "anydesk", "teamviewer"], "Yes, many IT problems can be fixed remotely. Message Mizan on WhatsApp to arrange remote support."),
        ],
    },
    "electrician-dubai": {
        "names": ["electrician", "electrical", "electric", "socket", "switch", "light", "breaker", "db", "distribution board", "wiring", "power", "fan"],
        "problems": [
            (["breaker keeps tripping", "mcb tripping", "power trips", "elcb tripping", "rcd tripping"], "A breaker that keeps tripping usually points to an overloaded circuit, a faulty appliance or moisture. Switch off and unplug, then let Mizan find the cause safely."),
            (["socket not working", "power point dead", "no power socket"], "A dead socket can be a tripped breaker, a loose connection or a burnt socket. Mizan can test and replace it."),
            (["light flickering", "lights flicker"], "Flickering lights are often a loose connection, a failing driver or an incompatible dimmer. Mizan can find and fix it."),
            (["burning smell", "socket burning", "sparks"], "A burning smell or sparks is a safety risk. Switch off the circuit at the breaker and call Mizan on +971 52 962 2078."),
            (["install light", "new light fitting", "chandelier", "fan installation"], "Yes, Mizan installs light fittings, chandeliers and fans."),
            (["new socket", "add power point", "extra socket"], "Mizan can add new power points and the wiring for them."),
            (["no power", "power cut whole house", "half house no power"], "If part of the house has no power, check the breakers in the DB first. If nothing has tripped or it trips again, call Mizan."),
        ],
    },
    "sound-system-installation-dubai": {
        "names": ["sound system", "speaker", "speakers", "amplifier", "pa system", "microphone", "background music", "audio"],
        "problems": [
            (["no sound speakers", "speaker not working", "sound system not working"], "No sound is often a cable, amplifier setting or a failed speaker. Mizan can test and repair existing sound systems."),
            (["humming speakers", "noise in speakers", "buzzing sound"], "Hum and buzz are usually grounding or cable problems. Mizan can trace and fix it."),
            (["music for shop", "background music restaurant", "cafe speakers"], "Mizan installs background music for shops, cafes and restaurants, with ceiling or wall speakers and an amplifier."),
            (["meeting room microphone", "conference audio", "hall microphone"], "Yes, Mizan installs microphones and sound for halls and meeting rooms."),
            (["announcement system", "paging system"], "Mizan installs PA and announcement systems for offices, warehouses and shops."),
        ],
    },
    "handyman-maintenance-dubai": {
        "names": ["handyman", "maintenance", "repair", "fix", "mounting", "tv mounting", "shelf", "curtain", "drill", "annual maintenance", "amc"],
        "problems": [
            (["tv mounting", "mount tv", "hang tv", "tv on wall"], "Yes, Mizan mounts TVs, shelves and fixtures."),
            (["move in", "move out", "before moving", "handover fixes"], "Mizan handles the small fixes before moving in or out, all in one visit where possible."),
            (["regular maintenance", "maintenance contract", "monthly maintenance", "annual maintenance contract"], "Mizan offers regular maintenance visits for homes, shops and offices. Message him to agree what is covered and how often."),
            (["many small jobs", "list of jobs", "several repairs"], "Send the list of jobs on WhatsApp with photos. Mizan can often do them in one visit."),
            (["hang curtains", "curtain rod", "install shelf", "drill wall"], "Yes, fitting and mounting jobs like curtain rods, shelves and fixtures are part of the handyman service."),
        ],
    },
}

GENERAL = [
    (["hi", "hello", "hey", "salam", "assalamualaikum", "good morning", "good evening", "hii"], "Hello! I'm Mizan's website assistant. Tell me what needs fixing, or tap one of the options below.", ["I have a problem", "Contact me", "CCTV", "Cabling"]),
    (["thank you", "thanks", "thx", "shukran", "great thanks"], "You're welcome! When you're ready, message Mizan on WhatsApp and he'll take it from there.", ["Contact me"]),
    (["bye", "goodbye", "see you", "ok bye"], "Goodbye! Mizan is one message away on WhatsApp at +971 52 962 2078.", []),
    (["who are you", "are you a bot", "are you human", "are you real", "is this ai", "chatgpt"], "I'm an automatic assistant on this website with ready answers about Mizan's services. I'm not a live person. For a real answer, tap WhatsApp and Mizan replies himself.", ["Contact me"]),
    (["i have a problem", "something broken", "need help", "help me", "not working", "broken", "fault", "issue", "problem"], "Sorry to hear that. What kind of problem is it? Pick one below, or describe it in your own words.", ["CCTV", "Cabling", "Wi-Fi", "Electrical", "Access control", "Intercom / PABX", "Computer", "Something else"]),
    (["contact me", "call me", "call me back", "callback", "contact", "talk to mizan", "speak to someone", "real person", "human"], "Sure. Tap \"Send to Mizan on WhatsApp\" below and your messages from this chat go with it, so you don't have to repeat yourself. You can also call +971 52 962 2078.", ["Send to WhatsApp", "Call Mizan"]),
    (["phone number", "your number", "mobile number", "call number", "telephone number"], "Call or WhatsApp Mizan on +971 52 962 2078. His second line is +971 52 629 2564.", ["Call Mizan", "Send to WhatsApp"]),
    (["whatsapp", "whatsapp number", "message on whatsapp"], "WhatsApp Mizan on +971 52 962 2078. A photo of the problem and your location pin help him come prepared.", ["Send to WhatsApp"]),
    (["email", "email address", "mail"], f"Email: {S.EMAIL}. For a faster reply, WhatsApp is best.", ["Send to WhatsApp"]),
    (["second number", "other number", "another number", "alternative number"], "The second line is +971 52 629 2564. The main WhatsApp number is +971 52 962 2078.", []),
    (["where are you", "location", "address", "office address", "where is your shop", "based"], "MTM Group Tech is based in Al Fahidi (Al Raffa), Bur Dubai, near Al Fahidi Metro Station. Mizan comes to you anywhere in Dubai.", ["Areas covered"]),
    (["metro", "nearest metro", "al fahidi metro"], "The base is near Al Fahidi Metro Station in Bur Dubai.", []),
    (["google maps", "map", "directions"], "You can find MTM Group Tech on Google Maps, and the link is in the footer of every page. Most jobs are on site, so Mizan comes to you.", []),
    (["opening hours", "working hours", "what time open", "are you open", "timing", "open now", "open today", "friday", "sunday"], "Hours aren't listed on the website. Message Mizan on WhatsApp and he'll confirm when he can come.", ["Send to WhatsApp"]),
    (["urgent", "emergency", "asap", "right now", "immediately", "today"], "For urgent jobs, call +971 52 962 2078 or WhatsApp your location and a photo. Mizan will tell you how soon he can come.", ["Call Mizan", "Send to WhatsApp"]),
    (["tomorrow", "this week", "weekend", "book appointment", "schedule visit", "appointment"], "Tell Mizan on WhatsApp which day suits you, along with your location and the job. He'll confirm a time.", ["Send to WhatsApp"]),
    (["price", "cost", "how much", "rate", "charges", "fee", "quotation", "quote", "estimate", "budget", "cheap", "expensive"], "Prices depend on the job, so Mizan looks at photos or visits first, then agrees the price with you before any work starts. No surprises on the bill.", ["Get a quote on WhatsApp"]),
    (["visit charge", "inspection fee", "site visit cost", "call out fee"], "Ask Mizan on WhatsApp about the visit. He agrees the price with you before any work starts.", ["Send to WhatsApp"]),
    (["payment", "pay by card", "cash", "bank transfer", "invoice"], "Payment details are agreed with Mizan directly. Ask him on WhatsApp.", ["Send to WhatsApp"]),
    (["warranty", "guarantee"], "Ask Mizan about warranty for your specific job and equipment. He'll explain what applies before starting.", []),
    (["languages", "language", "do you speak", "speak english", "speak hindi", "speak urdu", "speak bengali", "bangla", "arabic"], "Mizan speaks English, Hindi, Urdu and Bengali.", []),
    (["how to book", "how to hire", "how does it work", "process", "steps"], "1) Send your location and the job, with a photo if you can. 2) Mizan replies, agrees a time and a price. 3) He comes, fixes it and tests it with you.", ["Send to WhatsApp"]),
    (["site visit", "come and see", "inspection", "survey"], "Yes. For bigger jobs Mizan visits first, agrees camera or cable positions with you, then quotes.", ["Send to WhatsApp"]),
    (["send photo", "photo", "picture", "video of problem"], "Photos help a lot. Send them on WhatsApp to +971 52 962 2078 with your location.", ["Send to WhatsApp"]),
    (["services", "what do you do", "what services", "service list", "what can you fix"], "Mizan's services: CCTV, network and CCTV cabling, Wi-Fi and networking, access control and biometric, PABX, intercom and IP phones, IT support, electrical work, sound systems, and handyman maintenance.", ["CCTV", "Cabling", "Wi-Fi", "Electrical"]),
    (["specialty", "best at", "main service", "strongest"], "CCTV is Mizan's specialty, closely followed by network and CCTV cabling.", ["CCTV", "Cabling"]),
    (["who is mizan", "about mizan", "owner", "technician name", "founder"], f"{S.OWNER} (Mizan) is an IT & ELV technician and electrician, and the founder of MTM Group Tech. He leads every job himself.", []),
    (["experience", "how long working", "qualified", "certified", "professional"], "Mizan is an experienced IT & ELV technician and electrician. His work photos are in the Recent work section of the home page.", []),
    (["company name", "mtm", "jabalsalala", "mizan technical"], "MTM Group Tech, also known as Jabalsalala Technical Service, trading online as Mizan Technical.", []),
    (["residential", "home", "villa", "apartment", "flat"], "Yes, Mizan works in homes, villas and apartments across Dubai.", []),
    (["commercial", "business", "company"], "Yes, Mizan works for shops, offices, restaurants and warehouses.", []),
    (["office"], "Offices are a big part of Mizan's work: cabling, CCTV, Wi-Fi, phones, access control and IT support.", ["Cabling", "CCTV"]),
    (["warehouse", "factory", "workshop", "showroom"], "Yes, warehouses and workshops: wide-area CCTV, access control, network cabling and electrical maintenance.", ["CCTV", "Cabling"]),
    (["shop", "store", "restaurant", "cafe", "salon"], "Yes, Mizan looks after shops, cafes, salons and restaurants: CCTV, background music, Wi-Fi and electrical work.", []),
    (["supply equipment", "do you sell", "buy cameras", "supply and install", "provide material"], "Mizan can supply, install and maintain the equipment. Tell him what you need on WhatsApp.", ["Send to WhatsApp"]),
    (["brand", "which brand", "hikvision or dahua", "best brand"], "Mizan advises on the right equipment for your site and budget. Ask him on WhatsApp which options fit your job.", []),
    (["reviews", "rating", "feedback", "google review"], "You can read and leave reviews on MTM Group Tech's Google Business page. The links are on the home page.", []),
    (["facebook", "instagram", "social media"], "MTM Group Tech is on Facebook as \"MTM Group Tech\". The link is in the footer.", []),
    (["tips", "blog", "guides", "articles"], "Practical guides are on the Tips page, for example why CCTV stops recording and how to fix weak Wi-Fi.", ["Tips"]),
    (["licence", "license", "trade license"], "Ask Mizan directly on WhatsApp for company documents.", []),
    (["outside dubai", "abu dhabi", "ajman", "other emirates", "uae"], "Mizan covers all of Dubai and takes jobs in Sharjah. For other emirates, message him with your location.", ["Send to WhatsApp"]),
    (["areas", "areas covered", "which areas", "do you come to", "cover my area", "service area"], "All of Dubai, including Bur Dubai, Deira, Al Karama, Al Barsha, Business Bay, Jumeirah, Dubai Marina & JLT, Al Quoz and Mirdif, plus Sharjah.", []),
    (["something else", "other", "not listed", "different"], "If it's technical and it's broken, ask anyway. Describe it here or send a photo on WhatsApp and Mizan will tell you if he can fix it.", ["Send to WhatsApp"]),
    (["ok", "okay", "yes", "sure", "fine", "alright"], "Great. Anything else I can help with? Or tap below to send this chat to Mizan.", ["Send to WhatsApp", "Call Mizan"]),
    (["no", "nothing", "no thanks", "that's all"], "No problem. Mizan is on WhatsApp whenever you need him.", []),
    (["remote", "online support", "fix remotely"], "Some IT and network problems can be fixed remotely. Message Mizan on WhatsApp to arrange it.", ["Send to WhatsApp"]),
    (["smart home", "smart lock", "automation"], "Ask Mizan about smart locks and smart home devices. He covers access control, intercoms, networks and electrical work.", ["Send to WhatsApp"]),
    (["ac", "air conditioner", "ac repair", "plumbing", "plumber", "painting", "carpentry"], "Mizan focuses on CCTV, cabling, networks, access control, phones, IT, electrical work and general handyman jobs. Ask him on WhatsApp whether your job fits.", ["Send to WhatsApp"]),
    (["job", "vacancy", "hiring", "work with you"], "For work enquiries, message Mizan directly on WhatsApp.", []),
]

NOUN = {'cctv-installation-dubai': 'CCTV systems', 'structured-cabling-dubai': 'network and CCTV cabling', 'wifi-networking-dubai': 'Wi-Fi and networks', 'access-control-biometric-dubai': 'access control and biometric systems', 'pabx-intercom-ip-phone-dubai': 'PABX, intercom and IP phone systems', 'it-support-computer-repair-dubai': 'computers and IT systems', 'electrician-dubai': 'electrical work', 'sound-system-installation-dubai': 'sound systems', 'handyman-maintenance-dubai': 'handyman and maintenance jobs'}

CHIP_TO_SVC = {"CCTV": "cctv-installation-dubai", "Cabling": "structured-cabling-dubai", "Wi-Fi": "wifi-networking-dubai",
               "Electrical": "electrician-dubai", "Access control": "access-control-biometric-dubai",
               "Intercom / PABX": "pabx-intercom-ip-phone-dubai", "Computer": "it-support-computer-repair-dubai"}


def lc_first(t):
    return t[0].lower() + t[1:]


def build_kb(root=Path(__file__).resolve().parent):
    kb = []
    def add(k, a, s="", c=(), l="", **flags):
        kb.append({"k": list(k), "a": a, "s": s, "c": list(c), "l": l, **flags})
    for k, a, c in GENERAL:
        small = k[0] in ("hi", "thank you", "bye", "ok", "no")
        add(k, a, c=c, **({"g": 1} if small else {}))
    for s in S.SERVICES:
        slug, short = s["slug"], s["short"]
        names = SVC[slug]["names"]
        noun = NOUN[slug]
        path = f"/{slug}/"
        add(names, f"{s['intro']} Main jobs: {'; '.join(lc_first(b) for b in s['bullets'][:4])}.", slug, ["Price", "Book a visit", "Send to WhatsApp"], path)
        for k, a in SVC[slug]["problems"]:
            add(k, a, slug, ["Send to WhatsApp"], path, p=1)
        for q, a in s["faq"]:
            add([q.lower().rstrip("?")], a, slug, [], path)
        for n in names[:7]:
            add([f"{n} price", f"{n} cost", f"how much {n}", f"{n} quotation"], f"For {noun}, Mizan looks at the site or photos first, then agrees the price with you before starting. {ASK}", slug, ["Send to WhatsApp"])
            add([f"{n} repair", f"fix {n}", f"{n} not working", f"{n} problem"], f"Yes, Mizan fixes problems with {noun}, including work done by someone else. Tell me what's happening, or send a photo on WhatsApp.", slug, ["Send to WhatsApp"], path)
            add([f"{n} installation", f"install {n}", f"new {n}", f"{n} setup"], f"Yes, Mizan handles new {noun} for homes, shops, offices and warehouses. {ASK}", slug, ["Book a visit", "Send to WhatsApp"], path)
        add([f"book {names[0]}", f"{names[0]} appointment", f"{names[0]} visit"], f"To book {noun}: {ASK}", slug, ["Send to WhatsApp"])
        for b in s["bullets"]:
            words = [w.strip("(),/").lower() for w in b.split() if len(w.strip("(),/")) > 3][:4]
            add([b.lower(), " ".join(words)], f"Yes: {lc_first(b)}. That's part of Mizan's {s['short']} service.", slug, ["Send to WhatsApp"], path)
        for h, p in s["body"]:
            add([h.lower()], p, slug, [], path)
    for a in S.AREAS:
        name, path = a["name"], f"/areas/{a['slug']}/"
        nm = name.lower().replace("&", "and")
        al = {nm} | {x.strip() for x in name.lower().split("&")} | {nm.replace("al ", "")} | ({"marina"} if "marina" in nm else set())
        add(sorted(al) + [f"technician in {nm}", f"do you come to {nm}", f"{nm} service"], a["blurb"], "", ["Send to WhatsApp"], path)
        add([f"how fast {x}" for x in sorted(al)] + [f"how soon {nm}", f"today in {nm}"], f"Mizan covers {name}. Send your location pin on WhatsApp and he'll confirm how soon he can come.", "", ["Send to WhatsApp"], path)
        for s in S.SERVICES:
            n = SVC[s["slug"]]["names"][0]
            add([f"{n} {nm}", f"{n} in {nm}", f"{s['short'].lower()} {nm}"], f"Yes, Mizan covers {NOUN[s['slug']]} in {name}. {ASK}", s["slug"], ["Send to WhatsApp"], f"/{s['slug']}/")
    for p in sorted((root / "published").glob("*.json")):
        t = json.loads(p.read_text())
        add([t["title"].lower().rstrip("?")], f"{t['description']} There's a full guide on the Tips page.", t.get("service", ""), ["Tips"], f"/tips/{t['slug']}/")
    return kb
