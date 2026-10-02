#!/usr/bin/env python3
"""
Bộ sinh website tĩnh cho giacngungon.org
Cách dùng:  python3 build.py      -> tạo thư mục dist/ để upload lên host
Thêm bài:   tạo file content/<ten-bai>.md (xem README.md)
"""
import json, re, shutil, unicodedata, html, datetime
from pathlib import Path
import yaml, markdown
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
DIST = ROOT / "dist"

# ------------------------------------------------------------------ CẤU HÌNH
SITE = {
    "name": "Giấc Ngủ Ngon",
    "domain": "https://giacngungon.org",
    "tagline": "Người đồng hành tin cậy cho giấc ngủ của bạn",
    "phone": "0901.312.129",
    "phone_raw": "0901312129",
    "zalo": "https://zalo.me/0901312129",
    "facebook": "",  # điền link fanpage nếu có
    "doctor": "Bs. Nguyễn Thi Phú",
    "doctor_title": "Bác sĩ chuyên khoa Tâm thần kinh – Giấc ngủ",
    "doctor_creds": [
        "Giảng viên Đại học Y Dược TP. HCM",
        "Phòng khám Tâm thần kinh – Bệnh viện Đại học Y Dược TP. HCM",
        "Phòng khám Giấc ngủ – Trung tâm Y khoa Hòa Hảo",
        "Khoa nội trú – Bệnh viện Tâm thần TP. HCM",
    ],
}

CATEGORIES = {
    "mat-ngu": {
        "name": "Mất ngủ", "color": "#5b7552", "icon": "moon",
        "desc": "Dấu hiệu, nguyên nhân, các dạng mất ngủ và những phương pháp điều trị đã được chứng minh hiệu quả.",
    },
    "roi-loan-giac-ngu": {
        "name": "Rối loạn giấc ngủ", "color": "#3f7f78", "icon": "wave",
        "desc": "Ngưng thở khi ngủ, ngáy, ngủ rũ, chân không yên, mộng du, bóng đè… – hiểu đúng để điều trị đúng.",
    },
    "cai-thien-giac-ngu": {
        "name": "Cải thiện giấc ngủ", "color": "#8a9a3b", "icon": "leaf",
        "desc": "Thói quen, môi trường phòng ngủ, ăn uống và kỹ thuật thư giãn giúp bạn ngủ nhanh, ngủ sâu hơn.",
    },
    "khoa-hoc-giac-ngu": {
        "name": "Hiểu về giấc ngủ", "color": "#4f7392", "icon": "brain",
        "desc": "Giấc ngủ vận hành thế nào, các giai đoạn ngủ, nhịp sinh học và vì sao thiếu ngủ nguy hiểm.",
    },
    "doi-tuong": {
        "name": "Giấc ngủ theo đối tượng", "color": "#b8734e", "icon": "people",
        "desc": "Trẻ em, tuổi dậy thì, phụ nữ mang thai, tiền mãn kinh, người cao tuổi và người làm ca đêm.",
    },
    "suc-khoe-tam-than": {
        "name": "Sức khỏe tâm thần", "color": "#7b5e86", "icon": "heart",
        "desc": "Lo âu, trầm cảm, sang chấn tâm lý, lưỡng cực, ám ảnh cưỡng chế, tâm thần phân liệt… – giải thích bằng lời dễ hiểu để bạn nhận ra vấn đề sớm và biết khi nào cần đi khám.",
        "cta": ("Bạn thấy mình hoặc người thân trong bài viết này?",
                "Những vấn đề tâm lý – tâm thần đều có thể điều trị. Gặp bác sĩ chuyên khoa để được lắng nghe, đánh giá đúng và có hướng điều trị phù hợp."),
        "side": "Khám và tư vấn lo âu, trầm cảm, mất ngủ và các vấn đề tâm lý với",
    },
}

ICONS = {
    "moon": '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
    "wave": '<path d="M2 12c2-4 4-4 6 0s4 4 6 0 4-4 6 0"/><path d="M2 18c2-4 4-4 6 0s4 4 6 0 4-4 6 0" opacity=".5"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10z"/><path d="M2 21c0-3 1.9-5.4 5.2-6.1"/>',
    "brain": '<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.9.7 2.5 2.5 0 0 1-2.9-3.4A3 3 0 0 1 3 12a3 3 0 0 1 1.8-2.8A2.5 2.5 0 0 1 7 5.5 2.5 2.5 0 0 1 9.5 2z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.9.7 2.5 2.5 0 0 0 2.9-3.4A3 3 0 0 0 21 12a3 3 0 0 0-1.8-2.8A2.5 2.5 0 0 0 17 5.5 2.5 2.5 0 0 0 14.5 2z"/>',
    "people": '<circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/><path d="M16 3.1a4 4 0 0 1 0 7.8"/><path d="M21 21v-2a4 4 0 0 0-3-3.9"/>',
    "heart": '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21l7.8-7.6 1-1.1a5.5 5.5 0 0 0 0-7.7z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "check": '<path d="M9 11l3 3 8-8"/><path d="M20 12v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h9"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
    "stetho": '<path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6 6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6 6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/>',
    "bed": '<path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/>',
    "snore": '<path d="M4 4h6l-6 7h6M13 10h5l-5 6h5M18 3h3l-3 4h3"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "arrow": '<path d="M5 12h14M13 5l7 7-7 7"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
}

