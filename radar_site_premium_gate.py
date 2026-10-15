#!/usr/bin/env python3
"""Permanent quality gate for the restaurantradar.app marketing site.

Purpose: the 2026-10-12 "site looks substandard" class had measured causes
(zero product imagery, no og:image/twitter card, dead mobile nav, orphan grids,
claims the APP did not back: it advertised a map it did not have). This gate is
the class-level mechanism: it fails on ANY recurrence of those defect classes,
in the repo (source of truth) and optionally against the live site.

Usage:
    python radar_site_premium_gate.py           # repo checks only
    python radar_site_premium_gate.py --live    # repo + live-site checks

Exit 0 = all checks pass. Exit 1 = at least one FAIL (printed with detail).
Deterministic, stdlib + PIL only, no network unless --live.
"""
import json
import os
import re
import struct
import subprocess
import sys
import urllib.request

REPO = r"D:\Hermes_Core\Workspace\restaurant_radar"
LIVE = "https://restaurantradar.app"
PAGES = ["index.html", "pricing.html", "city-license.html", "privacy.html"]
RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok)))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return f.read()


def png_size(path):
    with open(path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return w, h


def main():
    live = "--live" in sys.argv
    html = {p: read(p) for p in PAGES}
    joined = "".join(html.values())
    css = read("assets/site.css")

    # ---- G1 link hygiene -------------------------------------------------
    dead = [m for h in html.values() for m in re.findall(r'href="(#|)"', h)]
    check("G1 no empty/dead hrefs", not dead, str(dead[:4]))
    # rotation-safe, redefined 2026-10-15 (audit CRITICAL-2): pages now carry STATIC hrefs so a
    # no-JS visitor and every crawler still gets a money link (measured: 0 of 5 buy CTAs had an href;
    # hrefs were injected only by fetch('assets/app_url.json')). A hardcoded host is therefore allowed
    # but must never DRIFT - radar_site_republish.py rewrites host strings on every tunnel rotation, so
    # the gate compares pages against the loader's own contract file instead of banning hosts outright.
    try:
        app_host = json.loads(read("assets/app_url.json"))["url"].rstrip("/")
    except Exception:
        app_host = ""
    drifted = sorted({m for h in html.values() for m in re.findall(r"https://[a-z0-9-]+\.trycloudflare\.com", h)
                      if app_host and not app_host.startswith(m)})
    check("G1 every hardcoded host matches assets/app_url.json (no stale tunnel link)",
          bool(app_host) and not drifted, str(drifted or f"app_url={app_host or 'UNREADABLE'}"))
    nohref = [f"{p}:{m[:60]}" for p, h in html.items()
              for m in re.findall(r"<a\s[^>]*data-app-url[^>]*>", h) if "href=" not in m]
    check("G1 every data-app-url CTA carries a static href (no-JS + crawler money link)",
          not nohref, str(nohref[:4]))
    # local links resolve
    known = set(PAGES) | {"sitemap.xml", "robots.txt", "manifest.json", "sw.js"}
    bad = []
    for p, h in html.items():
        for l in re.findall(r'href="([^"]+)"', h):
            if l.startswith(("https://", "http://", "mailto:", "tel:", "#")):
                continue
            if l.startswith(("assets/", "/assets/")):
                f = l.lstrip("/").split("?")[0]
                if not os.path.exists(os.path.join(REPO, f)):
                    bad.append(l)
                continue
            base = l.split("?")[0].lstrip("/")
            if base and base not in known:
                bad.append(l)
    check("G1b local hrefs resolve on disk", not bad, str(sorted(set(bad))[:5]))

    # ---- G2 money path: only sellable tiers -----------------------------
    au = json.loads(read("assets/app_url.json"))
    check("G2 app_url has url + both checkout keys",
          all(k in au for k in ("url", "checkout_founding", "checkout_city")), str(list(au)))
    check("G2b checkout targets are the two sellable tiers",
          au.get("checkout_founding", "").endswith("/api/checkout/founding_professional")
          and au.get("checkout_city", "").endswith("/api/checkout/city_license"))
    for tier in ("/api/checkout/professional", "/api/checkout/premier"):
        check(f"G2c forbidden tier absent: {tier}", tier not in joined and tier not in json.dumps(au))

    # ---- G3 structure ----------------------------------------------------
    tb = {}
    for p, h in html.items():
        for t in ("div", "a", "section", "header", "footer", "main", "ul", "li", "span", "h1", "h2", "h3", "nav", "button"):
            o = len(re.findall(rf"<{t}[\s>]", h))
            c = h.count(f"</{t}>")
            if o != c:
                tb.setdefault(p, []).append(f"{t}:{o}/{c}")
    check("G3 balanced tags", not tb, str(tb)[:200])
    check("G3b lang attr every page", all('lang="en"' in h for h in html.values()))
    check("G3c skip link every page", all("skip-link" in h for h in html.values()))

    # ---- G4 no forms / secrets ------------------------------------------
    check("G4 no <form", not any("<form" in h.lower() for h in html.values()))
    check("G4b no secret shapes", not re.search(r"(sk_live|pk_live|whsec_|sk-or-|Bearer\s+[A-Za-z0-9])", joined))

    # ---- G5 sitemap / robots / manifest ---------------------------------
    sm = read("sitemap.xml")
    check("G5 sitemap covers all 4 pages",
          all(f"restaurantradar.app/{p}" in sm for p in PAGES[1:]) and "restaurantradar.app/" in sm)
    check("G5b robots points at sitemap", "sitemap.xml" in read("robots.txt").lower())
    mj = json.loads(read("manifest.json"))
    check("G5c manifest valid + radar name", "radar" in mj.get("name", "").lower())

    # ---- G6 JS parses ----------------------------------------------------
    node = r"""node --check"""
    for js_rel in ("sw.js",):
        full = os.path.join(REPO, js_rel)
        # node on this host mangles MSYS paths -> use native path via cmd
        r = subprocess.run(f'node --check "{full}"', capture_output=True, text=True, timeout=30, shell=True)
        check(f"G6 {js_rel} parses (node --check)", r.returncode == 0, (r.stderr or "")[:120])
    # inline page JS: extract <script>...</script> bodies to temp + node check
    for p, h in html.items():
        blocks = re.findall(r"<script>(.*?)</script>", h, re.S)
        tmp = os.path.join(REPO, "_gate_pagejs.js")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write("\n;\n".join(blocks))
        r = subprocess.run(f'node --check "{tmp}"', capture_output=True, text=True, timeout=30, shell=True)
        os.remove(tmp)
        check(f"G6b {p} inline JS parses", r.returncode == 0, (r.stderr or "")[:120])

    # ---- G7 honesty of numbers ------------------------------------------
    check("G7 venue count cited (932)", "932" in html["index.html"])
    check("G7b false 247/94% claims absent", "247" not in joined and "94%" not in joined)
    check("G7c review stat is the true count (3), not the test-inflated 4",
          ">3<" in html["index.html"].replace(" ", "") and "reviews from early users" in html["index.html"]
          and not re.search(r">4<\s*<span class=\"stat-label\">reviews", html["index.html"]))
    hype = [w for w in ("revolutionary", "game-changing", "best-in-class", "world-class", "unparalleled")
            if w in joined.lower()]
    check("G7d no hype words", not hype, str(hype))

    # ---- G8 social/SEO block on every page ------------------------------
    for p, h in html.items():
        have = all(t in h for t in (
            'property="og:image"', 'property="og:title"', 'property="og:description"',
            'property="og:url"', 'name="twitter:card" content="summary_large_image"',
            'name="twitter:image"', 'name="theme-color"', 'rel="canonical"'))
        check(f"G8 {p} full og/twitter/canonical block", have)

    # ---- G9 mobile nav reachable ----------------------------------------
    for p, h in html.items():
        ok = ('class="hamburger"' in h and 'id="hamburger"' in h
              and 'aria-controls="siteNav"' in h and 'id="siteNav"' in h)
        check(f"G9 {p} hamburger + controllable nav", ok)
    check("G9b css hamburger >=44px and shown <=1023px",
          re.search(r"\.hamburger\s*\{[^}]*display:\s*none", css, re.S) is not None
          and "width: 44px; height: 44px" in css and "@media (max-width: 1023px)" in css
          and re.search(r"\.hamburger\s*\{[^}]*display:\s*none", css, re.S) is not None)

    # ---- G10 fail-safe reveal (no content hidden without JS) -------------
    check("G10 reveal gated under html.js (not bare opacity:0)",
          "html.js .reveal" in css and not re.search(r"(?<!html\.js )\.reveal\s*\{[^}]*opacity:\s*0", css))
    check("G10b prefers-reduced-motion honored", "prefers-reduced-motion" in css)
    check("G10c html.js class set by inline JS on every page",
          all("classList.add('js')" in h for h in html.values()))

    # ---- G11 real product imagery ---------------------------------------
    idx = html["index.html"]
    img_tag = re.search(r"<img[^>]*product-map\.png[^>]*>", idx)
    check("G11 hero has real product screenshot with alt",
          img_tag is not None and 'alt="' in img_tag.group(0) and len(re.search(r'alt="([^"]*)"', img_tag.group(0)).group(1)) > 20)
    og_path = os.path.join(REPO, "assets", "img", "og-image.png")
    og_ok = os.path.exists(og_path) and png_size(og_path) == (1200, 630) and os.path.getsize(og_path) < 800_000
    check("G11b og-image.png exists 1200x630 <800KB", og_ok,
          str(png_size(og_path)) if os.path.exists(og_path) else "missing")
    pm_path = os.path.join(REPO, "assets", "img", "product-map.png")
    check("G11c product-map.png exists", os.path.exists(pm_path))

    # ---- G12 app loader present -----------------------------------------
    for p, h in html.items():
        check(f"G12 {p} async app_url loader", "data-app-url" in h and "app_url.json" in h)
    check("G12b no unbacked star ratings on index",
          not re.search(r"⭐\s*\d|★\s*\d\.\d", html["index.html"]) or "early users" in idx)

    # ---- G13 tap targets in CSS -----------------------------------------
    check("G13 buttons >=48px", "min-height: 48px" in css)
    check("G13b no bare auto-fit orphan grids", "repeat(auto-fit" not in css)

    # ---- G14 --live checks ----------------------------------------------
    if live:
        for path in ["/"] + ["/" + p for p in PAGES[1:]]:
            try:
                req = urllib.request.Request(LIVE + path, headers={"User-Agent": "radar-gate"})
                body = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
                ok = ('property="og:image"' in body and 'name="twitter:card"' in body
                      and 'class="hamburger"' in body)
                check(f"G14 live {path} og+twitter+hamburger", ok)
            except Exception as e:
                check(f"G14 live {path} reachable", False, str(e)[:80])
        try:
            req = urllib.request.Request(LIVE + "/assets/img/og-image.png", headers={"User-Agent": "radar-gate"})
            resp = urllib.request.urlopen(req, timeout=25)
            check("G14b live og-image serves", resp.status == 200 and len(resp.read()) > 100_000)
        except Exception as e:
            check("G14b live og-image serves", False, str(e)[:80])

    passed = sum(1 for _, ok in RESULTS if ok)
    print(f"\nSUMMARY: {passed}/{len(RESULTS)} checks pass")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())