"""Business facts, services and service areas for mizantechnical.site.

Edit this file to change wording, then run `python3 build.py`.
"""

DOMAIN = "https://mizantechnical.site"
NAME = "MTM Group Tech"
ALT_NAME = "Jabalsalala Technical Service"
OWNER = "Mohammad Mizanur Rahman"
OWNER_TITLE = "IT & ELV Technician and Electrician"
PHONE = "+971529622078"
PHONE_PRETTY = "+971 52 962 2078"
PHONE2 = "+971526292564"
PHONE2_PRETTY = "+971 52 629 2564"
WA = "https://wa.me/971529622078"
LANGUAGES = ["English", "Hindi", "Urdu", "Bengali"]
ADDRESS = {"street": "Al Fahidi (Al Raffa), Bur Dubai, near Al Fahidi Metro Station", "city": "Dubai", "country": "AE"}
MAPS = "https://www.google.com/maps/search/?api=1&query=MTM%20Group%20Tech%2C%20Al%20Fahidi%2C%20Dubai"
REVIEW = "https://search.google.com/local/writereview?placeid=ChIJ247zSdJpXz4RwjRNSPeqTOw"
FACEBOOK = "https://www.facebook.com/share/1BxH7MmmYX/?mibextid=wwXIfr"
SLOGAN = "Mizan Will Fix It"
# Inbox that receives a copy of every website request (via formsubmit.co).
# Leave empty to only open WhatsApp.
EMAIL = "mtmgroup.tech@gmail.com"


def img(photo_id, w=1600):
    return f"https://images.unsplash.com/{photo_id}?auto=format&fit=crop&w={w}&q=80"


IMG = {
    "panel": "img/work-db-boards.jpg",
    "screwdriver": img("photo-1660330589693-99889d60181e"),
    "plumbing": img("photo-1676210133055-eab6ef033ce3"),
    "cctv": img("photo-1557597774-9d273605dfa9"),
    "wires": img("photo-1635335874521-7987db781153"),
    "drill": img("photo-1562259929-b4e1fd3aef09"),
    "tools": img("photo-1581783898377-1c85bf937427"),
    "rack": "img/work-rack.jpg",
    "rack2": "img/work-rack-dressing.jpg",
    "db": "img/work-db-board.jpg",
    "reader": "img/work-access-reader.jpg",
    "intercom": "img/work-door-intercom.jpg",
    "boardroom": "img/work-boardroom.jpg",
    "ledwall": "img/work-led-wall.jpg",
    "dubai": img("photo-1651467606797-e1c660cf3fda"),
}

# Describes what is actually in each photo (used as alt text on page heroes)
IMG_ALT = {
    "panel": "Electrical distribution boards wired by Mizan's team on a Dubai job",
    "cctv": "CCTV security cameras mounted on a building wall",
    "wires": "Colour-coded wiring inside an electrical switch box",
    "rack": "Mizan cabling a network rack on an office fit-out in Dubai",
    "rack2": "Network cables bundled and dressed inside a server rack by Mizan",
    "db": "Distribution board wired and labelled by Mizan's team",
    "reader": "Access control reader and network cabinet installed on an office wall",
    "intercom": "Video door intercom installed by Mizan at a villa gate",
    "boardroom": "Boardroom table fitted with power and data points for an office",
    "ledwall": "Curved LED feature wall lighting fitted by Mizan's team",
    "dubai": "Dubai city skyline",
}