def icon(name, size=24, cls="ic"):
    return (f'<svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

# ------------------------------------------------------------------ TIỆN ÍCH
def strip_accents(s):
    s = s.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")

def slugify(value, separator="-"):
    v = strip_accents(value).lower()
    v = re.sub(r"[^a-z0-9\s-]", "", v)
    return re.sub(r"[\s-]+", separator, v).strip(separator)

def esc(s):
    return html.escape(str(s), quote=True)

def fmt_date(d):
    return d.strftime("%d/%m/%Y")

# kích thước hiển thị gần đúng của ảnh thẻ theo cỡ (để trình duyệt chọn bản ảnh vừa đủ)
THUMB_SIZES = {"sm": "76px", "md": "(max-width:900px) 92vw, 380px", "lg": "(max-width:900px) 92vw, 600px",
               "xl": "(max-width:900px) 92vw, 720px"}

def athumb(a, size="md", lazy=True):
    """Ảnh đại diện bài: dùng ảnh thật nếu có, ngược lại dùng hình minh họa theo chuyên mục"""
    if a.get("img"):
        load = 'loading="lazy"' if lazy else 'fetchpriority="high"'
        return (f'<div class="thumb thumb-{size} has-img" style="--c:{CATEGORIES[a["category"]]["color"]}">'
                f'<img src="{a["img_t"]}" srcset="{a["img_s"]} {a["img_s_w"]}w, {a["img_t"]} {a["img_t_w"]}w" '
                f'sizes="{THUMB_SIZES.get(size, THUMB_SIZES["md"])}" alt="" width="{a["img_t_w"]}" height="{a["img_t_h"]}" {load} decoding="async"></div>')
    return thumb(a["category"], size)

def thumb(cat_key, size="md"):
    c = CATEGORIES[cat_key]
    return (f'<div class="thumb thumb-{size}" style="--c:{c["color"]}">'
            f'<span class="stars"></span>{icon(c["icon"], 44, "thumb-ic")}</div>')

# ------------------------------------------------------------------ ĐỌC BÀI VIẾT
def load_articles():
    arts = []
    for f in sorted(CONTENT.glob("*.md")):
        raw = f.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n(.*)$", raw, re.S)
        if not m:
            raise SystemExit(f"Thiếu front matter: {f.name}")
        meta = yaml.safe_load(m.group(1))
        body = m.group(2).strip()
        meta.setdefault("slug", f.stem)
        if meta["category"] not in CATEGORIES:
            raise SystemExit(f"Chuyên mục không hợp lệ trong {f.name}: {meta['category']}")
        d = meta.get("date")
        meta["date"] = d if isinstance(d, datetime.date) else datetime.date.fromisoformat(str(d))
        u = meta.get("updated") or meta["date"]
        meta["updated"] = u if isinstance(u, datetime.date) else datetime.date.fromisoformat(str(u))
        md = markdown.Markdown(extensions=["toc", "tables", "attr_list", "sane_lists"],
                               extension_configs={"toc": {"slugify": slugify, "toc_depth": "2"}})
        meta["html"] = md.convert(body)
        meta["toc"] = [(t["id"], t["name"]) for t in md.toc_tokens]
        words = len(re.sub(r"<[^>]+>", " ", meta["html"]).split())
        meta["words"] = words
        meta["minutes"] = max(2, round(words / 200))
        meta.setdefault("key", [])
        meta.setdefault("sources", [])
        meta.setdefault("featured", False)
        meta.setdefault("reviewed", False)
        arts.append(meta)
    slugs = [a["slug"] for a in arts]
    dup = {s for s in slugs if slugs.count(s) > 1}
    if dup:
        raise SystemExit(f"Trùng slug: {dup}")
    # cùng ngày: bài có "weight" lớn hơn đứng trước (mặc định 0)
    arts.sort(key=lambda a: (a["date"], a.get("weight", 0), a["slug"]), reverse=True)
    return arts

# ------------------------------------------------------------------ KHUNG TRANG
FONTS = "https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=Lora:ital,wght@0,600;0,700;1,500&family=Quicksand:wght@500;600&display=swap"
def head(title, desc, path, jsonld=None, og_type="website", og_img=None):
    url = SITE["domain"] + path
    full = title if title == SITE["name"] else f"{title} | {SITE['name']}"
    ld = ""
    if jsonld:
        ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>'
    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['domain']}{og_img or '/assets/img/og-cover.png'}">
<meta property="og:locale" content="vi_VN">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#273a24">
<link rel="icon" href="/assets/img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preload" as="style" href="{FONTS}" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="{FONTS}"></noscript>
<link rel="stylesheet" href="/assets/css/style.css?v={BUILD_V}">
{ld}
</head>
<body>
<a class="skip" href="#noi-dung">Bỏ qua điều hướng</a>
"""

def header(arts):
    by_cat = {k: [a for a in arts if a["category"] == k] for k in CATEGORIES}
    mega = ""
    for k, c in CATEGORIES.items():
        items = "".join(f'<li><a href="/{a["slug"]}/">{esc(a["title"])}</a></li>' for a in by_cat[k][:6])
        mega += (f'<div class="mega-col"><a class="mega-h" href="/chuyen-muc/{k}/" style="--c:{c["color"]}">'
                 f'{icon(c["icon"], 18)}{c["name"]}</a><ul>{items}</ul>'
                 f'<a class="mega-all" href="/chuyen-muc/{k}/">Xem tất cả →</a></div>')
    return f"""<div class="topbar"><div class="wrap topbar-in">
<span>{icon('phone',15)} Tư vấn &amp; đặt lịch: <a href="tel:{SITE['phone_raw']}"><b>{SITE['phone']}</b></a></span>
<span class="topbar-r"><a href="{SITE['zalo']}" target="_blank" rel="noopener">Chat Zalo</a><a href="/chinh-sach-bien-tap/">Chính sách biên tập</a></span>
</div></div>
<header class="hdr" id="top"><div class="wrap hdr-in">
<a class="logo" href="/" aria-label="{SITE['name']} – Trang chủ">
<img src="/assets/img/logo-icon.png" alt="" width="46" height="46"><span class="wordmark">Giấc ngủ ngon</span></a>
<nav class="nav" id="nav" aria-label="Điều hướng chính">
<div class="nav-item has-mega"><button class="nav-link" aria-expanded="false">Kiến thức giấc ngủ <i class="caret"></i></button>
<div class="mega"><div class="wrap mega-in">{mega}</div></div></div>
<div class="nav-item has-drop"><button class="nav-link" aria-expanded="false">Công cụ <i class="caret"></i></button>
<div class="drop"><a href="/cong-cu/tinh-gio-ngu/">{icon('clock',18)}<span><b>Tính giờ đi ngủ</b><small>Theo chu kỳ 90 phút</small></span></a>
<a href="/cong-cu/kiem-tra-giac-ngu/">{icon('check',18)}<span><b>Kiểm tra giấc ngủ</b><small>Bài tự đánh giá 8 câu</small></span></a></div></div>
<a class="nav-link" href="/blog/">Bài viết</a>
<a class="nav-link" href="/bac-si/">Bác sĩ</a>
<a class="nav-link" href="/lien-he/">Liên hệ</a>
</nav>
<div class="hdr-act">
<button class="icon-btn" id="openSearch" aria-label="Tìm kiếm">{icon('search',20)}</button>
<a class="btn btn-gold hide-sm" href="/lien-he/">{icon('calendar',17)} Đặt lịch khám</a>
<button class="icon-btn show-sm" id="menuBtn" aria-label="Mở menu" aria-controls="nav" aria-expanded="false">{icon('menu',22)}</button>
</div></div></header>
<div class="search-ov" id="searchOv" hidden><div class="search-box" role="dialog" aria-label="Tìm kiếm bài viết">
<div class="search-row">{icon('search',20)}<input id="searchInput" type="search" placeholder="Tìm bài viết: mất ngủ, ngáy, melatonin…" autocomplete="off"><button class="icon-btn" id="closeSearch" aria-label="Đóng">{icon('x',20)}</button></div>
<div id="searchRes" class="search-res"></div></div></div>
<main id="noi-dung">
"""

def footer():
    cats = "".join(f'<li><a href="/chuyen-muc/{k}/">{c["name"]}</a></li>' for k, c in CATEGORIES.items())
    year = datetime.date.today().year
    fb = f'<a href="{SITE["facebook"]}" target="_blank" rel="noopener">Facebook</a>' if SITE["facebook"] else ""
    return f"""</main>
