"""Genera/compara snapshots de las respuestas GET de la API (caracterizacion).

Uso:
    python scripts/gen_snapshot.py baseline   # captura baseline (antes de migrar)
    python scripts/gen_snapshot.py check      # compara vivo vs baseline

Requiere el backend corriendo en http://127.0.0.1:8000 con los datos reales.
Normaliza fechas ISO a <DT> para evitar falsos positivos por timestamps now().
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

BASE = "http://127.0.0.1:8000"
SNAP = os.path.join(os.path.dirname(__file__), "..", "tests", "snapshots", "endpoints.json")
DT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?")

# rutas a excluir: volatiles / archivos / mutaciones
EXCLUDE_SUBSTR = ("/pdf", "/openapi", "/docs", "/redoc", "/health", "/stats", "/debug")


def normalize(obj):
    if isinstance(obj, str):
        return DT_RE.sub("<DT>", obj)
    if isinstance(obj, list):
        return [normalize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()}
    return obj


def get_urls():
    import main
    urls = []
    for r in main.app.routes:
        path = getattr(r, "path", "")
        methods = getattr(r, "methods", set()) or set()
        if "GET" not in methods:
            continue
        if not path.startswith("/api/v1"):
            continue
        if any(s in path for s in EXCLUDE_SUBSTR):
            continue
        # rellenar {param} -> 1
        url = re.sub(r"\{[^}]+\}", "1", path)
        urls.append(url)
    return sorted(set(urls))


def fetch(url):
    try:
        req = urllib.request.Request(BASE + url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", "replace")
            status = resp.status
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": None}
    except Exception as e:
        return {"status": "ERR", "body": str(e)}
    try:
        parsed = normalize(json.loads(body))
    except Exception:
        parsed = body[:200]
    return {"status": status, "body": parsed}


def main_run(mode):
    urls = get_urls()
    if mode == "baseline":
        snap = {u: fetch(u) for u in urls}
        os.makedirs(os.path.dirname(SNAP), exist_ok=True)
        with open(SNAP, "w", encoding="utf-8") as f:
            json.dump(snap, f, ensure_ascii=False, indent=1, sort_keys=True)
        oks = sum(1 for v in snap.values() if v["status"] == 200)
        print(f"baseline: {len(snap)} rutas GET, {oks} con 200")
    elif mode == "check":
        with open(SNAP, encoding="utf-8") as f:
            base = json.load(f)
        diffs = []
        for u, expected in base.items():
            live = fetch(u)
            if live != expected:
                diffs.append(u)
        if diffs:
            print(f"❌ {len(diffs)} rutas DIFIEREN del baseline:")
            for u in diffs:
                print("   ", u)
        else:
            print(f"✅ {len(base)} rutas IDENTICAS al baseline")
        return len(diffs)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    sys.exit(main_run(mode) or 0)
