#!/usr/bin/env python3
"""Regenera cronologia.html.

Fuente de datos principal: cronologia.jsonl (una línea JSON por evento).
La función migrate_md() convierte cronologia.md → cronologia.jsonl (uso único).

Uso:
  python gen_html.py              # lee JSONL → regenera HTML
  python gen_html.py --migrate    # convierte MD → JSONL, luego regenera HTML
"""

import re, json, sys
from pathlib import Path

BASE  = Path(__file__).parent
MD    = BASE / "cronologia.md"
JSONL = BASE / "cronologia.jsonl"
HTML  = BASE / "cronologia.html"

# ── Escape para JS ────────────────────────────────────────────────────────────

def esc(s):
    return str(s).replace('\\','\\\\').replace("'","\\'").replace('\n',' ')

# ── Leer / escribir JSONL ─────────────────────────────────────────────────────

def load_jsonl(path):
    eventos = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                eventos.append(json.loads(line))
    return eventos

def dump_jsonl(path, eventos):
    with open(path, 'w', encoding='utf-8') as f:
        for ev in eventos:
            f.write(json.dumps(ev, ensure_ascii=False) + '\n')

# ── Migración MD → JSONL (uso único) ─────────────────────────────────────────

def _parse_date(raw):
    raw = raw.strip()
    meses = ['','enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']
    m = re.match(r'\[(\d{4})-(\d{2})-(\d{2})\]', raw)
    if m:
        y, mo, d = m.groups()
        return f"{int(d)} {meses[int(mo)]} {y}", int(y)
    m = re.match(r'\[(\d{4})-(\d{2})\]', raw)
    if m:
        y, mo = m.groups()
        return f"{meses[int(mo)]} {y}", int(y)
    m = re.match(r'\[(\d{4})\]', raw)
    if m:
        return m.group(1), int(m.group(1))
    return raw, 2023

def _clave_imagen(ev):
    """Clave estable para reconocer un evento entre migraciones.

    Usa la URL de la primera fuente: sobrevive a correcciones de titulo o de
    fecha, que son las ediciones habituales en el Markdown.
    """
    fuentes = ev.get('fuentes') or []
    if fuentes and fuentes[0].get('url'):
        return fuentes[0]['url']
    return f"{ev.get('fecha','')}|{ev.get('titulo','')}"


def migrate_md(md_path, jsonl_path):
    # Las imagenes viven solo en el JSONL (las pone fetch_imagenes.py), asi que
    # hay que rescatarlas antes de reconstruirlo desde el Markdown.
    imgs = {}
    if jsonl_path.exists():
        for ev in load_jsonl(jsonl_path):
            if ev.get('imagen'):
                imgs[_clave_imagen(ev)] = (ev['imagen'],
                                           ev.get('imagen_medio', ''),
                                           ev.get('imagen_generica', False))

    text = md_path.read_text(encoding='utf-8')
    blocks = re.split(r'\n(?=### \[)', text)
    eventos = []
    for block in blocks:
        if not block.startswith('### ['):
            continue
        lines = block.split('\n')
        header = lines[0]
        m = re.match(r'### (\[[\d\-]+\])\s*(.*)', header)
        if not m:
            continue
        fecha_label, anio = _parse_date(m.group(1))
        titulo = m.group(2).strip()

        desc = intervinientes = categorias = aristas = ''
        fuentes_raw = []
        in_fuentes = False

        for line in lines[1:]:
            ls = line.strip()
            if ls.startswith('**Descripción:**'):
                desc = ls[len('**Descripción:**'):].strip(); in_fuentes = False
            elif ls.startswith('**Intervinientes:**'):
                intervinientes = ls[len('**Intervinientes:**'):].strip(); in_fuentes = False
            elif ls.startswith('**Categorías:**'):
                categorias = ls[len('**Categorías:**'):].strip(); in_fuentes = False
            elif ls.startswith('**Aristas:**'):
                aristas = ls[len('**Aristas:**'):].strip(); in_fuentes = False
            elif ls.startswith('**Fuentes:**'):
                in_fuentes = True
            elif in_fuentes and ls.startswith('- ['):
                fuentes_raw.append(ls)

        fuentes = []
        for f in fuentes_raw:
            fm = re.match(r'- \[([^\]]+)\]\(([^)]+)\)\s*(?:—\s*(.*))?', f)
            if fm:
                fuentes.append({'titulo': fm.group(1),
                                'url':    fm.group(2),
                                'medio':  (fm.group(3) or '').strip()})

        ev = {
            'fecha':        fecha_label,
            'anio':         anio,
            'titulo':       titulo,
            'desc':         desc,
            'intervinientes': [x.strip() for x in intervinientes.split(',') if x.strip()],
            'categorias':   [x.strip() for x in re.split(r'[,|]', categorias) if x.strip()],
            'aristas':      [x.strip() for x in re.split(r'[,|]', aristas)   if x.strip()],
            'fuentes':      fuentes,
        }
        prev = imgs.get(_clave_imagen(ev))
        if prev:
            ev['imagen'], medio, generica = prev
            if medio:
                ev['imagen_medio'] = medio
            if generica:
                ev['imagen_generica'] = True
        eventos.append(ev)

    dump_jsonl(jsonl_path, eventos)
    conservadas = sum(1 for e in eventos if e.get('imagen'))
    print(f"Migracion completa: {len(eventos)} eventos -> {jsonl_path.name} "
          f"({conservadas} con imagen)")
    return eventos