<footer class="ftr"><div class="wrap">
<div class="ftr-grid">
<div class="ftr-brand"><a class="logo-foot" href="/" aria-label="{SITE['name']}"><img src="/assets/img/logo-full-white.png" alt="Giấc ngủ ngon" width="150" height="121" loading="lazy" decoding="async"></a>
<p>Kiến thức giấc ngủ dễ hiểu, dựa trên bằng chứng – và phòng khám giúp bạn lấy lại những đêm ngon giấc.</p>
<div class="ftr-contact"><a href="tel:{SITE['phone_raw']}">{icon('phone',16)} {SITE['phone']}</a><a href="{SITE['zalo']}" target="_blank" rel="noopener">{icon('chat',16)} Zalo</a>{fb}</div></div>
<div><h4>Chuyên mục</h4><ul>{cats}</ul></div>
<div><h4>Công cụ</h4><ul><li><a href="/cong-cu/tinh-gio-ngu/">Tính giờ đi ngủ</a></li><li><a href="/cong-cu/kiem-tra-giac-ngu/">Kiểm tra giấc ngủ</a></li><li><a href="/blog/">Tất cả bài viết</a></li></ul></div>
<div><h4>Về chúng tôi</h4><ul><li><a href="/bac-si/">Bác sĩ &amp; quy trình khám</a></li><li><a href="/lien-he/">Đặt lịch khám</a></li><li><a href="/chinh-sach-bien-tap/">Chính sách biên tập</a></li></ul></div>
</div>
<p class="ftr-disc">Nội dung trên website chỉ nhằm mục đích cung cấp thông tin, không thay thế cho việc chẩn đoán hay điều trị của bác sĩ. Nếu bạn có vấn đề về sức khỏe, hãy đến cơ sở y tế. Trường hợp khẩn cấp, gọi <b>115</b>.{IMG_CREDIT}</p>
<div class="ftr-bot"><span>© {year} {SITE['name']} · giacngungon.org</span><a href="#top">Lên đầu trang ↑</a></div>
</div></footer>
<a class="fab" href="{SITE['zalo']}" target="_blank" rel="noopener" aria-label="Chat Zalo với phòng khám">{icon('chat',22)}<span>Zalo</span></a>
<script src="/assets/js/config.js?v={BUILD_V}"></script>
<script src="/assets/js/main.js?v={BUILD_V}"></script>
</body></html>"""

def card(a, size="md", lazy=True):
    c = CATEGORIES[a["category"]]
    return (f'<article class="card"><a href="/{a["slug"]}/" class="card-a">{athumb(a, size, lazy)}'
            f'<div class="card-b"><span class="tag" style="--c:{c["color"]}">{c["name"]}</span>'
            f'<h3>{esc(a["title"])}</h3><p>{esc(a["description"])}</p>'
            f'<span class="meta">{a["minutes"]} phút đọc</span></div></a></article>')

def cta_band(cat=None):
    h, p = CATEGORIES.get(cat, {}).get("cta") or ("Mất ngủ kéo dài hơn 3 tuần?", "Đừng tự chịu đựng. Gặp bác sĩ chuyên khoa để tìm đúng nguyên nhân và có phác đồ phù hợp với bạn.")
    return f"""<section class="cta-band"><div class="wrap cta-in">
<div><h2>{h}</h2><p>{p}</p></div>
<div class="cta-btns"><a class="btn btn-gold btn-lg" href="/lien-he/">{icon('calendar',18)} Đặt lịch khám</a>
<a class="btn btn-ghost-light btn-lg" href="tel:{SITE['phone_raw']}">{icon('phone',18)} {SITE['phone']}</a></div>
</div></section>"""

def write(path, content):
    out = DIST / path.lstrip("/")
    if path.endswith("/"):
        out = out / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")

# ------------------------------------------------------------------ TRANG CHỦ
def page_home(arts):
    feat = sorted([a for a in arts if a["featured"]], key=lambda a: a["featured"] if isinstance(a["featured"], int) and not isinstance(a["featured"], bool) else 99)[:3] or arts[:3]
    main_f, side_f = feat[0], feat[1:3]
    intents = [
        ("moon", "Tôi bị mất ngủ", "/dau-hieu-mat-ngu/"),
        ("zap", "Tôi muốn ngủ nhanh hơn", "/20-cach-ngu-ngon-va-sau/"),
        ("snore", "Tôi ngáy / ngưng thở khi ngủ", "/ngung-tho-khi-ngu/"),
        ("check", "Làm bài kiểm tra giấc ngủ", "/cong-cu/kiem-tra-giac-ngu/"),
        ("clock", "Tính giờ đi ngủ – thức dậy", "/cong-cu/tinh-gio-ngu/"),
        ("stetho", "Tôi muốn gặp bác sĩ", "/lien-he/"),
    ]
    tiles = "".join(f'<a class="intent" href="{u}">{icon(i,26)}<span>{t}</span>{icon("arrow",18,"ic arr")}</a>' for i, t, u in intents)

    tabs, panels = "", ""
    for i, (k, c) in enumerate(CATEGORIES.items()):
        lst = [a for a in arts if a["category"] == k][:4]
        sel = "true" if i == 0 else "false"
        tabs += f'<button role="tab" aria-selected="{sel}" data-tab="{k}" style="--c:{c["color"]}">{c["name"]}</button>'
        big, rest = lst[0], lst[1:]
        small = "".join(f'<a class="mini" href="/{a["slug"]}/">{athumb(a,"sm")}<span><b>{esc(a["title"])}</b><small>{a["minutes"]} phút đọc</small></span></a>' for a in rest)
        panels += (f'<div class="tabpanel" role="tabpanel" data-panel="{k}" {"hidden" if i else ""}>'
                   f'<div class="latest">{card(big, "lg")}<div class="mini-list">{small}'
                   f'<a class="more" href="/chuyen-muc/{k}/">Xem tất cả bài về {c["name"].lower()} →</a></div></div></div>')

    risk = [
        ("Phụ nữ tiền mãn kinh", "Suy giảm estrogen, bốc hỏa, đổ mồ hôi đêm và thay đổi tâm lý khiến giấc ngủ chập chờn.", "/mat-ngu-tien-man-kinh/"),
        ("Phụ nữ mang thai", "Thay đổi nội tiết, khó tìm tư thế, tiểu đêm và lo âu làm mẹ bầu khó ngủ sâu.", "/mat-ngu-khi-mang-thai/"),
        ("Người trên 60 tuổi", "Giấc ngủ nông hơn, dễ thức giấc, kèm các bệnh mạn tính và thuốc điều trị.", "/nhung-cach-cai-thien-chat-luong-giac-ngu-cho-tuoi-gia/"),
        ("Người căng thẳng, lo âu", "Não bộ “không chịu tắt” vì công việc, tiền bạc, các mối quan hệ hay bệnh tật.", "/mat-ngu-do-lo-au-cang-thang/"),
    ]
    risk_html = "".join(f'<a class="risk" href="{u}"><span class="risk-n">0{i+1}</span><h3>{t}</h3><p>{d}</p><span class="link">Tìm hiểu →</span></a>' for i, (t, d, u) in enumerate(risk))

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "name": SITE["name"], "url": SITE["domain"] + "/", "inLanguage": "vi"},
        {"@type": "MedicalClinic", "name": "Phòng khám Giấc Ngủ Ngon", "url": SITE["domain"] + "/",
         "telephone": "+84" + SITE["phone_raw"][1:], "medicalSpecialty": "Psychiatric",
         "employee": {"@type": "Physician", "name": SITE["doctor"].replace("Bs. ", "")}}]}

    body = f"""