# Each service becomes /<slug>/. Keep claims factual: no prices, no warranties, no
# response-time promises unless the owner confirms them.
SERVICES = [
    {
        "slug": "cctv-installation-dubai",
        "short": "CCTV installation",
        "title": "CCTV Installation in Dubai | Camera Setup & Repair",
        "h1": "CCTV installation in Dubai",
        "desc": "CCTV camera installation, DVR/NVR setup, repair and maintenance for homes, shops and offices in Dubai. Watch your cameras live on your phone. Call or WhatsApp Mizan.",
        "img": "cctv",
        "intro": "CCTV is Mizan's specialty. Whether you need two cameras at a villa gate or a full system for a shop or warehouse, we plan the camera positions, run the cabling, set up the recorder and connect it to your phone so you can watch live from anywhere.",
        "bullets": ["IP and analog (HD) cameras, bullet and dome, indoor and outdoor", "IP camera NVR / DVR setup and configuration", "Live view and playback on your mobile", "Repair of cameras that stopped recording or lost picture", "Moving, adding or upgrading existing cameras", "Regular maintenance and cleaning"],
        "body": [
            ("Homes, shops and offices", "For homes we usually cover entrances, parking and the main gate. For shops and offices we look at the cash counter, stock areas and entry points. We visit first, agree the camera positions with you, and only then quote."),
            ("Cameras we install", "We work with wired IP cameras on an NVR, HD analog cameras on a DVR, and Wi-Fi cameras where running a cable is not practical. Indoor domes suit shops and offices, weatherproof bullets suit gates, parking and outside walls, and night-vision models keep a clear picture after dark."),
            ("Neat cabling and a safe recorder", "Most problems with CCTV start with poor cabling. We run cables in conduit or trunking, use proper connectors and PoE switches, and place the recorder somewhere secure and ventilated, with a hard disk sized for the number of days you want to keep."),
            ("Already have cameras?", "Many calls we get are for systems that stopped recording, lost the phone connection after a router change, or have a camera showing no picture. Send a photo of the recorder and the problem on WhatsApp and we can usually tell you what is needed before we come."),
        ],
        "faq": [
            ("Can I watch my CCTV cameras on my phone?", "Yes. We set up the recorder's mobile app on your phone during installation and show you how to view live and recorded footage."),
            ("Do you repair CCTV systems installed by someone else?", "Yes. We service and repair existing systems, including cameras with no picture, recorders that stopped recording and lost remote access."),
            ("How many cameras do I need?", "It depends on the entrances, rooms and outside areas you want covered. We walk the site with you, or look at photos and a rough plan on WhatsApp, and suggest the fewest cameras that cover what matters."),
            ("How long is the footage kept?", "That depends on the hard disk size, the number of cameras and the recording quality. We size the disk for the number of days you need, for example two weeks or a month."),
            ("Do the cameras work at night?", "Yes. We install cameras with infrared or colour night vision so entrances and parking stay visible after dark."),
            ("Should I choose wired or Wi-Fi cameras?", "Wired cameras are the most reliable and are our first choice. Wi-Fi cameras are useful where a cable cannot reach, as long as the signal at that spot is strong."),
            ("How is the price decided?", "We look at the site or photos first, then agree the price with you before any work starts."),
        ],
    },
    {
        "slug": "structured-cabling-dubai",
        "short": "Network & CCTV cabling",
        "title": "Structured Cabling in Dubai | Network & CCTV Cabling",
        "h1": "Structured, network and CCTV cabling in Dubai",
        "desc": "Cat6 network cabling, CCTV cabling, patch panels and racks for offices, shops, villas and warehouses in Dubai. Neat, labelled and tested. WhatsApp Mizan.",
        "img": "rack",
        "intro": "Cabling is one of Mizan's strongest skills. Good cameras and fast internet only work as well as the cable behind them, so we run it neatly, label every point and test it before we leave.",
        "bullets": ["Cat6 and Cat6A network cabling for offices, shops and villas", "CCTV cabling for IP (PoE) and HD analog cameras", "Fibre optic cabling between floors and buildings", "Data points, face plates and wall sockets", "Patch panels, network racks and cable management", "Testing and labelling of every cable run", "Tidying, tracing and re-terminating old messy cabling"],
        "body": [
            ("Network cabling for offices and homes", "We plan where each desk, printer, access point and TV needs a point, run the cables in conduit or trunking back to one rack, terminate them on a patch panel and label both ends. That makes adding a switch, moving a desk or finding a fault much quicker later."),
            ("CCTV cabling done right", "Most CCTV problems we are called for come from the cabling: loose connectors, cables crushed in ceilings or runs that are too long. We use proper cable for the camera type, PoE switches for IP cameras, and keep outdoor joints sealed against heat and dust."),
            ("Fixing old cabling", "If your rack is a tangle and nobody knows which cable goes where, we trace, test, label and tidy it so your network and cameras are easier to look after."),
        ],
        "faq": [
            ("What cable do you use for office networks?", "Usually Cat6, which handles gigabit speeds comfortably. For longer runs or higher speeds we discuss Cat6A or fibre with you."),
            ("Can you run CCTV and network cabling in the same job?", "Yes. We often cable cameras, access points and data points together and bring everything back to one rack, which saves time and keeps it neat."),
            ("Do you test the cables?", "Yes. Every run is tested and labelled at both ends before we finish."),
            ("Can you work in an occupied office or shop?", "Yes. We plan the work around your opening hours and keep the area tidy while we cable."),
            ("How is the price decided?", "It depends on the number of points, cable lengths and how the cable can be routed. We look at the site or photos first and agree the price before starting."),
        ],
    },
    {
        "slug": "wifi-networking-dubai",
        "short": "Wi-Fi & networking",
        "title": "Wi-Fi & Network Installation in Dubai | Cabling & Setup",
        "h1": "Wi-Fi and network installation in Dubai",
        "desc": "Fix weak Wi-Fi and slow networks. Structured cabling, routers, switches and access points for homes and offices in Dubai. Call or WhatsApp MTM Group Tech.",
        "img": "rack2",
        "intro": "Dead zones, dropping connections and slow office internet are usually a layout or cabling problem, not the internet package. We find where the signal fails and fix it with proper cabling and well-placed access points.",
        "bullets": ["Structured cabling (LAN and network cabling) and patch panels", "Router, switch and Wi-Fi configuration and management", "Whole-home and whole-office Wi-Fi coverage", "Mesh systems for villas and multi-floor homes", "LAN, WAN, VLAN and VPN setup and troubleshooting", "Connecting CCTV, printers and phones to the network"],
        "body": [
            ("For homes", "In villas and larger apartments one router is rarely enough. We add wired access points or a mesh system so every room, the majlis and the garden get a stable signal."),
            ("For offices and shops", "We run cabling to desks, set up switches and separate guest Wi-Fi from your business network, then label everything so the next job is easy."),
        ],
        "faq": [
            ("Why is my Wi-Fi weak in some rooms?", "Concrete walls and distance block Wi-Fi. The fix is usually an extra wired access point or a mesh unit in the right place, not a faster internet plan."),
            ("Do you work with my existing internet provider's router?", "Yes. We work with the router your provider installed and add equipment around it where needed."),
        ],
    },
    {
        "slug": "access-control-biometric-dubai",
        "short": "Access control & biometric",
        "title": "Access Control & Biometric Systems in Dubai | Installation",
        "h1": "Access control and biometric systems in Dubai",
        "desc": "Fingerprint, face and card access control, door locks and attendance machines installed and serviced in Dubai. Call or WhatsApp MTM Group Tech.",
        "img": "reader",
        "intro": "Control who enters your office, building or store room, and record staff attendance automatically. We install the reader, the lock and the controller, and set up the users for you.",
        "bullets": ["Fingerprint and face-recognition readers", "Card and keypad door access", "Magnetic and electric strike locks", "Time-attendance installation, reports and support", "Exit buttons and emergency release", "Repair and re-programming of existing systems"],
        "body": [
            ("Attendance made simple", "Biometric attendance machines record when staff arrive and leave. We install the device, enrol your staff and show you how to download the reports."),
        ],
        "faq": [
            ("Can you add new staff fingerprints to my existing machine?", "Yes. We can enrol new users, remove old ones and fix devices that stopped syncing."),
            ("What happens to the door in a power cut?", "We fit the lock and release setup that suits your door, including emergency release where required, and explain how it behaves before we leave."),
        ],
    },
    {
        "slug": "pabx-intercom-ip-phone-dubai",
        "short": "PABX, intercom & IP phones",
        "title": "PABX, VoIP, Intercom & IP Phone Installation in Dubai",
        "h1": "PABX, intercom and IP phones in Dubai",
        "desc": "Office PABX telephone systems, IP phones, door and video intercoms installed, programmed and repaired in Dubai. Call or WhatsApp MTM Group Tech.",
        "img": "intercom",
        "intro": "From a small office that needs extensions and call transfer to a villa that needs a video intercom at the gate, we install, wire and program the system so it works the way you need.",
        "bullets": ["PABX installation and programming", "IP telephone (VoIP) installation and configuration", "Extension wiring and moves", "Door intercom and video intercom", "Gate and villa intercoms", "Fault finding and repair"],
        "body": [],
        "faq": [
            ("Can you program extensions and call transfer on my existing PABX?", "Yes. We program existing systems as well as installing new ones."),
            ("Do you install video intercoms for villas?", "Yes, including the outdoor station at the gate and indoor screens inside the house."),
        ],
    },
    {
        "slug": "it-support-computer-repair-dubai",
        "short": "IT support & computer repair",
        "title": "IT Support & Computer Repair in Dubai | On-site Service",
        "h1": "IT support and computer repair in Dubai",
        "desc": "On-site IT support in Dubai: computer and laptop repair, slow PCs, printers, software, email and office network problems. Call or WhatsApp MTM Group Tech.",
        "img": "boardroom",
        "intro": "When a computer, printer or office system stops working, business stops too. We come to your home or office, find the problem and fix it on site where possible.",
        "bullets": ["Computer and laptop troubleshooting", "Slow computers, viruses and clean-ups", "Printer and scanner setup", "Software and email setup", "Office network and shared folders", "On-site and remote IT support"],
        "body": [],
        "faq": [
            ("Do you come to the office?", "Yes. Most IT support jobs are done on site at your home or office."),
            ("Can you look after our small office's IT regularly?", "Yes. Ask on WhatsApp about regular maintenance visits for your office."),
        ],
    },
    {
        "slug": "electrician-dubai",
        "short": "Electrician",
        "title": "Electrician in Dubai | Electrical Installation & Repair",
        "h1": "Electrician in Dubai",
        "desc": "Electrical repairs and installation in Dubai: sockets, switches, lights, DB boards, tripping breakers and new points. Call or WhatsApp Mizan for an electrician.",
        "img": "db",
        "intro": "Tripping breakers, dead sockets, flickering lights or a new point where you need it. We find the fault safely and fix it properly.",
        "bullets": ["Socket, switch and light installation", "Breakers that keep tripping", "Distribution board (DB) work", "New power points and wiring", "Light fittings and fans", "Electrical maintenance for shops and offices"],
        "body": [
            ("Safety first", "Electrical faults can be dangerous. If something smells of burning or a breaker keeps tripping, switch it off at the board and send us a message."),
        ],
        "faq": [
            ("My breaker keeps tripping. Can you fix it?", "Yes. We trace which circuit or appliance causes the trip and repair the fault."),
            ("Do you install lights and ceiling fans?", "Yes, along with new sockets, switches and power points."),
        ],
    },
    {
        "slug": "sound-system-installation-dubai",
        "short": "Sound systems",
        "title": "Sound System Installation in Dubai | PA & Background Music",
        "h1": "Sound system installation in Dubai",
        "desc": "Sound and PA systems for shops, offices, restaurants, mosques, halls and homes in Dubai: speakers, amplifiers and background music. Call or WhatsApp MTM Group Tech.",
        "img": "wires",
        "intro": "Clear sound in the right places. We install ceiling and wall speakers, amplifiers and microphones for background music, announcements and events.",
        "bullets": ["Ceiling and wall speakers", "Amplifiers and mixers", "Background music for shops and restaurants", "PA and announcement systems", "Microphones for halls and meeting rooms", "Repair of existing sound systems"],
        "body": [],
        "faq": [
            ("Can you fix an existing sound system?", "Yes. We repair and re-wire existing speakers, amplifiers and microphones."),
        ],
    },
    {
        "slug": "handyman-maintenance-dubai",
        "short": "Handyman & maintenance",
        "title": "Handyman & Maintenance Services in Dubai | Home & Office",
        "h1": "Handyman and maintenance in Dubai",
        "desc": "Reliable handyman and maintenance in Dubai for homes and offices: fixing, fitting, mounting and regular maintenance visits. One call, Mizan will fix it.",
        "img": "ledwall",
        "intro": "Not sure who to call? If something technical at home or in the office is broken, send a photo. Mizan will tell you if we can fix it, and in most cases we can.",
        "bullets": ["General repairs at home and in the office", "Fitting and mounting (TVs, shelves, fixtures)", "Small fixes before moving in or out", "Regular maintenance visits", "Shop and office maintenance", "One contact for many small jobs"],
        "body": [
            ("One technician, many jobs", "Save time by listing everything that needs fixing. We can often handle several small jobs in one visit."),
        ],
        "faq": [
            ("Can you do several small jobs in one visit?", "Yes. Send us the list on WhatsApp and we will plan the visit."),
        ],
    },
]