# ── Serializar a JS ───────────────────────────────────────────────────────────

def ev_to_js(ev):
    ints  = ', '.join(f"'{esc(i)}'" for i in ev['intervinientes'])
    cats  = ', '.join(f"'{esc(c)}'" for c in ev['categorias'])
    aris  = ', '.join(f"'{esc(a)}'" for a in ev['aristas'])
    fuents = ''
    for f in ev['fuentes']:
        fuents += f"      {{ titulo: '{esc(f['titulo'])}', medio: '{esc(f['medio'])}', url: '{esc(f['url'])}' }},\n"
    img = ''
    if ev.get('imagen'):
        img = (f"    imagen: '{esc(ev['imagen'])}', "
               f"imagenMedio: '{esc(ev.get('imagen_medio',''))}',\n")
        if ev.get('imagen_generica'):
            img += "    imagenGenerica: true,\n"
    return (
        f"  {{\n"
        f"    fecha: '{esc(ev['fecha'])}', anio: {ev['anio']},\n"
        f"    titulo: '{esc(ev['titulo'])}',\n"
        f"{img}"
        f"    desc: '{esc(ev['desc'])}',\n"
        f"    intervinientes: [{ints}],\n"
        f"    categorias: [{cats}],\n"
        f"    aristas: [{aris}],\n"
        f"    fuentes: [\n{fuents}"
        f"    ]\n"
        f"  }}"
    )

# ── Reconstruir HTML ──────────────────────────────────────────────────────────

def rebuild(html_path, eventos):
    lines = html_path.read_text(encoding='utf-8').splitlines(keepends=True)
    start = next(i for i, l in enumerate(lines) if l.strip().startswith('const EVENTOS = ['))
    end   = next(i for i in range(start, len(lines)) if lines[i].strip() == '];')
    new_array  = 'const EVENTOS = [\n'
    new_array += ',\n'.join(ev_to_js(ev) for ev in eventos)
    new_array += '\n];\n'
    return ''.join(lines[:start] + [new_array] + lines[end+1:])

# ── Main ──────────────────────────────────────────────────────────────────────

if '--migrate' in sys.argv:
    eventos = migrate_md(MD, JSONL)
else:
    eventos = load_jsonl(JSONL)

print(f"Eventos: {len(eventos)}")
html = rebuild(HTML, eventos)
HTML.write_text(html, encoding='utf-8')
print(f"HTML regenerado: {HTML.name}")
print(f"Fuentes: {sum(len(e['fuentes']) for e in eventos)}")
