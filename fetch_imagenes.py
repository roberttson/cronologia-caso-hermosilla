#!/usr/bin/env python3
"""Extrae la imagen de portada (og:image) de las fuentes de cada evento.

Recorre cronologia.jsonl y, por cada evento sin imagen, consulta sus fuentes en
orden hasta encontrar una con og:image utilizable. El resultado se guarda en el
propio JSONL (campos 'imagen' y 'imagen_medio') y se cachea en imagenes.json
para que las siguientes corridas no vuelvan a pedir lo mismo.

Las imagenes NO se descargan: se enlazan desde el servidor del medio. Eso evita
sumar peso al sitio y deja la imagen alojada en su origen.

Uso:
  python fetch_imagenes.py            # solo eventos sin imagen
  python fetch_imagenes.py --todos    # re-consulta todos (ignora cache)
  python fetch_imagenes.py --reporte  # no consulta nada, solo muestra cobertura
"""

import json, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BASE  = Path(__file__).parent
JSONL = BASE / "cronologia.jsonl"
CACHE = BASE / "imagenes.json"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")

TIMEOUT = 12

# Patrones de imagenes que no aportan nada (logos, placeholders, avatares).
DESCARTAR = re.compile(
    r"(logo|placeholder|default|avatar|sprite|icon|favicon|blank|"
    r"generic|share|opengraph-default|banner-|/ads?/)",
    re.I,
)

META_PATTERNS = [
    re.compile(r'<meta[^>]+property=["\']og:image(?::url)?["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image(?::url)?["\']', re.I),
    re.compile(r'<meta[^>]+name=["\']twitter:image(?::src)?["\'][^>]+content=["\']([^"\']+)', re.I),
    re.compile(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']twitter:image(?::src)?["\']', re.I),
]


def cargar_cache():
    if CACHE.exists():
        return json.loads(CACHE.read_text(encoding="utf-8"))
    return {}


def guardar_cache(cache):
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def extraer_og(url):
    """Devuelve la URL de la imagen de portada, o None."""
    req = Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "es-CL,es;q=0.9",
    })
    with urlopen(req, timeout=TIMEOUT) as r:
        # Con el <head> basta; evita descargar articulos completos.
        raw = r.read(200_000)
        final_url = r.geturl()

    html = raw.decode("utf-8", errors="ignore")

    for pat in META_PATTERNS:
        m = pat.search(html)
        if not m:
            continue
        img = m.group(1).strip().replace("&amp;", "&")
        if not img:
            continue
        img = urljoin(final_url, img)
        if not img.startswith("https://"):
            # Sin HTTPS el navegador la bloquea por contenido mixto.
            continue
        if DESCARTAR.search(img):
            continue
        return img
    return None


def main():
    todos   = "--todos" in sys.argv
    reporte = "--reporte" in sys.argv

    eventos = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
    cache   = {} if todos else cargar_cache()

    if reporte:
        con = sum(1 for e in eventos if e.get("imagen"))
        print(f"Cobertura: {con}/{len(eventos)} eventos con imagen "
              f"({con*100//max(len(eventos),1)}%)")
        faltan = [e for e in eventos if not e.get("imagen")]
        for e in faltan[:15]:
            print(f"  sin imagen: [{e['fecha']}] {e['titulo'][:60]}")
        if len(faltan) > 15:
            print(f"  ... y {len(faltan)-15} mas")
        return

    nuevos = fallidos = 0

    for ev in eventos:
        if ev.get("imagen") and not todos:
            continue

        encontrada = None
        for f in ev.get("fuentes", []):
            url = f.get("url", "")
            if not url:
                continue

            if url in cache:
                img = cache[url]
            else:
                try:
                    img = extraer_og(url)
                except Exception as exc:
                    img = None
                    print(f"    fallo {urlparse(url).netloc}: {type(exc).__name__}")
                cache[url] = img
                time.sleep(0.6)   # cortesia con los servidores

            if img:
                encontrada = (img, f.get("medio", "") or urlparse(url).netloc)
                break

        if encontrada:
            ev["imagen"], ev["imagen_medio"] = encontrada
            nuevos += 1
            print(f"  OK  [{ev['fecha']}] {ev['titulo'][:52]}")
        else:
            ev.pop("imagen", None)
            ev.pop("imagen_medio", None)
            fallidos += 1
            print(f"  --  [{ev['fecha']}] {ev['titulo'][:52]}")

        guardar_cache(cache)

    with open(JSONL, "w", encoding="utf-8") as f:
        for ev in eventos:
            f.write(json.dumps(ev, ensure_ascii=False) + "\n")

    con = sum(1 for e in eventos if e.get("imagen"))
    print(f"\nNuevas: {nuevos}  |  sin imagen: {fallidos}  |  "
          f"cobertura total: {con}/{len(eventos)}")


if __name__ == "__main__":
    main()