# Each area becomes /areas/<slug>/. Keep the blurb specific to the area so pages are
# not duplicates of each other.
AREAS = [
    {"slug": "bur-dubai", "name": "Bur Dubai", "blurb": "Our base is in Al Fahidi (Al Raffa), Bur Dubai, near Al Fahidi Metro Station, so this is home ground. We look after shops in the old souq, offices and apartments around Al Fahidi, Mankhool and Al Raffa."},
    {"slug": "deira", "name": "Deira", "blurb": "Deira's trading offices, warehouses and busy shops need CCTV, phones and networks that keep running. We are just across the creek from Deira."},
    {"slug": "al-karama", "name": "Al Karama", "blurb": "Karama's apartments, restaurants and small offices are close to our base, which makes it easy to send a technician when something stops working."},
    {"slug": "al-barsha", "name": "Al Barsha", "blurb": "From Al Barsha villas that need full Wi-Fi coverage and gate intercoms to apartments and offices near Mall of the Emirates."},
    {"slug": "business-bay", "name": "Business Bay", "blurb": "Business Bay offices rely on solid networks, access control and phones. We install and maintain them for small and growing companies."},
    {"slug": "jumeirah", "name": "Jumeirah", "blurb": "Jumeirah villas often need CCTV at the gate, video intercoms and Wi-Fi that reaches every floor and the garden."},
    {"slug": "dubai-marina-jlt", "name": "Dubai Marina & JLT", "blurb": "High-rise apartments and offices in the Marina and JLT, where Wi-Fi dead zones, smart locks and small office IT are common jobs."},
    {"slug": "al-quoz", "name": "Al Quoz", "blurb": "Warehouses, workshops and showrooms in Al Quoz need wide-area CCTV, access control and reliable electrical work."},
    {"slug": "mirdif", "name": "Mirdif", "blurb": "Family villas in Mirdif: CCTV, intercoms, Wi-Fi coverage and the everyday repairs that come with a busy home."},
    {"slug": "sharjah", "name": "Sharjah", "blurb": "We also take jobs in Sharjah for homes, shops and offices. Send your location on WhatsApp to arrange a visit."},
]

