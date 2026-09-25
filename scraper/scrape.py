#!/usr/bin/env python3
"""
MiniMakers Kit Shop — Supplier Scraper (Proof of Concept)
=========================================================
Scrapes products from Ugandan electronics suppliers, adds a markup,
and writes products.js for the shop page (shop.html).

Suppliers:
  - Neriko Electronics  (nerikoelectronics.com)   — robots, Arduino, Raspberry Pi
  - Bbiri Centre        (bbiri-centre.com)         — electronics components

Output: products.js  (variable SCRAPED_PRODUCTS)
Run:    python3 scraper/scrape.py   (from repo root, writes ./products.js)
"""

import json
import re
import time
import urllib.request
from html import unescape

MARKUP = 5000          # UGX added to every supplier price
ROUND_TO = 500         # round final price to nearest 500
MAX_PAGES_NERIKO = 8    # how many product pages to scrape per run
TIMEOUT = 25

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return r.read().decode("utf-8", errors="ignore")


def text_of(html):
    """Strip tags to plain text (no external deps needed)."""
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", "\n", html)
    txt = unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    return "\n".join(line.strip() for line in txt.splitlines() if line.strip())


def round_price(p):
    return int(round((p + MARKUP) / ROUND_TO) * ROUND_TO)


def parse_price(s):
    s = s.replace("UGX", "").replace(",", "").strip()
    m = re.match(r"([\d\.]+)", s)
    return int(float(m.group(1))) if m else None


# ---------------------------------------------------------------
# Neriko Electronics  —  /products?page=N
# Text layout:  [Out of stock]  <Product Name>  UGX<price>
# ---------------------------------------------------------------
def scrape_neriko():
    items = []
    for page in range(1, MAX_PAGES_NERIKO + 1):
        url = f"https://nerikoelectronics.com/products?page={page}"
        try:
            txt = text_of(fetch(url))
        except Exception as e:
            print(f"  neriko page {page}: fetch failed ({e}) — stopping")
            break
        lines = [l for l in txt.splitlines() if l.strip()]
        found = 0
        i = 0
        while i < len(lines) - 1:
            line = lines[i]
            nxt = lines[i + 1]
            price = None
            name = None
            out_of_stock = "out of stock" in line.lower()
            candidate = line if not out_of_stock else (lines[i - 1] if i > 0 else "")
            # pattern A: name line then UGX price line
            if nxt.upper().startswith("UGX") and not line.upper().startswith("UGX"):
                price = parse_price(nxt)
                name = candidate
            # pattern B: price on same line "Name UGX 55,000"
            m = re.match(r"^(.+?)\s+UGX\s?([\d,\.]+)\s*$", line)
            if price is None and m:
                name, price_s = m.group(1), "UGX" + m.group(2)
                price = parse_price(price_s)
            if price and name and 500 <= price <= 5_000_000 and len(name) > 3 \
               and "sort by" not in name.lower() and "items found" not in name.lower():
                items.append({
                    "name": name.strip(),
                    "price": round_price(price),
                    "stock": not out_of_stock,
                    "source": "Neriko Electronics",
                    "link": url,
                })
                found += 1
                i += 2
                continue
            i += 1
        print(f"  neriko page {page}: {found} items")
        if found == 0:
            break
        time.sleep(1)  # be polite
    seen, deduped = set(), []
    for it in items:
        key = it["name"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(it)
    return deduped


# ---------------------------------------------------------------
# Bbiri Centre  —  /shop/ pages
# Text layout:  <Product Name>  PriceUGX 30,000
# ---------------------------------------------------------------
def scrape_bbiri():
    items = []
    urls = ["https://www.bbiri-centre.com/shop/"]
    for page in range(2, 7):
        urls.append(f"https://www.bbiri-centre.com/shop/page/{page}/")
    for url in urls:
        try:
            txt = text_of(fetch(url))
        except Exception as e:
            print(f"  bbiri {url}: fetch failed ({e}) — skipping")
            continue
        pat = re.compile(r"([A-Z0-9][^\n]{4,80}?)\s*\n(?:Price)?UGX\s?([\d,\.]+)", re.I)
        found = 0
        for m in pat.finditer(txt):
            name = m.group(1).strip()
            price = parse_price("UGX" + m.group(2))
            if not price or price < 500 or len(name) < 4:
                continue
            if re.match(r"^(home|shop now|price|read more|add to cart|sale|ugx)$", name, re.I):
                continue
            items.append({
                "name": name,
                "price": round_price(price),
                "stock": True,
                "source": "Bbiri Centre",
                "link": "https://www.bbiri-centre.com/shop/",
            })
            found += 1
        print(f"  bbiri {url}: {found} items")
        time.sleep(1)
    seen, deduped = set(), []
    for it in items:
        key = it["name"].lower()
        if key not in seen:
            seen.add(key)
            deduped.append(it)
    return deduped


def categorize(name):
    n = name.lower()
    if any(k in n for k in ["kit", "bundle", "arduino", "raspberry", "pi ", "robot", "starter"]):
        return "starter"
    if any(k in n for k in ["motor", "sensor", "led", "battery", "batteries", "breadboard",
                            "resistor", "jumper", "cable", "wire", "servo", "display", "relay"]):
        return "parts"
    return "tools"


def main():
    print("Scraping suppliers...")
    all_items = []
    try:
        all_items += scrape_neriko()
    except Exception as e:
        print("Neriko failed entirely:", e)
    try:
        all_items += scrape_bbiri()
    except Exception as e:
        print("Bbiri failed entirely:", e)

    for it in all_items:
        it["cat"] = categorize(it["name"])
        it["emoji"] = "🧩" if it["cat"] == "parts" else ("🤖" if it["cat"] == "starter" else "🔧")
        it["desc"] = f"Sourced from {it['source']}. Delivery arranged via MiniMakers."
        it["id"] = "sc-" + re.sub(r"[^a-z0-9]+", "-", it["name"].lower())[:40]

    in_stock = [it for it in all_items if it["stock"]]
    print(f"Total: {len(in_stock)} in-stock items (+{len(all_items)-len(in_stock)} out of stock skipped)")

    with open("products.js", "w", encoding="utf-8") as f:
        f.write("// AUTO-GENERATED by scraper — do not edit by hand\n")
        f.write(f"// Scraped {time.strftime('%Y-%m-%d %H:%M')} UTC · markup UGX {MARKUP}\n")
        f.write("var SCRAPED_PRODUCTS = " + json.dumps(in_stock, ensure_ascii=False, indent=1) + ";\n")
    print("Wrote products.js ✅")


if __name__ == "__main__":
    main()
