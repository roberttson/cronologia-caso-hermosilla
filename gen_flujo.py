#!/usr/bin/env python3
"""Genera flujo.html: diagrama de flujo incremental del Caso Hermosilla.

Pensado para exponer en vivo. Cada arista es un carril horizontal; el tiempo
corre hacia la derecha. Al avanzar paso a paso van apareciendo los hechos, se
abren las aristas y se dibujan los cruces entre ellas.

Un cruce puede ser de dos tipos:
  - explicito: el hecho pertenece a dos o mas aristas a la vez.
  - por interviniente: comparte una persona con un hecho anterior de otra
    arista. Se ponderan por rareza, porque que aparezca Hermosilla no explica
    nada (esta en casi todos) y que aparezca Migueles si.

Uso:
  python gen_flujo.py
"""

import json
from collections import Counter
from pathlib import Path

BASE  = Path(__file__).parent
JSONL = BASE / "cronologia.jsonl"
OUT   = BASE / "flujo.html"

ARISTAS = {
    'audio-sii':            {'label': 'Audio / SII',         'color': '#E63946'},
    'factop':               {'label': 'Factop',              'color': '#F77F00'},
    'parque-capital':       {'label': 'Parque Capital',      'color': '#FCBF49'},
    'poder-judicial':       {'label': 'Poder Judicial',      'color': '#4A90E2'},
    'pdi':                  {'label': 'PDI',                 'color': '#9B59B6'},
    'politico-diplomatico': {'label': 'Político-diplomático','color': '#2A9D8F'},
    'bielorrusa':           {'label': 'Muñeca Bielorrusa',   'color': '#D946EF'},
}
ORDEN = list(ARISTAS)

# Un interviniente que aparece en mas de esta fraccion de los hechos no explica
# ningun cruce: es parte del decorado del caso.
UMBRAL_UBICUO = 0.18

# Heuristica de "hito clave" para el modo resumen. Se busca solo en el TITULO
# (la descripcion menciona de pasada casi todos estos terminos y ensucia el
# filtro). Es editable a proposito: sube o baja segun cuanto quieras contar.
CLAVE_KW = (
    'formaliz', 'conden', 'prisión preventiva', 'destitu', 'detención',
    'acusación', 'expulsa', 'sentencia', 'remoción', 'juicio oral',
    'cierra investigación', 'renuncia', 'allana',
)


def norm(nombre):
    """Reduce 'Ángela Vivanco (exministra)' a 'ángela vivanco'."""
    n = nombre.split('(')[0].strip().lower()
    return ' '.join(n.split())


def cargar():
    return [json.loads(l) for l in
            JSONL.read_text(encoding='utf-8').splitlines() if l.strip()]


def preparar(eventos):
    total = len(eventos)
    freq = Counter()
    for ev in eventos:
        for i in set(norm(x) for x in ev.get('intervinientes', [])):
            freq[i] += 1

    ubicuos = {n for n, c in freq.items() if c > total * UMBRAL_UBICUO}

    # Primer indice en que aparece cada arista: marca su apertura.
    apertura = {}
    for i, ev in enumerate(eventos):
        for a in ev.get('aristas', []):
            if a in ARISTAS and a not in apertura:
                apertura[a] = i

    nodos = []
    for i, ev in enumerate(eventos):
        aristas = [a for a in ev.get('aristas', []) if a in ARISTAS]
        if not aristas:
            aristas = ['audio-sii']
        principal = min(aristas, key=lambda a: ORDEN.index(a))

        propios = {norm(x): x for x in ev.get('intervinientes', [])}
        utiles  = {k: v for k, v in propios.items() if k not in ubicuos}

        # Cruce por interviniente: hecho anterior mas reciente, de otra arista,
        # que comparta a alguien no ubicuo.
        enlaces = []
        for j in range(i - 1, -1, -1):
            if len(enlaces) >= 2:
                break
            prev = nodos[j]
            if prev['principal'] == principal:
                continue
            comunes = set(utiles) & set(prev['utiles'])
            if comunes:
                nombres = [utiles[c] for c in sorted(comunes)][:3]
                if any(e['idx'] == j for e in enlaces):
                    continue
                enlaces.append({
                    'idx': j,
                    'via': nombres,
                    'de': prev['principal'],
                })

        titulo_l = ev.get('titulo', '').lower()
        abre_arista = any(apertura.get(a) == i for a in aristas)
        clave = (len(aristas) > 1 or abre_arista
                 or any(k in titulo_l for k in CLAVE_KW))

        nodos.append({
            'idx': i,
            'fecha': ev.get('fecha', ''),
            'anio': ev.get('anio'),
            'titulo': ev.get('titulo', ''),
            'desc': ev.get('desc', ''),
            'aristas': aristas,
            'principal': principal,
            'abre': [a for a in aristas if apertura.get(a) == i],
            'cruces': [a for a in aristas if a != principal],
            'enlaces': enlaces,
            'intervinientes': ev.get('intervinientes', []),
            'fuentes': ev.get('fuentes', []),
            'imagen': ev.get('imagen') if not ev.get('imagen_generica') else None,
            'imagenMedio': ev.get('imagen_medio', ''),
            'clave': clave,
            'utiles': utiles,   # se descarta antes de serializar
        })

    for n in nodos:
        n.pop('utiles', None)
    return nodos