<section class="banner" aria-label="Làm thế nào để có một giấc ngủ ngon?">
<img src="/assets/img/banner.webp" srcset="/assets/img/banner-sm.webp 960w, /assets/img/banner.webp 1901w" sizes="100vw" alt="" width="1901" height="877" fetchpriority="high" decoding="async">
<div class="wrap banner-in"><p class="banner-q"><svg class="banner-mark" viewBox="0 0 64 52" aria-hidden="true"><path d="M0 52V30Q0 8 22 0l4 7Q13 13 13 25h13v27zm38 0V30q0-22 22-30l4 7q-13 6-13 18h13v27z"/></svg>Làm thế nào để có<br>một giấc ngủ ngon?</p></div>
</section>
<section class="hero"><div class="wrap hero-in">
<div class="hero-t"><p class="eyebrow">{icon('moon',16)} giacngungon.org</p>
<h1>{SITE['tagline']}</h1>
<p class="lead">Kiến thức giấc ngủ dễ hiểu, dựa trên bằng chứng khoa học – cùng bác sĩ chuyên khoa đồng hành khi bạn cần.</p>
<form class="hero-search" action="/blog/" role="search"><input name="q" type="search" placeholder="Bạn đang gặp vấn đề gì về giấc ngủ?" aria-label="Tìm bài viết"><button class="btn btn-gold">{icon('search',18)} Tìm</button></form></div>
<div class="hero-card"><h2>Bạn cần giúp gì để ngủ ngon hơn?</h2><div class="intents">{tiles}</div></div>
</div><div class="hero-stars" aria-hidden="true"></div></section>

<section class="sec"><div class="wrap">
<div class="sec-h"><h2>Bài viết nổi bật</h2><a href="/blog/" class="link">Tất cả bài viết →</a></div>
<div class="feat">
<a class="feat-main" href="/{main_f['slug']}/">{athumb(main_f,'xl')}<div><span class="tag" style="--c:{CATEGORIES[main_f['category']]['color']}">{CATEGORIES[main_f['category']]['name']}</span><h3>{esc(main_f['title'])}</h3><p>{esc(main_f['description'])}</p><span class="meta">{main_f['minutes']} phút đọc</span></div></a>
<div class="feat-side">{''.join(card(a) for a in side_f)}</div>
</div></div></section>

<section class="facts"><div class="wrap facts-in">
<div class="fact"><b>1/3</b><span>cuộc đời chúng ta dành cho giấc ngủ</span></div>
<div class="fact"><b>7–9 giờ</b><span>là thời lượng ngủ khuyến nghị cho người trưởng thành</span></div>
<div class="fact"><b>~90 phút</b><span>là độ dài trung bình của một chu kỳ ngủ</span></div>
<div class="fact"><b>4–6</b><span>chu kỳ ngủ nối tiếp nhau trong một đêm</span></div>
</div></section>

<section class="sec"><div class="wrap">
<div class="sec-h"><h2>Mới nhất theo chủ đề</h2></div>
<div class="tabs" role="tablist">{tabs}</div>{panels}
</div></section>

<section class="sec sec-soft"><div class="wrap">
<div class="sec-h center"><p class="eyebrow">Ai dễ bị mất ngủ?</p><h2>Những đối tượng cần đặc biệt chú ý</h2></div>
<div class="risks">{risk_html}</div></div></section>

<section class="sec"><div class="wrap doc-sec">
<div class="doc-card"><div class="doc-ava" aria-hidden="true"><img src="/assets/img/logo-icon.png" alt="" width="70" height="70"></div>
<h3>{SITE['doctor']}</h3><p class="doc-t">{SITE['doctor_title']}</p>
<ul class="creds">{''.join(f'<li>{icon("shield",16)}{c}</li>' for c in SITE['doctor_creds'])}</ul>
<a class="btn btn-navy" href="/bac-si/">Xem hồ sơ bác sĩ</a></div>
<div class="steps-wrap"><p class="eyebrow">Quy trình khám &amp; điều trị</p><h2>Ba bước để lấy lại giấc ngủ</h2>
<ol class="steps">
<li><span>1</span><div><h3>Đặt lịch khám</h3><p>Đặt lịch qua website, gọi điện hoặc nhắn Zalo <a href="tel:{SITE['phone_raw']}">{SITE['phone']}</a>. Phòng khám sẽ xác nhận giờ hẹn với bạn.</p></div></li>
<li><span>2</span><div><h3>Bác sĩ khám &amp; tư vấn</h3><p>Bác sĩ trực tiếp lắng nghe, đánh giá giấc ngủ và các yếu tố liên quan, giải đáp lo lắng và đưa ra phương án điều trị phù hợp nhất cho bạn.</p></div></li>
<li><span>3</span><div><h3>Theo dõi sau khám</h3><p>Bác sĩ tiếp tục theo dõi mức độ cải thiện để điều chỉnh phác đồ, giúp bạn ngủ tốt bền vững – không phụ thuộc thuốc.</p></div></li>
</ol><a class="btn btn-gold" href="/lien-he/">{icon('calendar',18)} Đặt lịch ngay</a></div>
</div></section>

<section class="sec sec-soft"><div class="wrap tools">
<a class="tool" href="/cong-cu/tinh-gio-ngu/"><div class="tool-ic">{icon('clock',30)}</div><div><h3>Máy tính giờ ngủ</h3><p>Nên đi ngủ lúc mấy giờ để thức dậy tỉnh táo? Tính theo chu kỳ ngủ 90 phút.</p><span class="link">Dùng ngay →</span></div></a>
<a class="tool" href="/cong-cu/kiem-tra-giac-ngu/"><div class="tool-ic">{icon('check',30)}</div><div><h3>Kiểm tra giấc ngủ của bạn</h3><p>8 câu hỏi, 2 phút – biết giấc ngủ của bạn đang ở mức nào và khi nào nên đi khám.</p><span class="link">Làm bài →</span></div></a>
</div></section>
{cta_band()}
"""
    return head(SITE["name"], "Giấc Ngủ Ngon – kiến thức về mất ngủ, rối loạn giấc ngủ và cách ngủ ngon dựa trên bằng chứng; đặt lịch khám với bác sĩ chuyên khoa giấc ngủ.", "/", ld) + header(ARTS) + body + footer()

# ------------------------------------------------------------------ BÀI VIẾT
def page_article(a, arts):
    c = CATEGORIES[a["category"]]
    path = f"/{a['slug']}/"
    related = [x for x in arts if x["category"] == a["category"] and x["slug"] != a["slug"]][:3]
    if len(related) < 3:
        related += [x for x in arts if x["slug"] != a["slug"] and x not in related][:3 - len(related)]
    toc = "".join(f'<li><a href="#{i}">{esc(n)}</a></li>' for i, n in a["toc"])
    key = ""
    if a["key"]:
        key = '<aside class="keybox"><h2>Những điểm chính</h2><ul>' + "".join(f"<li>{esc(k)}</li>" for k in a["key"]) + "</ul></aside>"
    src = ""
    if a["sources"]:
        src = ('<details class="sources"><summary>Nguồn tham khảo (' + str(len(a["sources"])) + ')</summary><ol>'
               + "".join(f"<li>{esc(s)}</li>" for s in a["sources"]) + "</ol></details>")
    reviewer = ""
    if a["reviewed"]:
        reviewer = f'<span class="byl">{icon("shield",16)} Tham vấn y khoa: <a href="/bac-si/">{SITE["doctor"]}</a></span>'
    ld = {"@context": "https://schema.org", "@type": "MedicalWebPage", "headline": a["title"],
          "description": a["description"], "inLanguage": "vi", "url": SITE["domain"] + path,
          "datePublished": a["date"].isoformat(), "dateModified": a["updated"].isoformat(),
          "publisher": {"@type": "Organization", "name": SITE["name"], "url": SITE["domain"]},
          "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
              {"@type": "ListItem", "position": 1, "name": "Trang chủ", "item": SITE["domain"] + "/"},
              {"@type": "ListItem", "position": 2, "name": c["name"], "item": f"{SITE['domain']}/chuyen-muc/{a['category']}/"},
              {"@type": "ListItem", "position": 3, "name": a["title"]}]}}
    fig = (f'<figure class="art-img"><img src="{a["img_w"]}" srcset="{a["img_t"]} {a["img_t_w"]}w, {a["img_w"]} {a["img_w_w"]}w" '
           f'sizes="(max-width:900px) 92vw, 820px" alt="{esc(a.get("image_alt") or a["title"])}" width="{a["img_w_w"]}" height="{a["img_w_h"]}" '
           f'fetchpriority="high" decoding="async"></figure>') if a.get("img") else ""
    if a.get("img"):
        ld["image"] = SITE["domain"] + a["img"]
    if a["reviewed"]:
        ld["reviewedBy"] = {"@type": "Physician", "name": SITE["doctor"].replace("Bs. ", "")}
    body = f"""
