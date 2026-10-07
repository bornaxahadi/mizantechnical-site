"""Two/three-colour line icons in the client's reference style: thin dark-blue outlines plus one solid
canary-yellow accent shape (class "acc"), which gets a small looping animation."""

ICONS = {
    "cctv": '<rect x="8" y="14" width="24" height="13" rx="2" class="ln tone"/><path d="M32 18l8-4v13l-8-4M14 27v9H8" class="ln"/><circle cx="15" cy="20.5" r="3.2" class="acc blink"/>',
    "cable": '<rect x="6" y="8" width="36" height="12" rx="2" class="ln tone"/><path d="M12 20v6c0 4 4 6 8 6h8c4 0 8 2 8 6v4M24 20v22" class="ln"/><rect x="10" y="12" width="4" height="4" class="acc blink"/><rect x="22" y="12" width="4" height="4" class="acc2"/><rect x="34" y="12" width="4" height="4" class="acc"/>',
    "wifi": '<path d="M7 20a24 24 0 0 1 34 0M12.5 25.5a16 16 0 0 1 23 0M18 31a8 8 0 0 1 12 0" class="ln"/><circle cx="24" cy="37" r="3.2" class="acc pulse"/>',
    "bio": '<rect x="13" y="6" width="22" height="36" rx="3" class="ln tone"/><circle cx="24" cy="34" r="2.6" class="acc2"/><rect x="17" y="11" width="14" height="5" class="acc scan"/>',
    "pabx": '<circle cx="11" cy="24" r="5" class="ln"/><circle cx="37" cy="24" r="5" class="ln"/><circle cx="37" cy="24" r="2.2" class="acc2"/><path d="M16 24h16" class="ln"/><circle cx="24" cy="24" r="3" class="acc travel"/>',
    "it": '<rect x="6" y="9" width="36" height="23" rx="2" class="ln tone"/><path d="M17 40h14M24 32v8" class="ln"/><circle cx="35" cy="27" r="1.8" class="acc2"/><rect x="11" y="14" width="10" height="7" class="acc blink"/>',
    "elec": '<path d="M27 5 11 27h11l-3 16 18-24H26z" class="ln tone"/><circle cx="37" cy="37" r="3.2" class="acc pulse"/><circle cx="9" cy="9" r="2" class="acc2"/>',
    "sound": '<path d="M7 19h7l9-7v24l-9-7H7z" class="ln tone"/><path d="M30 18a8 8 0 0 1 0 12M35 13a15 15 0 0 1 0 22" class="ln"/><circle cx="30" cy="24" r="2.6" class="acc travel-x"/>',
    "home": '<path d="M7 22 24 9l17 13M11 19v21h26V19" class="ln"/><rect x="20" y="28" width="8" height="12" class="acc scan"/>',
    "fast": '<circle cx="24" cy="24" r="16" class="ln"/><path d="M24 13v11l7 4" class="ln"/><circle cx="24" cy="8" r="3" class="acc orbit"/>',
    "tested": '<path d="M24 6 9 12v10c0 9 6.5 16 15 20 8.5-4 15-11 15-20V12z" class="ln"/><path d="m17 24 5 5 9-10" class="ln"/><circle cx="38" cy="10" r="3" class="acc pulse"/>',
    "price": '<rect x="7" y="13" width="34" height="22" rx="2" class="ln tone"/><circle cx="24" cy="24" r="5" class="ln"/><rect x="11" y="17" width="6" height="4" class="acc blink"/>',
    "map": '<path d="M24 43s13-11.5 13-22a13 13 0 0 0-26 0c0 10.5 13 22 13 22z" class="ln"/><circle cx="24" cy="21" r="4.5" class="acc pulse"/>',
    "repair": '<g class="spin"><path d="M37.1,20.7 L40.8,21.2 L40.8,26.8 L37.1,27.3 L35.6,31.0 L37.8,33.9 L33.9,37.8 L31.0,35.6 L27.3,37.1 L26.8,40.8 L21.2,40.8 L20.7,37.1 L17.0,35.6 L14.1,37.8 L10.2,33.9 L12.4,31.0 L10.9,27.3 L7.2,26.8 L7.2,21.2 L10.9,20.7 L12.4,17.0 L10.2,14.1 L14.1,10.2 L17.0,12.4 L20.7,10.9 L21.2,7.2 L26.8,7.2 L27.3,10.9 L31.0,12.4 L33.9,10.2 L37.8,14.1 L35.6,17.0Z" class="ln"/><circle cx="24" cy="24" r="6.5" class="ln"/></g><circle cx="24" cy="24" r="3.4" class="acc pulse"/>',
    "tools": '<path d="M31 7a8 8 0 0 0-7.6 10.4L8.6 32.2a3.3 3.3 0 0 0 4.7 4.7l14.8-14.8A8 8 0 0 0 39 15l-4.9 1.2-3.2-3.2L32 8z" class="ln"/><path d="M10 10l2.5-1.5L30 26l-2 2L10 10z" class="ln"/><path d="M29.5 31.5l3-3 9.2 9.2a2.1 2.1 0 0 1-3 3z" class="acc blink"/>',
    "drill": '<path d="M7 13h22a4 4 0 0 1 4 4v5a4 4 0 0 1-4 4H7z" class="ln tone"/><path d="M13 26l-3 14h9l3-14M7 13v13" class="ln"/><path d="M38 19.5h7" class="ln"/><rect x="15.5" y="26" width="4" height="5" class="acc2"/><rect x="33" y="16" width="5" height="7" class="acc jitter"/>',
    "meter": '<rect x="12" y="5" width="24" height="38" rx="3" class="ln tone"/><path d="M17 19a7 7 0 0 1 14 0" class="ln"/><path d="M24 19l3.5-5" class="ln swing"/><circle cx="24" cy="37" r="2.7" class="acc2"/><rect x="17" y="24" width="14" height="6" class="acc blink"/>',
    "hardhat": '<path d="M10 32a14 14 0 0 1 28 0" class="ln"/><path d="M6 32h36v4.5H6z" class="ln"/><path d="M19 18.5V32M29 18.5V32" class="ln"/><rect x="21.5" y="16" width="5" height="16" class="acc scan-sm"/>',
    "techhelp": '<g transform="translate(0 8) scale(.8)"><path d="M12 8h6l3 8-4 3a20 20 0 0 0 10 10l3-4 8 3v6a3 3 0 0 1-3 3A31 31 0 0 1 9 11a3 3 0 0 1 3-3z" class="ln"/></g><path d="M29 5h13a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-7l-4 3.5V18h-2a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2z" class="ln"/><circle cx="35.5" cy="11.5" r="2.6" class="acc pulse"/>',
    "toolbox": '<rect x="6" y="18" width="36" height="22" rx="2" class="ln tone"/><path d="M17 18v-5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v5M6 27h36" class="ln"/><rect x="21" y="24" width="6" height="7" class="acc blink"/>',
}


def icon(name, cls="ic-svg"):
    return f'<svg class="{cls}" viewBox="0 0 48 48" aria-hidden="true">{ICONS[name]}</svg>'
