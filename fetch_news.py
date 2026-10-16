#!/usr/bin/env python3
"""RSS kaynaklarından haberleri çekip news.json dosyasına yazar.
Sadece Python standart kütüphanesi kullanır, ek kurulum gerekmez."""
import json, re, html, sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

# (kaynak adı, kategori, rss adresi) -> istediğin kadar ekle/çıkar
FEEDS = [
    ("AA", "Gündem", "https://www.aa.com.tr/tr/rss/default?cat=guncel"),
    ("AA", "Ekonomi", "https://www.aa.com.tr/tr/rss/default?cat=ekonomi"),
    ("AA", "Spor", "https://www.aa.com.tr/tr/rss/default?cat=spor"),
    ("AA", "Dünya", "https://www.aa.com.tr/tr/rss/default?cat=dunya"),
    ("TRT Haber", "Gündem", "https://www.trthaber.com/sondakika.rss"),
    ("BBC Türkçe", "Dünya", "https://feeds.bbci.co.uk/turkce/rss.xml"),
]
MAX_ITEMS = 150
SUMMARY_LEN = 220
UA = "Mozilla/5.0 (compatible; HaberBot/1.0)"

def local(tag):
    return tag.rsplit("}", 1)[-1]

def clean(text):
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()

def parse_date(s):
    if not s:
        return None
    s = s.strip()
    try:
        d = parsedate_to_datetime(s)
    except Exception:
        try:
            d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)

def find_image(el):
    for child in el.iter():
        t = local(child.tag)
        if t in ("content", "thumbnail", "enclosure"):
            url = child.get("url")
            typ = child.get("type", "")
            if url and (t != "enclosure" or typ.startswith("image")):
                return url
    m = re.search(r'<img[^>]+src=["\']([^"\']+)', ET.tostring(el, encoding="unicode"))
    return html.unescape(m.group(1)) if m else None

def parse_feed(xml_bytes, source, category):
    root = ET.fromstring(xml_bytes)
    out = []
    for el in root.iter():
        if local(el.tag) not in ("item", "entry"):
            continue
        f = {}
        for c in el:
            f.setdefault(local(c.tag), c)
        title = clean(f["title"].text) if "title" in f else ""
        link = ""
        if "link" in f:
            link = (f["link"].get("href") or f["link"].text or "").strip()
        summ = ""
        for k in ("description", "summary", "encoded", "content"):
            if k in f and f[k].text:
                summ = clean(f[k].text)
                break
        date = None
        for k in ("pubDate", "published", "updated", "date"):
            if k in f:
                date = parse_date(f[k].text)
                if date:
                    break
        if not title or not link.startswith(("http://", "https://")):
            continue
        if len(summ) > SUMMARY_LEN:
            summ = summ[:SUMMARY_LEN].rsplit(" ", 1)[0] + "…"
        if summ.lower().startswith(title.lower()[:40]):
            summ = ""
        out.append({
            "title": title, "link": link, "summary": summ,
            "source": source, "category": category,
            "image": find_image(el),
            "published": (date or datetime.now(timezone.utc)).isoformat(),
        })
    return out

def main():
    items = []
    for source, category, url in FEEDS:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=20) as r:
                got = parse_feed(r.read(), source, category)
            print(f"OK   {source}/{category}: {len(got)} haber")
            items += got
        except Exception as e:
            print(f"HATA {source}/{category}: {e}", file=sys.stderr)

    seen, unique = set(), []
    for it in sorted(items, key=lambda x: x["published"], reverse=True):
        key = re.sub(r"\W+", "", it["title"].lower())
        if it["link"] in seen or key in seen:
            continue
        seen.add(it["link"]); seen.add(key)
        unique.append(it)

    if not unique:
        print("Hiç haber alınamadı, news.json değiştirilmedi.", file=sys.stderr)
        sys.exit(1)

    data = {"updated": datetime.now(timezone.utc).isoformat(), "items": unique[:MAX_ITEMS]}
    with open("news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"news.json yazıldı: {len(data['items'])} haber")

if __name__ == "__main__":
    main()