<div class="art-hero" style="--c:{c['color']}"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Trang chủ</a><span>›</span><a href="/chuyen-muc/{a['category']}/">{c['name']}</a></nav>
<h1>{esc(a['title'])}</h1><p class="dek">{esc(a['description'])}</p>
<div class="bylines"><span class="byl">{icon('leaf',16)} Biên soạn: Ban biên tập Giấc Ngủ Ngon</span>{reviewer}
<span class="byl">{icon('calendar',16)} Cập nhật: {fmt_date(a['updated'])}</span><span class="byl">{icon('clock',16)} {a['minutes']} phút đọc</span></div>
</div></div>
<div class="wrap art-grid">
<article class="prose">
{fig}
{key}
{a['html']}
<div class="disc">{icon('shield',18)}<p>Bài viết mang tính chất tham khảo, không thay thế chẩn đoán và điều trị của bác sĩ. Hãy trao đổi với bác sĩ trước khi dùng bất kỳ loại thuốc hay thực phẩm chức năng nào.</p></div>
{src}
</article>
<aside class="side">
<div class="side-box toc"><h2>Trong bài này</h2><ol>{toc}</ol></div>
<div class="side-box side-cta"><h2>Cần bác sĩ tư vấn?</h2><p>{c.get("side", "Khám và điều trị mất ngủ, rối loạn giấc ngủ với")} {SITE['doctor']}.</p>
<a class="btn btn-gold btn-block" href="/lien-he/">{icon('calendar',17)} Đặt lịch khám</a><a class="btn btn-ghost btn-block" href="tel:{SITE['phone_raw']}">{icon('phone',17)} {SITE['phone']}</a></div>
</aside></div>
<section class="sec sec-soft"><div class="wrap"><div class="sec-h"><h2>Bài viết liên quan</h2><a class="link" href="/chuyen-muc/{a['category']}/">Thêm về {c['name'].lower()} →</a></div>
<div class="grid3">{''.join(card(x) for x in related)}</div></div></section>
{cta_band(a['category'])}
"""
    return head(a["title"], a["description"], path, ld, "article", a.get("img")) + header(arts) + body + footer()

# ------------------------------------------------------------------ CHUYÊN MỤC & BLOG
def page_category(k, arts):
    c = CATEGORIES[k]
    lst = [a for a in arts if a["category"] == k]
    others = "".join(f'<a class="chip" href="/chuyen-muc/{kk}/" style="--c:{cc["color"]}">{cc["name"]}</a>' for kk, cc in CATEGORIES.items() if kk != k)
    body = f"""
<div class="cat-hero" style="--c:{c['color']}"><div class="wrap"><nav class="crumbs"><a href="/">Trang chủ</a><span>›</span><a href="/blog/">Bài viết</a></nav>
<div class="cat-hero-in"><div class="cat-ic">{icon(c['icon'],40)}</div><div><h1>{c['name']}</h1><p class="dek">{c['desc']}</p><span class="meta light">{len(lst)} bài viết</span></div></div></div></div>
<section class="sec"><div class="wrap"><div class="grid3">{''.join(card(a, lazy=i >= 3) for i, a in enumerate(lst))}</div>
<div class="chips-row"><span>Chủ đề khác:</span>{others}</div></div></section>{cta_band(k)}"""
    return head(c["name"], c["desc"], f"/chuyen-muc/{k}/") + header(arts) + body + footer()

def page_blog(arts):
    chips = '<button class="chip on" data-f="all">Tất cả</button>' + "".join(
        f'<button class="chip" data-f="{k}" style="--c:{c["color"]}">{c["name"]}</button>' for k, c in CATEGORIES.items())
    cards = "".join(f'<div class="bi" data-cat="{a["category"]}" data-s="{esc(strip_accents((a["title"]+" "+a["description"]).lower()))}">{card(a, lazy=i >= 3)}</div>' for i, a in enumerate(arts))
    body = f"""
<div class="cat-hero" style="--c:#4a6441"><div class="wrap"><nav class="crumbs"><a href="/">Trang chủ</a></nav>
<h1>Thư viện kiến thức giấc ngủ</h1><p class="dek">{len(arts)} bài viết về mất ngủ, rối loạn giấc ngủ, sức khỏe tâm thần và cách ngủ ngon – được biên soạn dễ hiểu, dựa trên các hướng dẫn y khoa.</p></div></div>
<section class="sec"><div class="wrap">
<div class="filter"><div class="chips">{chips}</div><label class="fsearch">{icon('search',18)}<input id="blogQ" type="search" placeholder="Lọc theo từ khóa…" aria-label="Lọc bài viết"></label></div>
<div class="grid3" id="blogGrid">{cards}</div><p id="blogEmpty" class="empty" hidden>Không tìm thấy bài phù hợp. Thử từ khóa khác nhé.</p>
</div></section>{cta_band()}"""
    return head("Bài viết", "Thư viện bài viết về mất ngủ, rối loạn giấc ngủ, cách cải thiện giấc ngủ và giấc ngủ theo từng đối tượng.", "/blog/") + header(arts) + body + footer()

# ------------------------------------------------------------------ TRANG TĨNH
def simple_page(title, desc, path, inner, arts, hero_color="#4a6441", dek=""):
    body = f"""<div class="cat-hero" style="--c:{hero_color}"><div class="wrap"><nav class="crumbs"><a href="/">Trang chủ</a></nav>
<h1>{title}</h1>{f'<p class="dek">{dek}</p>' if dek else ''}</div></div>{inner}"""
    return head(title, desc, path) + header(arts) + body + footer()

def page_calc(arts):
    inner = f"""<section class="sec"><div class="wrap narrow">