# Mizan's own job photos: the home carousel and /gallery/. One photo per job
# type, no near-duplicates. (file stem, alt text, caption, category)
GALLERY = [
    ("work-onsite", "Mizan on site in Dubai wearing a safety vest", "On site in Dubai", "On site"),
    ("work-rack", "Mizan cabling a network rack on an office fit-out in Dubai", "Network rack cabling", "Cabling"),
    ("work-network-cabinet", "Network cabinet with patched data cables and switches", "Network cabinet", "Cabling"),
    ("work-patch-panel", "Patch panels with neatly terminated blue network cables", "Patch panel termination", "Cabling"),
    ("work-rack-dressing", "Network cables bundled and dressed inside a new server rack", "Rack cable dressing", "Cabling"),
    ("work-cable-riser", "Bundles of network cable pulled through a cable riser", "Cable pulls in the riser", "Cabling"),
    ("work-cable-tray", "Cable trays and a coiled network cable ready for termination", "Cable trays", "Cabling"),
    ("work-floor-boxes", "Floor boxes for power and data being fitted in a new office", "Floor boxes for power and data", "Cabling"),
    ("work-boardroom", "Boardroom table being fitted with power and data points", "Boardroom table data points", "IT & AV"),
    ("work-door-intercom", "Video door intercom installed at a villa gate", "Video door intercom", "Security"),
    ("work-access-reader", "Access control reader and network cabinet installed on an office wall", "Access control & cabinet", "Security"),
    ("work-db-panel", "Electrical distribution board with warning labels", "Electrical distribution board", "Electrical"),
    ("work-db-boards", "New electrical distribution boards with breakers wired in", "Distribution boards", "Electrical"),
    ("work-led-wall", "Curved LED feature wall lighting installed in a Dubai showroom", "LED feature wall lighting", "Electrical"),
    ("work-onsite-office", "Mizan on site at an office fit-out in Dubai", "Office fit-out, Dubai", "On site"),
]