PLANTILLA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Caso Hermosilla — Diagrama de flujo</title>
<style>
:root {
  --bg: #0E1116;
  --bg-card: #181D24;
  --bg-card-hover: #1F252E;
  --border: #2A313C;
  --text: #ECEFF4;
  --text-muted: #8A95A5;
  --accent: #F4A261;
  --lane-h: 62px;
  --step: 132px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
               "Helvetica Neue", sans-serif;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* ── Barra superior ─────────────────────────────────────────────── */
header {
  flex: none;
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 12px 22px;
  border-bottom: 1px solid var(--border);
  background: #11151B;
}

h1 {
  font-size: 0.98rem;
  font-weight: 800;
  letter-spacing: 0.02em;
  white-space: nowrap;
}
h1 span { color: var(--accent); }

.progreso {
  font-variant-numeric: tabular-nums;
  font-size: 0.82rem;
  color: var(--text-muted);
  white-space: nowrap;
}
.progreso b { color: var(--text); font-size: 1rem; }

.barra {
  flex: 1;
  height: 5px;
  background: #222933;
  border-radius: 3px;
  overflow: hidden;
  min-width: 60px;
}
.barra i {
  display: block;
  height: 100%;
  width: 0;
  background: var(--accent);
  transition: width 0.35s ease;
}

.controles { display: flex; gap: 8px; align-items: center; }

button {
  background: var(--bg-card);
  color: var(--text);
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 8px 14px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
  white-space: nowrap;
}
button:hover:not(:disabled) { background: var(--bg-card-hover); border-color: var(--accent); }
button:disabled { opacity: 0.35; cursor: default; }
button.primario { background: var(--accent); color: #14181E; border-color: var(--accent); }
button.primario:hover:not(:disabled) { filter: brightness(1.12); }
button.activo { border-color: var(--accent); color: var(--accent); }

/* ── Cuerpo ─────────────────────────────────────────────────────── */
.cuerpo { flex: 1; display: flex; min-height: 0; }

/* Carriles */
.lienzo {
  flex: 1;
  position: relative;
  overflow: hidden;
  min-width: 0;
}

.etiquetas {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 168px;
  background: linear-gradient(90deg, var(--bg) 78%, transparent);
  z-index: 5;
  pointer-events: none;
  padding-top: 34px;
}

.etiqueta {
  height: var(--lane-h);
  display: flex;
  align-items: center;
  padding-left: 16px;
  font-size: 0.74rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  opacity: 0.28;
  transition: opacity 0.4s ease;
}
.etiqueta.viva { opacity: 1; }
.etiqueta i {
  width: 9px; height: 9px;
  border-radius: 50%;
  margin-right: 9px;
  flex: none;
  background: currentColor;
}

.scroll {
  position: absolute;
  inset: 0;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
  scrollbar-color: #39414E var(--bg);
}
.scroll::-webkit-scrollbar { height: 9px; }
.scroll::-webkit-scrollbar-thumb { background: #39414E; border-radius: 5px; }

.pista { position: relative; height: 100%; padding-top: 34px; }

.carril {
  position: absolute;
  left: 0; right: 0;
  height: var(--lane-h);
  border-bottom: 1px dashed #1C222B;
}

svg.lineas { position: absolute; inset: 0; overflow: visible; pointer-events: none; }

.nodo {
  position: absolute;
  transform: translate(-50%, -50%);
  cursor: pointer;
  z-index: 3;
}

.punto {
  width: 17px; height: 17px;
  border-radius: 50%;
  border: 3px solid var(--bg);
  transition: all 0.3s cubic-bezier(.2,.9,.3,1.3);
}
.nodo.clave .punto { width: 23px; height: 23px; }
.nodo:hover .punto { transform: scale(1.35); }
.nodo.actual .punto {
  transform: scale(1.5);
  box-shadow: 0 0 0 5px rgba(244,162,97,0.22), 0 0 22px rgba(244,162,97,0.55);
}

.nodo .rotulo {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  top: 20px;
  font-size: 0.6rem;
  color: var(--text-muted);
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.nodo.actual .rotulo, .nodo:hover .rotulo { opacity: 1; color: var(--text); }

.cruce-punto {
  position: absolute;
  width: 10px; height: 10px;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: 2;
  opacity: 0.85;
}

.anio-marca {
  position: absolute;
  top: 6px;
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--text-muted);
  letter-spacing: 0.12em;
  transform: translateX(-50%);
  z-index: 4;
}
.anio-linea {
  position: absolute;
  top: 26px; bottom: 0;
  width: 1px;
  background: #1C222B;
  z-index: 1;
}

/* Animacion de aparicion */
.nodo, .cruce-punto { animation: surge 0.42s cubic-bezier(.2,.9,.3,1.3); }
@keyframes surge {
  from { opacity: 0; transform: translate(-50%,-50%) scale(0.3); }
  to   { opacity: 1; }
}

/* ── Panel lateral ──────────────────────────────────────────────── */
aside {
  flex: none;
  width: 380px;
  border-left: 1px solid var(--border);
  background: #11151B;
  overflow-y: auto;
  padding: 20px 22px 28px;
  scrollbar-width: thin;
}

.p-fecha {
  font-size: 0.7rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 700;
  margin-bottom: 7px;
}
.p-titulo { font-size: 1.06rem; font-weight: 800; line-height: 1.32; margin-bottom: 13px; }
.p-img {
  width: 100%; height: auto; max-height: 165px; object-fit: cover;
  border-radius: 9px; border: 1px solid var(--border); margin-bottom: 13px; display: block;
}
.p-desc { font-size: 0.86rem; line-height: 1.62; color: #C8D0DC; margin-bottom: 17px; }

.p-bloque { margin-bottom: 16px; }
.p-bloque h3 {
  font-size: 0.66rem; letter-spacing: 0.17em; text-transform: uppercase;
  color: var(--text-muted); margin-bottom: 8px; font-weight: 700;
}

.pill {
  display: inline-block;
  font-size: 0.66rem; font-weight: 700;
  padding: 4px 9px; border-radius: 20px;
  color: #14181E; margin: 0 4px 4px 0;
}
.tag {
  display: inline-block;
  font-size: 0.7rem;
  background: #1D232C; border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 3px 9px; border-radius: 5px; margin: 0 4px 4px 0;
}

.aviso {
  border-left: 3px solid var(--accent);
  background: rgba(244,162,97,0.07);
  padding: 11px 13px;
  border-radius: 0 7px 7px 0;
  font-size: 0.8rem;
  line-height: 1.55;
  margin-bottom: 14px;
}
.aviso.abre { border-left-color: #7CD992; background: rgba(124,217,146,0.08); }
.aviso b { color: var(--text); }

.p-fuente {
  display: block;
  font-size: 0.76rem;
  color: var(--text-muted);
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: 7px;
  padding: 8px 10px;
  margin-bottom: 6px;
  line-height: 1.4;
  transition: all 0.15s ease;
}
.p-fuente:hover { border-color: var(--accent); color: var(--text); }

.vacio { color: var(--text-muted); font-size: 0.87rem; line-height: 1.6; padding-top: 30px; }

/* Pantalla completa / presentacion */
body.presenta header { padding: 9px 18px; }
body.presenta { --lane-h: 68px; }

@media (max-width: 1100px) {
  aside { width: 320px; }
}
@media (max-width: 820px) {
  .cuerpo { flex-direction: column; }
  aside { width: auto; border-left: none; border-top: 1px solid var(--border); max-height: 42vh; }
  .etiquetas { width: 120px; }
}
</style>
</head>
<body>

<header>
  <h1>Caso Hermosilla · <span>flujo de los hechos</span></h1>
  <div class="progreso"><b id="n-actual">0</b> / __TOTAL__</div>
  <div class="barra"><i id="barra"></i></div>
  <div class="controles">
    <button id="btn-clave" title="Mostrar solo los hitos principales">Solo clave</button>
    <button id="btn-reinicio" title="Volver al inicio (Inicio)">⟲</button>
    <button id="btn-atras" title="Anterior (←)">‹ Atrás</button>
    <button id="btn-sig" class="primario" title="Siguiente (→ o Espacio)">Siguiente ›</button>
    <button id="btn-auto" title="Reproducir solo">▶ Auto</button>
    <button id="btn-full" title="Pantalla completa (F)">⛶</button>
  </div>
</header>

<div class="cuerpo">
  <div class="lienzo">
    <div class="scroll" id="scroll">
      <div class="pista" id="pista">
        <svg class="lineas" id="svg"></svg>
      </div>
    </div>
    <div class="etiquetas" id="etiquetas"></div>
  </div>
  <aside id="panel"></aside>
</div>

<script>
const ARISTAS = __ARISTAS__;
const ORDEN   = __ORDEN__;
const NODOS   = __NODOS__;

const LANE_H = 62, TOP = 34, STEP = 132, X0 = 210;

let paso = -1;          // ultimo indice revelado
let soloClave = false;
let auto = null;

const $ = id => document.getElementById(id);
const visibles = () => soloClave ? NODOS.filter(n => n.clave) : NODOS;

function laneY(arista) {
  return TOP + ORDEN.indexOf(arista) * LANE_H + LANE_H / 2;
}
function posX(pos) { return X0 + pos * STEP; }

/* ── Construccion inicial ───────────────────────────────────────── */
function pintarEtiquetas() {
  $('etiquetas').innerHTML = ORDEN.map(a =>
    `<div class="etiqueta" data-a="${a}" style="color:${ARISTAS[a].color}">
       <i></i>${ARISTAS[a].label}
     </div>`).join('');
}

function pintarCarriles() {
  const pista = $('pista');
  pista.querySelectorAll('.carril,.anio-marca,.anio-linea').forEach(e => e.remove());
  ORDEN.forEach((a, i) => {
    const d = document.createElement('div');
    d.className = 'carril';
    d.style.top = (TOP + i * LANE_H) + 'px';
    pista.appendChild(d);
  });

  const lista = visibles();
  pista.style.width = (posX(lista.length) + 260) + 'px';
  pista.style.minHeight = (TOP + ORDEN.length * LANE_H + 40) + 'px';

  let anioPrev = null;
  lista.forEach((n, pos) => {
    if (n.anio === anioPrev) return;
    anioPrev = n.anio;
    const x = posX(pos) - STEP / 2;
    const m = document.createElement('div');
    m.className = 'anio-marca';
    m.style.left = x + 'px';
    m.textContent = n.anio;
    pista.appendChild(m);
    const l = document.createElement('div');
    l.className = 'anio-linea';
    l.style.left = x + 'px';
    pista.appendChild(l);
  });
}

/* ── Dibujo incremental ─────────────────────────────────────────── */
function redibujar(scrollTo) {
  const pista = $('pista'), svg = $('svg');
  pista.querySelectorAll('.nodo,.cruce-punto').forEach(e => e.remove());
  svg.innerHTML = '';

  const lista = visibles();
  const hasta = Math.min(paso, lista.length - 1);
  const ultimoPorArista = {};
  const posDe = {};
  lista.forEach((n, i) => posDe[n.idx] = i);

  const ns = 'http://www.w3.org/2000/svg';
  const linea = (x1, y1, x2, y2, color, w, dash, op) => {
    const p = document.createElementNS(ns, 'path');
    const mx = (x1 + x2) / 2;
    p.setAttribute('d', y1 === y2
      ? `M${x1},${y1} L${x2},${y2}`
      : `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`);
    p.setAttribute('stroke', color);
    p.setAttribute('stroke-width', w);
    p.setAttribute('fill', 'none');
    p.setAttribute('opacity', op);
    if (dash) p.setAttribute('stroke-dasharray', dash);
    svg.appendChild(p);
  };

  for (let i = 0; i <= hasta; i++) {
    const n = lista[i];
    const x = posX(i), y = laneY(n.principal);
    const color = ARISTAS[n.principal].color;
    const esActual = i === hasta;

    // Hilo del propio carril
    const ant = ultimoPorArista[n.principal];
    if (ant !== undefined) {
      linea(posX(ant), y, x, y, color, 2.2, null, 0.5);
    }

    // Cruces explicitos: el hecho pertenece a otra arista tambien
    n.cruces.forEach(a => {
      const y2 = laneY(a);
      linea(x, y, x, y2, ARISTAS[a].color, 2, '4 3', 0.75);
      const c = document.createElement('div');
      c.className = 'cruce-punto';
      c.style.left = x + 'px';
      c.style.top = y2 + 'px';
      c.style.background = ARISTAS[a].color;
      pista.appendChild(c);
      if (ultimoPorArista[a] === undefined) ultimoPorArista[a] = i;
    });

    // Cruces por interviniente compartido
    n.enlaces.forEach(e => {
      const p = posDe[e.idx];
      if (p === undefined || p > hasta) return;
      linea(posX(p), laneY(e.de), x, y, '#6B7688', 1.3, '2 5', esActual ? 0.85 : 0.28);
    });

    const d = document.createElement('div');
    d.className = 'nodo' + (n.clave ? ' clave' : '') + (esActual ? ' actual' : '');
    d.style.left = x + 'px';
    d.style.top = y + 'px';
    d.innerHTML = `<div class="punto" style="background:${color}"></div>
                   <div class="rotulo">${n.fecha}</div>`;
    d.onclick = () => { paso = i; redibujar(true); };
    pista.appendChild(d);

    ultimoPorArista[n.principal] = i;
  }

  // Etiquetas de aristas ya abiertas
  const abiertas = new Set();
  for (let i = 0; i <= hasta; i++) lista[i].aristas.forEach(a => abiertas.add(a));
  document.querySelectorAll('.etiqueta').forEach(el =>
    el.classList.toggle('viva', abiertas.has(el.dataset.a)));

  $('n-actual').textContent = hasta + 1 < 0 ? 0 : hasta + 1;
  $('barra').style.width = lista.length ? ((hasta + 1) / lista.length * 100) + '%' : '0';
  $('btn-atras').disabled = hasta < 0;
  $('btn-sig').disabled = hasta >= lista.length - 1;

  panel(hasta >= 0 ? lista[hasta] : null, lista, posDe);

  if (scrollTo && hasta >= 0) {
    const s = $('scroll');
    s.scrollTo({ left: posX(hasta) - s.clientWidth * 0.62, behavior: 'smooth' });
  }
}

/* ── Panel de detalle ───────────────────────────────────────────── */
function panel(n, lista, posDe) {
  const el = $('panel');
  if (!n) {
    el.innerHTML = `<div class="vacio">
      Pulsa <b>Siguiente</b> (o la flecha →) para ir levantando el caso hecho por hecho.<br><br>
      Cada carril es una arista. Cuando un hecho pertenece a dos aristas, se dibuja
      la línea vertical que las cruza. Las líneas punteadas grises marcan hechos
      que comparten personas.
    </div>`;
    return;
  }

  const abre = n.abre.map(a =>
    `<div class="aviso abre">Se abre una arista nueva:
       <b style="color:${ARISTAS[a].color}">${ARISTAS[a].label}</b></div>`).join('');

  const cruces = n.cruces.length ? `<div class="aviso">
      Este hecho <b>cruza</b> ${ARISTAS[n.principal].label} con
      ${n.cruces.map(a => `<b style="color:${ARISTAS[a].color}">${ARISTAS[a].label}</b>`).join(' y ')}:
      pertenece a las dos a la vez.</div>` : '';

  const enlaces = n.enlaces.filter(e => posDe[e.idx] !== undefined).map(e => {
    const prev = NODOS[e.idx];
    return `<div class="aviso">Se conecta con
      <b>${prev.fecha}</b> (${ARISTAS[e.de].label}) a través de
      <b>${e.via.join(', ')}</b>.</div>`;
  }).join('');

  el.innerHTML = `
    <div class="p-fecha">${n.fecha}</div>
    <div class="p-titulo">${n.titulo}</div>
    ${n.imagen ? `<img class="p-img" src="${n.imagen}" alt="" loading="lazy"
        referrerpolicy="no-referrer" onerror="this.remove()">` : ''}
    ${abre}${cruces}${enlaces}
    <div class="p-desc">${n.desc}</div>
    <div class="p-bloque">
      <h3>Aristas</h3>
      ${n.aristas.map(a => `<span class="pill" style="background:${ARISTAS[a].color}">${ARISTAS[a].label}</span>`).join('')}
    </div>
    <div class="p-bloque">
      <h3>Intervinientes</h3>
      ${n.intervinientes.map(i => `<span class="tag">${i}</span>`).join('')}
    </div>
    <div class="p-bloque">
      <h3>Fuentes</h3>
      ${n.fuentes.map(f => `<a class="p-fuente" href="${f.url}" target="_blank" rel="noopener">
          ${f.titulo}<br><span style="opacity:.65">${f.medio}</span></a>`).join('')}
    </div>`;
}

/* ── Controles ──────────────────────────────────────────────────── */
function sig()   { const l = visibles(); if (paso < l.length - 1) { paso++; redibujar(true); } else pararAuto(); }
function atras() { if (paso >= 0) { paso--; redibujar(true); } }
function reinicio() { paso = -1; pararAuto(); redibujar(false); $('scroll').scrollTo({left:0, behavior:'smooth'}); }

function pararAuto() {
  if (auto) { clearInterval(auto); auto = null; $('btn-auto').textContent = '▶ Auto'; $('btn-auto').classList.remove('activo'); }
}
function alternarAuto() {
  if (auto) return pararAuto();
  auto = setInterval(sig, 2600);
  $('btn-auto').textContent = '⏸ Pausa';
  $('btn-auto').classList.add('activo');
  sig();
}

$('btn-sig').onclick = () => { pararAuto(); sig(); };
$('btn-atras').onclick = () => { pararAuto(); atras(); };
$('btn-reinicio').onclick = reinicio;
$('btn-auto').onclick = alternarAuto;
$('btn-full').onclick = () => {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen();
  else document.exitFullscreen();
};
$('btn-clave').onclick = () => {
  soloClave = !soloClave;
  $('btn-clave').classList.toggle('activo', soloClave);
  paso = -1;
  pintarCarriles();
  redibujar(false);
  $('scroll').scrollTo({ left: 0 });
};

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'A') return;
  if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'Enter') { e.preventDefault(); pararAuto(); sig(); }
  else if (e.key === 'ArrowLeft') { e.preventDefault(); pararAuto(); atras(); }
  else if (e.key === 'Home') { e.preventDefault(); reinicio(); }
  else if (e.key.toLowerCase() === 'f') $('btn-full').click();
  else if (e.key.toLowerCase() === 'p') alternarAuto();
});

document.addEventListener('fullscreenchange', () =>
  document.body.classList.toggle('presenta', !!document.fullscreenElement));

pintarEtiquetas();
pintarCarriles();
redibujar(false);
</script>
</body>
</html>
"""


def main():
    eventos = cargar()
    nodos = preparar(eventos)

    def j(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

    html = (PLANTILLA
            .replace('__ARISTAS__', j(ARISTAS))
            .replace('__ORDEN__',   j(ORDEN))
            .replace('__NODOS__',   j(nodos))
            .replace('__TOTAL__',   str(len(nodos))))

    OUT.write_text(html, encoding='utf-8')

    claves  = sum(1 for n in nodos if n['clave'])
    cruces  = sum(1 for n in nodos if n['cruces'])
    enlaces = sum(len(n['enlaces']) for n in nodos)
    print(f"flujo.html generado: {len(nodos)} hechos")
    print(f"  hitos clave (modo resumen): {claves}")
    print(f"  cruces explicitos (2+ aristas): {cruces}")
    print(f"  conexiones por interviniente: {enlaces}")
    print(f"  peso: {OUT.stat().st_size/1024:.0f} KB")


if __name__ == '__main__':
    main()