<div class="tool-card" id="calc">
<div class="seg" role="tablist"><button class="on" data-mode="wake" role="tab">Tôi muốn thức dậy lúc…</button><button data-mode="sleep" role="tab">Tôi sẽ đi ngủ lúc…</button></div>
<div class="calc-row"><label for="calcTime" id="calcLabel">Giờ thức dậy</label>
<input type="time" id="calcTime" value="06:00"><button class="btn btn-gold" id="calcNow" type="button">Đi ngủ ngay bây giờ</button></div>
<div id="calcOut" class="calc-out" aria-live="polite"></div>
</div>
<div class="prose narrow-prose">
<h2>Máy tính giờ ngủ hoạt động thế nào?</h2>
<p>Mỗi đêm, giấc ngủ đi qua nhiều <b>chu kỳ</b>, mỗi chu kỳ trung bình khoảng <b>90 phút</b> (dao động 70–120 phút tùy người) gồm ngủ nông, ngủ sâu và ngủ REM. Thức dậy ở cuối một chu kỳ – khi bạn đang ngủ nông – thường dễ chịu hơn so với bị đánh thức giữa giai đoạn ngủ sâu.</p>
<p>Công cụ cộng thêm khoảng <b>15 phút</b> để đi vào giấc ngủ, rồi tính ngược/xuôi theo bội số của 90 phút. Người trưởng thành nên nhắm tới <b>5–6 chu kỳ</b> (7,5–9 giờ).</p>
<blockquote><p><b>Lưu ý:</b> Đây là ước tính trung bình. Nếu bạn thường xuyên mất hơn 30 phút mới ngủ được, hay thức giấc nhiều lần trong đêm, hãy đọc <a href="/dau-hieu-mat-ngu/">dấu hiệu mất ngủ</a> hoặc <a href="/lien-he/">đặt lịch gặp bác sĩ</a>.</p></blockquote>
<p>Tìm hiểu thêm: <a href="/cac-giai-doan-giac-ngu/">Các giai đoạn của giấc ngủ</a> · <a href="/can-ngu-bao-nhieu-tieng/">Cần ngủ bao nhiêu tiếng mỗi ngày?</a></p>
</div></div></section>"""
    return simple_page("Máy tính giờ ngủ", "Nên đi ngủ lúc mấy giờ để thức dậy tỉnh táo? Công cụ tính giờ đi ngủ và giờ thức dậy theo chu kỳ ngủ 90 phút.",
                       "/cong-cu/tinh-gio-ngu/", inner, arts, "#4f7392", "Nên đi ngủ lúc mấy giờ để sáng dậy tỉnh táo? Tính theo chu kỳ ngủ 90 phút.")

QUIZ = [
    ("Bạn thường mất bao lâu để chìm vào giấc ngủ?", ["Dưới 20 phút", "20–30 phút", "30–60 phút", "Trên 60 phút"]),
    ("Bạn thức giấc giữa đêm và khó ngủ lại bao nhiêu đêm mỗi tuần?", ["Hầu như không", "1–2 đêm", "3–4 đêm", "5 đêm trở lên"]),
    ("Bạn có thức dậy sớm hơn dự định mà không ngủ lại được?", ["Không bao giờ", "Thỉnh thoảng", "Thường xuyên", "Gần như mỗi ngày"]),
    ("Trung bình bạn ngủ được bao nhiêu tiếng mỗi đêm?", ["7 tiếng trở lên", "6–7 tiếng", "5–6 tiếng", "Dưới 5 tiếng"]),
    ("Ban ngày bạn thấy mệt mỏi, buồn ngủ hoặc khó tập trung ở mức nào?", ["Không có", "Nhẹ", "Rõ rệt", "Rất nhiều, ảnh hưởng công việc"]),
    ("Bạn lo lắng, căng thẳng về chuyện ngủ không được ở mức nào?", ["Không lo", "Hơi lo", "Khá lo", "Rất lo, sợ đến giờ đi ngủ"]),
    ("Tình trạng ngủ kém của bạn đã kéo dài bao lâu?", ["Không có vấn đề", "Dưới 1 tháng", "1–3 tháng", "Trên 3 tháng"]),
    ("Bạn có đang dùng thuốc ngủ, rượu hoặc thuốc an thần để dễ ngủ?", ["Không", "Hiếm khi", "Vài lần mỗi tuần", "Gần như mỗi đêm"]),
]

def page_quiz(arts):
    qs = ""
    for i, (q, opts) in enumerate(QUIZ):
        o = "".join(f'<label class="opt"><input type="radio" name="q{i}" value="{v}" required><span>{esc(t)}</span></label>' for v, t in enumerate(opts))
        qs += f'<fieldset class="q"><legend><span>{i+1}</span>{esc(q)}</legend><div class="opts">{o}</div></fieldset>'
    inner = f"""<section class="sec"><div class="wrap narrow">
<form class="tool-card" id="quiz"><div class="quiz-prog"><div id="quizBar"></div></div>{qs}
<button class="btn btn-gold btn-lg btn-block" type="submit">Xem kết quả</button></form>
<div id="quizOut" class="quiz-out" hidden aria-live="polite"></div>
<p class="small-note">Bài tự đánh giá do Ban biên tập Giấc Ngủ Ngon xây dựng để tham khảo nhanh, không phải công cụ chẩn đoán. Kết quả không được lưu hay gửi đi đâu.</p>
</div></section>"""
    return simple_page("Kiểm tra giấc ngủ của bạn", "Bài tự đánh giá giấc ngủ 8 câu hỏi: biết giấc ngủ của bạn đang ở mức nào và khi nào nên đi khám bác sĩ.",
                       "/cong-cu/kiem-tra-giac-ngu/", inner, arts, "#3f7f78", "8 câu hỏi – khoảng 2 phút. Trả lời dựa trên tình trạng của bạn trong 2 tuần gần đây.")

def page_doctor(arts):
    inner = f"""<section class="sec"><div class="wrap doc-page">
<div class="doc-card big"><div class="doc-ava" aria-hidden="true"><img src="/assets/img/logo-icon.png" alt="" width="84" height="84"></div><h2>{SITE['doctor']}</h2><p class="doc-t">{SITE['doctor_title']}</p>
<ul class="creds">{''.join(f'<li>{icon("shield",16)}{c}</li>' for c in SITE['doctor_creds'])}</ul>
<a class="btn btn-gold btn-block" href="/lien-he/">{icon('calendar',18)} Đặt lịch khám</a><a class="btn btn-ghost btn-block" href="tel:{SITE['phone_raw']}">{icon('phone',18)} {SITE['phone']}</a></div>
<div class="prose">
<h2>Phòng khám giúp gì cho bạn?</h2>
<p>Mất ngủ hiếm khi chỉ là “khó ngủ”. Phía sau có thể là căng thẳng kéo dài, lo âu, trầm cảm, thay đổi nội tiết, đau mạn tính, ngưng thở khi ngủ hay thói quen sinh hoạt chưa phù hợp. Vì vậy, điều trị hiệu quả bắt đầu từ việc <b>tìm đúng nguyên nhân</b>.</p>
<ul><li>Khám và điều trị mất ngủ cấp tính, mất ngủ mạn tính</li><li>Rối loạn giấc ngủ do lo âu, căng thẳng, trầm cảm</li><li>Tư vấn và điều trị các vấn đề sức khỏe tâm thần: <a href="/roi-loan-lo-au/">lo âu</a>, <a href="/roi-loan-tram-cam/">trầm cảm</a>, <a href="/roi-loan-stress-sau-sang-chan/">sang chấn tâm lý</a>, <a href="/roi-loan-luong-cuc/">lưỡng cực</a>, <a href="/roi-loan-am-anh-cuong-che/">ám ảnh cưỡng chế</a>…</li><li>Mất ngủ ở phụ nữ mang thai, tiền mãn kinh, người cao tuổi</li><li>Tư vấn các rối loạn giấc ngủ khác: ngủ rũ, chân không yên, ác mộng, mộng du…</li><li>Hướng dẫn giảm dần và ngưng thuốc ngủ an toàn khi đã dùng lâu</li></ul>
<h2>Quy trình khám</h2>
<ol><li><b>Đặt lịch:</b> qua <a href="/lien-he/">form đặt lịch</a>, điện thoại hoặc Zalo {SITE['phone']}.</li>
<li><b>Khám &amp; tư vấn:</b> bác sĩ hỏi kỹ về giấc ngủ, sức khỏe, tâm lý, thuốc đang dùng; có thể đề nghị bạn ghi <a href="/ve-sinh-giac-ngu/">nhật ký giấc ngủ</a> 1–2 tuần.</li>
<li><b>Điều trị:</b> kết hợp điều chỉnh thói quen, liệu pháp nhận thức – hành vi cho mất ngủ (CBT-I) và thuốc khi cần thiết, theo đúng chỉ định.</li>
<li><b>Theo dõi:</b> tái khám để đánh giá tiến triển và điều chỉnh phác đồ.</li></ol>
<h2>Nên chuẩn bị gì trước khi đi khám?</h2>
<ul><li>Các thuốc, thực phẩm chức năng bạn đang dùng (mang theo vỏ hộp hoặc toa thuốc).</li><li>Kết quả xét nghiệm, toa thuốc cũ nếu có.</li><li>Ghi lại giờ đi ngủ, giờ thức dậy, số lần thức giấc trong khoảng 1 tuần gần nhất.</li><li>Nếu có thể, hỏi người ngủ cùng xem bạn có ngáy to, ngừng thở hay cử động bất thường khi ngủ không.</li></ul>
</div></div></section>{cta_band()}"""
    return simple_page("Bác sĩ & quy trình khám", f"{SITE['doctor']} – {SITE['doctor_title']}. Khám và điều trị mất ngủ, rối loạn giấc ngủ.", "/bac-si/", inner, arts, "#273a24",
                       "Khám và điều trị mất ngủ, rối loạn giấc ngủ – lắng nghe, tìm đúng nguyên nhân, điều trị bền vững.")

def page_contact(arts):
    inner = f"""<section class="sec"><div class="wrap contact">
