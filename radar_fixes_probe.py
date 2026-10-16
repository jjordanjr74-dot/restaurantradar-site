#!/usr/bin/env python3
r"""radar_fixes_probe.py — mechanical, live acceptance probe for the 2026-10-15 audit fixes.

Checks (exit 0 = all PASS, 1 = any FAIL):
  * local app  GET /health            -> 200 + {"status":"ok","service":"radar"}
  * local app  GET /api/radar         -> 200 + 60 targets
  * public tunnel (radar_public_url.txt) GET /api/radar -> 200 + 60 targets
  * live site  GET /does-not-exist-xyz -> 404 + the CUSTOM page (not GitHub's default) in the body
  * live site  GET /index.html + /pricing.html -> no unbacked "10 spots"/"first 10" scarcity text

No paid APIs. GET only (never HEAD: the app 405s HEAD).
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

LOCAL = "http://127.0.0.1:5596"
LIVE = "https://restaurantradar.app"
PUB_FILE = r"D:/Hermes_Core/Logs/radar_public_url.txt"
RADAR_Q = "/api/radar?lat=38.25&lon=-104.6"

failures: list[str] = []


def check(name: str, ok: bool, detail: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'}: {name} :: {detail}")
    if not ok:
        failures.append(name)


def get(url: str, timeout: int = 20) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "radar-fixes-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:  # 404/405 arrive here
        return e.code, e.read().decode("utf-8", "replace")


def targets(body: str) -> int:
    try:
        d = json.loads(body)
        res = d.get("results")
        return len(res) if isinstance(res, list) else -1
    except Exception:
        return -1


def main() -> int:
    # 1) local /health
    try:
        code, body = get(LOCAL + "/health")
        d = json.loads(body) if body.strip() else {}
        ok = code == 200 and d.get("status") == "ok" and d.get("service") == "radar"
        check("local GET /health -> 200 {\"status\":\"ok\",\"service\":\"radar\"}", ok, f"http {code} body={body.strip()[:80]}")
    except Exception as e:
        check("local GET /health", False, f"{type(e).__name__}: {e}")

    # 2) local /api/radar
    try:
        code, body = get(LOCAL + RADAR_Q)
        n = targets(body)
        check("local GET /api/radar -> 200, 60 targets", code == 200 and n == 60, f"http {code} targets={n}")
    except Exception as e:
        check("local GET /api/radar", False, f"{type(e).__name__}: {e}")

    # 3) public tunnel /api/radar
    try:
        pub = open(PUB_FILE, encoding="utf-8").read().strip().rstrip("/")
    except Exception as e:
        pub = ""
        check("read radar_public_url.txt", False, f"{type(e).__name__}: {e}")
    if pub:
        try:
            code, body = get(pub + RADAR_Q, timeout=25)
            n = targets(body)
            check(f"public {pub}/api/radar -> 200, 60 targets", code == 200 and n == 60, f"http {code} targets={n}")
        except Exception as e:
            check(f"public {pub}/api/radar", False, f"{type(e).__name__}: {e}")

    # 4) live custom 404
    try:
        code, body = get(LIVE + "/does-not-exist-xyz")
        custom = "Pueblo" in body and ("off the radar" in body.lower() or "isn't on the map" in body.lower())
        github_default = "github" in body.lower() and "Pueblo" not in body
        check("live /does-not-exist-xyz -> 404 + CUSTOM styled page", code == 404 and custom and not github_default,
              f"http {code} custom={custom} github_default={github_default} bytes={len(body)}")
    except Exception as e:
        check("live custom 404", False, f"{type(e).__name__}: {e}")

    # 5) no unbacked scarcity text live
    try:
        bad = []
        for path in ("/index.html", "/pricing.html"):
            _, body = get(LIVE + path)
            for needle in ("10 spots", "first 10", "first-come basis"):
                if needle in body:
                    bad.append(f"{path}:{needle}")
        check("live index+pricing contain no unbacked '10 spots'/'first 10' scarcity", not bad, str(bad))
    except Exception as e:
        check("live scarcity text", False, f"{type(e).__name__}: {e}")

    print(f"\nSUMMARY: {'ALL PASS' if not failures else str(len(failures)) + ' FAIL -> ' + ', '.join(failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