<form class="tool-card" id="bookForm" novalidate>
<h2>Đặt lịch khám</h2><p class="muted">Để lại thông tin, phòng khám sẽ liên hệ xác nhận lịch hẹn với bạn.</p>
<div class="fgrid">
<label>Họ và tên *<input name="ho_ten" required autocomplete="name"></label>
<label>Số điện thoại *<input name="so_dien_thoai" type="tel" required autocomplete="tel" pattern="[0-9 .+]{{9,15}}"></label>
<label>Email<input name="email" type="email" autocomplete="email"></label>
<label>Ngày muốn khám<input name="ngay_hen" type="date"></label>
<label class="full">Địa chỉ<input name="dia_chi" autocomplete="street-address"></label>
<label class="full">Tình trạng / lời nhắn<textarea name="loi_nhan" rows="4" placeholder="Ví dụ: khó ngủ khoảng 2 tháng, thường thức giấc lúc 2–3 giờ sáng…"></textarea></label>
</div>
<input type="text" name="_gotcha" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
<button class="btn btn-gold btn-lg btn-block" type="submit">Gửi yêu cầu đặt lịch</button>
<div id="formMsg" class="form-msg" role="status" hidden></div>
</form>
<div class="contact-side">
<div class="side-box"><h2>Liên hệ nhanh</h2>
<a class="qc" href="tel:{SITE['phone_raw']}">{icon('phone',22)}<span><b>{SITE['phone']}</b><small>Gọi điện tư vấn &amp; đặt lịch</small></span></a>
<a class="qc" href="{SITE['zalo']}" target="_blank" rel="noopener">{icon('chat',22)}<span><b>Zalo {SITE['phone']}</b><small>Nhắn tin bất cứ lúc nào</small></span></a>
</div>
<div class="side-box"><h2>Bác sĩ phụ trách</h2><p><b>{SITE['doctor']}</b><br>{SITE['doctor_title']}</p><a class="link" href="/bac-si/">Xem hồ sơ →</a></div>
<div class="side-box warn"><p><b>Trường hợp khẩn cấp</b> (khó thở, đau ngực, có ý nghĩ tự làm hại bản thân…) hãy gọi <b>115</b> hoặc đến cơ sở y tế gần nhất.</p></div>
</div></div></section>"""
    return simple_page("Liên hệ & đặt lịch khám", "Đặt lịch khám mất ngủ, rối loạn giấc ngủ với bác sĩ chuyên khoa. Hotline/Zalo 0901.312.129.", "/lien-he/", inner, arts, "#273a24",
                       f"Gọi hoặc nhắn Zalo {SITE['phone']}, hoặc để lại thông tin bên dưới.")

def page_policy(arts):
    inner = f"""<section class="sec"><div class="wrap narrow"><div class="prose">
<h2>Sứ mệnh</h2><p>Giấc Ngủ Ngon mong muốn mang đến kiến thức về giấc ngủ <b>chính xác, dễ hiểu và hữu ích</b> cho người Việt, để bạn hiểu cơ thể mình và biết khi nào cần tìm sự giúp đỡ của bác sĩ.</p>
<h2>Cách chúng tôi biên soạn nội dung</h2>
<ul><li>Nội dung dựa trên hướng dẫn của các tổ chức y khoa uy tín (Viện Y học Giấc ngủ Hoa Kỳ – AASM, Viện Y tế Quốc gia Hoa Kỳ – NIH, Tổ chức Y tế Thế giới – WHO, Bộ Y tế Việt Nam…) và các nghiên cứu đã được bình duyệt.</li>
<li>Mỗi bài có mục “Nguồn tham khảo” để bạn tự kiểm chứng.</li>
<li>Bài viết được rà soát và cập nhật định kỳ; ngày cập nhật được ghi rõ ở đầu bài.</li>
<li>Những bài có dòng “Tham vấn y khoa” đã được bác sĩ đọc và góp ý chuyên môn.</li>
<li>Chúng tôi không nêu liều dùng thuốc cụ thể – việc dùng thuốc cần có chỉ định của bác sĩ.</li></ul>
<h2>Miễn trừ trách nhiệm</h2><p>Thông tin trên website chỉ mang tính tham khảo, không thay thế cho việc khám, chẩn đoán hoặc điều trị y khoa. Không tự ý bắt đầu, thay đổi hay ngưng thuốc dựa trên nội dung bài viết.</p>
<h2>Góp ý &amp; báo lỗi</h2><p>Nếu phát hiện thông tin chưa chính xác, vui lòng <a href="/lien-he/">liên hệ</a> hoặc nhắn Zalo {SITE['phone']}. Chúng tôi trân trọng mọi góp ý.</p>
</div></div></section>"""
    return simple_page("Chính sách biên tập", "Cách Giấc Ngủ Ngon biên soạn, kiểm duyệt và cập nhật nội dung sức khỏe giấc ngủ.", "/chinh-sach-bien-tap/", inner, arts, "#273a24")

def page_404(arts):
    inner = f"""<section class="sec"><div class="wrap narrow center"><p class="big404">404</p><h2>Trang này đã “đi ngủ” mất rồi</h2>
<p class="muted">Có thể đường dẫn đã thay đổi. Hãy thử tìm bài viết bạn cần:</p>
<p><a class="btn btn-gold" href="/blog/">Xem tất cả bài viết</a> <a class="btn btn-ghost" href="/">Về trang chủ</a></p></div></section>"""
    return head("Không tìm thấy trang", "Không tìm thấy trang", "/404.html") + header(arts) + inner + footer()

# ------------------------------------------------------------------ BUILD
IMG_CREDIT = ""
IMG_MAX, IMG_Q = 1400, 80   # kích thước tối đa & chất lượng JPEG ảnh bài viết
BUILD_V = datetime.datetime.now().strftime("%Y%m%d%H%M")
ARTS = []

def main():
    global ARTS, IMG_CREDIT
    ARTS = load_articles()
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)
    # ảnh bài viết: content/images/<file> -> dist/assets/img/bai/<slug>.jpg (1400px) + <slug>-t.jpg (640px)
    out = DIST / "assets/img/bai"; out.mkdir(parents=True, exist_ok=True); n_img = 0
    for a in ARTS:
        src = CONTENT / "images" / str(a.get("image") or "")
        if not a.get("image") or not src.is_file():
            if a.get("image"): print(f"  ! Thiếu ảnh {src.name} cho bài {a['slug']} → dùng hình minh họa")
            continue
        # ảnh trong bài: nén JPEG, tối đa 1400px (IMG_MAX, IMG_Q chỉnh ở đầu file)
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB"); im.thumbnail((IMG_MAX, IMG_MAX), Image.LANCZOS)
        im.save(out / f"{a['slug']}.jpg", quality=IMG_Q, optimize=True, progressive=True)
        w, h = im.size
        a["img"] = f"/assets/img/bai/{a['slug']}.jpg"
        # bản WebP (nhẹ hơn JPEG ~30%) dùng để hiển thị; JPEG ở trên giữ cho ảnh chia sẻ Facebook/Zalo
        im.save(out / f"{a['slug']}.webp", "WEBP", quality=IMG_Q, method=6)
        a["img_w"], a["img_w_w"], a["img_w_h"] = f"/assets/img/bai/{a['slug']}.webp", w, h
        # ảnh thẻ bài viết: 720px và 360px (trình duyệt tự chọn bản vừa đủ theo màn hình)
        for suffix, px, key in (("-the", 720, "img_t"), ("-nho", 360, "img_s")):
            th = im.copy(); th.thumbnail((px, px), Image.LANCZOS)
            th.save(out / f"{a['slug']}{suffix}.webp", "WEBP", quality=76, method=6)
            a[key], a[key + "_w"], a[key + "_h"] = f"/assets/img/bai/{a['slug']}{suffix}.webp", th.size[0], th.size[1]
        n_img += 1
    if n_img:
        IMG_CREDIT = " Một số hình ảnh: Freepik."
    print(f"  Ảnh bài viết: {n_img}")
    write("/", page_home(ARTS))
    for a in ARTS:
        write(f"/{a['slug']}/", page_article(a, ARTS))
    for k in CATEGORIES:
        write(f"/chuyen-muc/{k}/", page_category(k, ARTS))
    write("/blog/", page_blog(ARTS))
    write("/cong-cu/tinh-gio-ngu/", page_calc(ARTS))
    write("/cong-cu/kiem-tra-giac-ngu/", page_quiz(ARTS))
    write("/bac-si/", page_doctor(ARTS))
    write("/lien-he/", page_contact(ARTS))
    write("/chinh-sach-bien-tap/", page_policy(ARTS))
    (DIST / "404.html").write_text(page_404(ARTS), encoding="utf-8")

    # chỉ mục tìm kiếm
    idx = [{"t": a["title"], "d": a["description"], "u": f"/{a['slug']}/", "c": CATEGORIES[a["category"]]["name"],
            "s": strip_accents((a["title"] + " " + a["description"] + " " + " ".join(a["key"])).lower())} for a in ARTS]
    idx += [{"t": "Máy tính giờ ngủ", "d": "Tính giờ đi ngủ, giờ thức dậy theo chu kỳ 90 phút", "u": "/cong-cu/tinh-gio-ngu/", "c": "Công cụ", "s": "may tinh gio ngu chu ky thuc day di ngu"},
            {"t": "Kiểm tra giấc ngủ", "d": "Bài tự đánh giá giấc ngủ 8 câu", "u": "/cong-cu/kiem-tra-giac-ngu/", "c": "Công cụ", "s": "kiem tra giac ngu trac nghiem danh gia mat ngu"}]
    (DIST / "search.json").write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")

    # sitemap & robots
    today = datetime.date.today().isoformat()
    urls = [("/", today), ("/blog/", today), ("/bac-si/", today), ("/lien-he/", today), ("/chinh-sach-bien-tap/", today),
            ("/cong-cu/tinh-gio-ngu/", today), ("/cong-cu/kiem-tra-giac-ngu/", today)]
    urls += [(f"/chuyen-muc/{k}/", today) for k in CATEGORIES]
    urls += [(f"/{a['slug']}/", a["updated"].isoformat()) for a in ARTS]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"<url><loc>{SITE['domain']}{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    (DIST / "sitemap.xml").write_text(sm, encoding="utf-8")
    # bộ nhớ đệm trình duyệt (Cloudflare đọc file _headers): CSS/JS đã có ?v= nên lưu lâu được
    (DIST / "_headers").write_text(
        "/assets/css/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/assets/js/*\n  Cache-Control: public, max-age=31536000, immutable\n"
        "/assets/img/*\n  Cache-Control: public, max-age=2592000\n"
        "/search.json\n  Cache-Control: public, max-age=3600\n", encoding="utf-8")
    # cấu hình cho hosting Apache/cPanel (iNET…): HTTPS, trang 404, nén gzip, bộ nhớ đệm, kiểu file WebP
    (DIST / ".htaccess").write_text("""# Giấc Ngủ Ngon – cấu hình Apache (tự sinh bởi build.py)
Options -Indexes
DirectoryIndex index.html
ErrorDocument 404 /404.html

<IfModule mod_rewrite.c>
RewriteEngine On
# Chuyển http -> https (chỉ áp dụng cho tên miền thật; địa chỉ tạm của hosting vẫn chạy http)
RewriteCond %{HTTP_HOST} giacngungon\\.org$ [NC]
RewriteCond %{HTTPS} off
RewriteCond %{HTTP:X-Forwarded-Proto} !https
RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]
# Bỏ www (giacngungon.org là địa chỉ chính)
RewriteCond %{HTTP_HOST} ^www\\.(giacngungon\\.org)$ [NC]
RewriteRule ^ https://%1%{REQUEST_URI} [L,R=301]
# Thêm dấu / cuối cho đường dẫn thư mục bài viết
RewriteCond %{REQUEST_FILENAME} -d
RewriteCond %{REQUEST_URI} !/$
RewriteRule ^(.*)$ /$1/ [L,R=301]
</IfModule>

AddType image/webp .webp
AddType application/json .json

<IfModule mod_deflate.c>
AddOutputFilterByType DEFLATE text/html text/css application/javascript text/javascript application/json image/svg+xml text/xml application/xml text/plain
</IfModule>

<IfModule mod_expires.c>
ExpiresActive On
ExpiresByType text/html "access plus 0 seconds"
ExpiresByType text/css "access plus 1 year"
ExpiresByType application/javascript "access plus 1 year"
ExpiresByType text/javascript "access plus 1 year"
ExpiresByType image/webp "access plus 30 days"
ExpiresByType image/jpeg "access plus 30 days"
ExpiresByType image/png "access plus 30 days"
ExpiresByType application/json "access plus 1 hour"
</IfModule>
""", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n", encoding="utf-8")
    print(f"✔ Đã build {len(ARTS)} bài viết, {len(urls)} URL → {DIST}")

if __name__ == "__main__":
    main()
