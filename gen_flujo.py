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
CORR  = BASE / "flujo_correcciones.json"
OUT   = BASE / "flujo.html"
OUT_PIEL = BASE / "flujo_retro.html"   # variante estetica, ver PIEL

ARISTAS = {
    'audio-sii':            {'label': 'Caso Hermosilla',     'color': '#E63946'},
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

# Los vinculos por interviniente compartido detectan COINCIDENCIA, no causalidad:
# que dos hechos compartan a Chadwick no significa que uno salga del otro. Al
# revisarlos uno por uno casi todos resultaron falsos, asi que la heuristica
# queda apagada y solo se dibuja la punteada que se dicte a mano en
# flujo_correcciones.json. Poner en True para volver a la deteccion automatica.
ENLACES_AUTOMATICOS = False

# Un medio que publica dos reportajes no conecta los hechos que cuenta: solo los
# cuenta. CIPER era la primera causa de cruces de todo el diagrama (28 de 159) y
# ninguno significaba nada. El umbral de arriba no los pillaba porque mide
# frecuencia, y el problema no es que aparezcan mucho sino que no son parte del
# hecho.
MEDIOS = {
    'ciper chile', 'ciper', 'reportea', 'the clinic', 'el mostrador',
    'la tercera', 'ex-ante', 'ex ante', 'interferencia', 'el mercurio',
}

# Heuristica de "hito clave" para el modo resumen. Se busca solo en el TITULO
# (la descripcion menciona de pasada casi todos estos terminos y ensucia el
# filtro). Es editable a proposito: sube o baja segun cuanto quieras contar.
CLAVE_KW = (
    'formaliz', 'conden', 'prisión preventiva', 'destitu', 'detención',
    'acusación', 'expulsa', 'sentencia', 'remoción', 'juicio oral',
    'cierra investigación', 'renuncia', 'allana',
)


# Los titulos tienen mediana de 80 caracteres: no caben en una tarjeta. Muchos
# vienen como "gist: detalle", asi que la parte anterior a los dos puntos suele
# ser justo el resumen que sirve de rotulo.
LARGO_CORTO = 58


def acortar(titulo):
    t = titulo.strip()
    if len(t) <= LARGO_CORTO:
        return t
    cabeza = t.split(':')[0].strip()
    if 12 <= len(cabeza) <= LARGO_CORTO:
        return cabeza
    corte = t[:LARGO_CORTO].rsplit(' ', 1)[0].rstrip(' ,;:')
    return corte + '…'


def norm(nombre):
    """Reduce 'Ángela Vivanco (exministra)' a 'ángela vivanco'."""
    n = nombre.split('(')[0].strip().lower()
    return ' '.join(n.split())


def cargar():
    return [json.loads(l) for l in
            JSONL.read_text(encoding='utf-8').splitlines() if l.strip()]


def _url(ev):
    fuentes = ev.get('fuentes') or []
    if fuentes and fuentes[0].get('url'):
        return fuentes[0]['url']
    return '%s|%s' % (ev.get('fecha', ''), ev.get('titulo', ''))


def asignar_refs(eventos):
    """Deja en ev['_ref'] un identificador estable y unico de cada hecho.

    Base: la URL de la primera fuente, la misma clave que usa gen_html.py para
    no perder las imagenes al regenerar. Aguanta correcciones de titulo y de
    fecha; la posicion en la lista no, porque se corre entera al insertar.

    Pero la URL sola no basta: hay 3 reportajes que son primera fuente de dos
    hechos distintos (por ejemplo la reunion grabada y la llegada del audio a
    CIPER salen ambas del mismo articulo de Ex-Ante). Sin desempatar, dos hechos
    comparten clave y una correccion se aplica al que no era. Cuando hay choque
    se agrega el titulo.
    """
    veces = Counter(_url(ev) for ev in eventos)
    for ev in eventos:
        u = _url(ev)
        ev['_ref'] = u if veces[u] == 1 else '%s#%s' % (u, ev.get('titulo', ''))
    return eventos


def ref(ev):
    return ev.get('_ref') or _url(ev)


def aplicar_correcciones(eventos):
    """Superpone las correcciones propias del diagrama de flujo.

    La linea de tiempo es correcta y no se toca: cronologia.md sigue siendo la
    fuente. Aca solo vive la lectura que necesita el diagrama, que es otra cosa
    (que arista manda, que hito es cabecera de su trama). Se aplica al vuelo, no
    se copia el JSONL, para que un hito nuevo en la cronologia aparezca solo.

    Campos por entrada, todos opcionales:
      aristas   reemplaza la lista de aristas del hecho
      suma      agrega aristas sin quitar las que ya tiene
      quita     saca aristas
      principal fuerza el carril donde se dibuja
      clave     True/False para forzar si sale en el modo resumen
      omitir    True para que el hecho no aparezca en el diagrama
    """
    if not CORR.exists():
        return eventos, []

    datos = json.loads(CORR.read_text(encoding='utf-8'))
    reglas = {r['ref']: r for r in datos.get('hitos', []) if r.get('ref')}
    vistos, avisos = set(), []

    salida = []
    for ev in eventos:
        r = reglas.get(ref(ev))
        if not r:
            salida.append(ev)
            continue
        vistos.add(ref(ev))

        if r.get('omitir'):
            continue

        aristas = list(r['aristas']) if 'aristas' in r else list(ev.get('aristas', []))
        for a in r.get('suma', []):
            if a not in aristas:
                aristas.append(a)
        aristas = [a for a in aristas if a not in r.get('quita', [])]

        malas = [a for a in aristas if a not in ARISTAS]
        if malas:
            avisos.append('hito "%s": arista inexistente %s' % (r.get('titulo', ref(ev)), malas))
            aristas = [a for a in aristas if a in ARISTAS]
        if not aristas:
            avisos.append('hito "%s": la correccion lo deja sin aristas' % r.get('titulo', ref(ev)))
            aristas = list(ev.get('aristas', []))

        ev = dict(ev, aristas=aristas)
        if r.get('principal'):
            if r['principal'] not in aristas:
                avisos.append('hito "%s": principal "%s" no esta entre sus aristas'
                              % (r.get('titulo', ref(ev)), r['principal']))
            else:
                ev['_principal'] = r['principal']
        if 'clave' in r:
            ev['_clave'] = bool(r['clave'])
        if 'enlaces' in r:
            ev['_enlaces'] = r['enlaces']
        if r.get('sin_imagen'):
            ev['imagen'] = None
        salida.append(ev)

    # Una correccion que no calza con ningun hecho es un error silencioso: la
    # URL cambio o el hito se borro. Hay que verlo, no tragarselo.
    for k in reglas:
        if k not in vistos:
            avisos.append('correccion sin hito que le calce: %s'
                          % (reglas[k].get('titulo') or k))
    return salida, avisos


def preparar(eventos, numeros=None):
    total = len(eventos)
    freq = Counter()
    for ev in eventos:
        for i in set(norm(x) for x in ev.get('intervinientes', [])):
            freq[i] += 1

    ubicuos = {n for n, c in freq.items() if c > total * UMBRAL_UBICUO} | MEDIOS

    ref_idx = {ref(ev): i for i, ev in enumerate(eventos)}

    # Primer indice en que aparece cada arista: marca su apertura.
    apertura = {}
    for i, ev in enumerate(eventos):
        for a in ev.get('aristas', []):
            if a in ARISTAS and a not in apertura:
                apertura[a] = i

    nodos = []
    ultimo_uso = {}   # arista -> indice del ultimo hecho que la toco
    for i, ev in enumerate(eventos):
        aristas = [a for a in ev.get('aristas', []) if a in ARISTAS]
        if not aristas:
            aristas = ['audio-sii']

        # Antes el carril de un hecho multi-arista salia de min(ORDEN), o sea
        # del orden en que estan escritas las aristas en el diccionario, que no
        # significa nada: un hecho PDI + Poder Judicial caia siempre en Poder
        # Judicial y el hilo brincaba de carril sin motivo. Ahora cae en la
        # arista con actividad mas reciente, para que el hilo siga derecho.
        principal = ev.get('_principal') or max(
            aristas, key=lambda a: (ultimo_uso.get(a, -1), -ORDEN.index(a)))

        propios = {norm(x): x for x in ev.get('intervinientes', [])}
        utiles  = {k: v for k, v in propios.items() if k not in ubicuos}

        # Enlaces dictados a mano en flujo_correcciones.json: mandan sobre la
        # heuristica. Una lista vacia significa "este hecho no se vincula con
        # nada", que es distinto de no haberlo revisado todavia.
        enlaces = []
        if '_enlaces' in ev:
            # Enlaces dictados a mano: mandan sobre la heuristica. Una lista
            # vacia significa "este hecho no se vincula con nada", que es
            # distinto de no haberlo revisado todavia.
            for man in ev['_enlaces']:
                j = ref_idx.get(man['ref'])
                if j is None or j >= i:
                    continue
                enlaces.append({
                    'idx': j,
                    'via': [man['razon']] if man.get('razon') else ['vínculo directo'],
                    'de': nodos[j]['principal'],
                    'manual': True,
                })
        elif ENLACES_AUTOMATICOS:
            # Cruce por interviniente: hecho anterior mas reciente, de otra
            # arista, que comparta a alguien no ubicuo.
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
        clave = ev['_clave'] if '_clave' in ev else (
            len(aristas) > 1 or abre_arista
            or any(k in titulo_l for k in CLAVE_KW))

        nodos.append({
            'idx': i,
            # Numero del hito en la cronologia, que es como se lee y se dicta.
            # No coincide con la posicion en el diagrama cuando hay hitos
            # omitidos, y confundirlos hace que una correccion caiga en el
            # hecho equivocado.
            'n': numeros[ev['_ref']] if numeros else i + 1,
            'fecha': ev.get('fecha', ''),
            'anio': ev.get('anio'),
            'titulo': ev.get('titulo', ''),
            'corto': acortar(ev.get('titulo', '')),
            'desc': ev.get('desc', ''),
            'aristas': aristas,
            'principal': principal,
            'abre': [a for a in aristas if apertura.get(a) == i],
            'cruces': [a for a in aristas if a != principal],
            'enlaces': enlaces,
            'intervinientes': ev.get('intervinientes', []),
            # Nombres normalizados, para poder resaltar a una persona a traves
            # de hitos que la escriben distinto ('Chadwick (exministro)').
            'pers': sorted({norm(x) for x in ev.get('intervinientes', [])}),
            'fuentes': ev.get('fuentes', []),
            'imagen': ev.get('imagen'),
            'generica': bool(ev.get('imagen_generica')),
            'imagenMedio': ev.get('imagen_medio', ''),
            'clave': clave,
            'utiles': utiles,   # se descarta antes de serializar
        })

        # La linea vertical del cruce toca todas sus aristas, asi que todas
        # cuentan como "usadas" para el hecho siguiente.
        for a in aristas:
            ultimo_uso[a] = i

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
  --lane-h: 108px;
  --card-w: 216px;
  --thumb-h: 38px;
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
/* El separador va aparte del subtitulo para poder esconder los dos juntos en
   celular: dentro del texto plano dejaba un "Caso Hermosilla ·" colgando. */
h1 .sep { font-style: normal; }

.progreso {
  font-variant-numeric: tabular-nums;
  font-size: 0.82rem;
  color: var(--text-muted);
  white-space: nowrap;
}
.progreso b { color: var(--text); font-size: 1.05rem; }
/* El numero grande es el del hito, el mismo que sale en la tarjeta y con el que
   se dicta. La fraccion es cuanto se lleva expuesto y va aparte, para que no se
   confundan: no coinciden, porque los hitos omitidos no ocupan posicion. */
.avance {
  margin-left: 9px;
  padding-left: 9px;
  border-left: 1px solid var(--border);
  font-size: 0.72rem;
  opacity: 0.75;
}
.avance span { font-variant-numeric: tabular-nums; }

/* Se puede pinchar y arrastrar para saltar a cualquier punto del relato. */
.barra {
  flex: 1;
  height: 10px;
  background: #222933;
  border-radius: 5px;
  min-width: 60px;
  cursor: pointer;
  position: relative;
  border: 1px solid transparent;
}
.barra:hover, .barra.tirando { border-color: var(--accent); }
.barra i {
  display: block;
  height: 100%;
  width: 0;
  background: var(--accent);
  border-radius: 5px;
  transition: width 0.3s ease;
}
.barra.tirando i { transition: none; }
/* Tirador: aparece al pasar el mouse, para que se note que se puede arrastrar */
.barra::after {
  content: '';
  position: absolute;
  top: 50%; left: var(--pos, 0%);
  width: 13px; height: 13px;
  margin-left: -6px;
  border-radius: 50%;
  background: var(--accent);
  border: 2px solid #11151B;
  transform: translateY(-50%) scale(0);
  transition: transform 0.15s ease;
}
.barra:hover::after, .barra.tirando::after { transform: translateY(-50%) scale(1); }

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
  opacity: 0;
  transform: translateX(-10px);
  transition: opacity 0.55s ease, transform 0.55s ease;
}
.etiqueta.viva { opacity: 1; transform: none; }
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
  overflow: auto;
  scrollbar-width: thin;
  scrollbar-color: #39414E var(--bg);
}
.scroll::-webkit-scrollbar { height: 9px; width: 9px; }
.scroll::-webkit-scrollbar-thumb { background: #39414E; border-radius: 5px; }

.pista { position: relative; padding-top: 34px; }

/* Un carril no existe hasta que aparece el hito que abre su arista: arrancar
   con los 7 dibujados vacios adelanta el final y no ayuda a leer. */
.carril {
  position: absolute;
  left: 0; right: 0;
  height: var(--lane-h);
  border-bottom: 1px dashed #1C222B;
  opacity: 0;
  transition: opacity 0.55s ease;
}
.carril.abierta { opacity: 1; }
/* Franja tenue del color de la arista, para no perder el carril de vista */
.carril::before {
  content: '';
  position: absolute;
  left: 0; right: 0; top: 0; bottom: 0;
  background: currentColor;
  opacity: 0.028;
}

svg.lineas { position: absolute; inset: 0; overflow: visible; pointer-events: none; }

/* ── Tarjeta de hito ────────────────────────────────────────────── */
.nodo {
  position: absolute;
  transform: translate(-50%, -50%);
  width: var(--card-w);
  cursor: pointer;
  z-index: 3;
}

.tarjeta {
  position: relative;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 9px;
  overflow: hidden;
  opacity: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.35);
  transition: transform 0.25s cubic-bezier(.2,.9,.3,1.3),
              box-shadow 0.25s ease, opacity 0.25s ease, border-color 0.25s ease;
}

/* Franja superior: un segmento por arista. Un hecho que pertenece a dos o tres
   aristas se lee como tal sin necesidad de dibujarlo dos veces en el lienzo. */
.t-franja { display: flex; height: 4px; flex: none; }
.t-franja i { flex: 1; }

.tarjeta img {
  width: 100%;
  height: var(--thumb-h);
  object-fit: cover;
  display: block;
  border-bottom: 1px solid var(--border);
  background: #12161C;
}

.t-cab {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 7px 0;
  font-size: 0.55rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
}
.t-cab i {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--c); flex: none;
}
/* Numero del hito en la cronologia: es el que se usa para dictar correcciones,
   asi que tiene que estar a la vista y no depender de la posicion. */
.t-cab b {
  color: var(--text);
  background: #262E3A;
  border-radius: 4px;
  padding: 1px 4px;
  margin-right: 1px;
  font-size: 0.92em;
}

/* El tamano de letra lo fija ajustarTitulo() en JS, hito por hito, para que el
   titulo entre completo: aca no se corta ni se pone elipsis. */
.t-tit {
  padding: 3px 7px 7px;
  font-weight: 700;
  line-height: 1.25;
  color: #DDE3EC;
  overflow-wrap: break-word;
  hyphens: auto;
}

/* Todas las tarjetas pesan lo mismo. Antes los hitos "clave" iban al 90% de
   opacidad y el resto al 62%, y el diagrama se leia como si la mitad de los
   hechos estuvieran a medio apagar. La jerarquia la lleva ahora una sola cosa:
   abrir una arista. */

/* El hito que inaugura una trama: es el unico que se destaca del resto, con el
   color de la arista que abre (--a, que no siempre es la del carril donde cae)
   en el borde y en una franja mas gruesa. */
.nodo.abre .tarjeta {
  border-color: var(--a);
  box-shadow: 0 0 0 1px var(--a), 0 5px 18px rgba(0,0,0,0.5);
}
.nodo.abre .t-franja { height: 7px; }

.nodo:hover .tarjeta {
  opacity: 1;
  transform: translateY(-3px);
  border-color: var(--c);
  box-shadow: 0 6px 18px rgba(0,0,0,0.5);
}

.nodo.actual .tarjeta {
  opacity: 1;
  border-color: var(--accent);
  border-top-color: var(--c);
  box-shadow: 0 0 0 2px rgba(244,162,97,0.55), 0 8px 26px rgba(0,0,0,0.6);
  transform: scale(1.06);
}
.nodo.actual .t-tit { color: var(--text); }

/* Hasta donde iba el relato, mientras se revisa un hito anterior: marca tenue
   para no perder el punto de avance. */
.nodo.frontera .tarjeta {
  opacity: 1;
  box-shadow: 0 0 0 2px rgba(236,239,244,0.28), 0 6px 18px rgba(0,0,0,0.5);
}

/* Marca de "aqui se abre una arista nueva": va sobre la foto para no sumar
   alto a la tarjeta. Sin foto cae al flujo normal, arriba del todo. */
.t-nueva {
  display: block;
  background: rgba(20,26,34,0.82);
  color: #7CD992;
  font-size: 0.5rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 3px 7px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tarjeta img + .t-nueva {
  position: absolute;
  top: 4px; left: 0; right: 0;
  backdrop-filter: blur(2px);
}

/* Donde la vertical de un cruce toca el otro carril. Antes era un circulo del
   tamano de un hito y se leia como un hecho duplicado; ahora es una marquita
   que no se puede confundir con una tarjeta. */
.cruce-marca {
  position: absolute;
  width: 3px; height: 13px;
  border-radius: 2px;
  transform: translate(-50%, -50%);
  z-index: 2;
  opacity: 0.8;
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

/* Animacion de aparicion (solo opacidad: el transform ya centra la tarjeta) */
.nodo { animation: surge 0.4s ease; }
.cruce-marca { animation: surge-p 0.42s cubic-bezier(.2,.9,.3,1.3); }
@keyframes surge   { from { opacity: 0; } to { opacity: 1; } }
@keyframes surge-p {
  from { opacity: 0; transform: translate(-50%,-50%) scaleY(0.2); }
  to   { opacity: 0.8; }
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
/* Los intervinientes son botones: al activarlos se hilan con punteada todos los
   hitos donde aparece esa persona. Es la vista por persona a pedido, en vez de
   dibujarlas todas siempre y tapar el diagrama. */
.tag {
  display: inline-block;
  font-size: 0.7rem;
  background: #1D232C; border: 1px solid var(--border);
  color: var(--text-muted);
  padding: 3px 9px; border-radius: 5px; margin: 0 4px 4px 0;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
}
.tag:hover { border-color: var(--text-muted); color: var(--text); }
.tag.activo {
  background: var(--p, var(--accent));
  border-color: var(--p, var(--accent));
  color: #14181E;
  font-weight: 700;
}

/* Barra de personas activas, en el header */
.personas { display: flex; gap: 6px; align-items: center; }
.persona-chip {
  display: inline-flex; align-items: center; gap: 6px;
  font-size: 0.72rem; font-weight: 700;
  color: #14181E;
  padding: 3px 5px 3px 9px; border-radius: 20px;
  white-space: nowrap;
}
.persona-chip button {
  all: unset;
  cursor: pointer;
  line-height: 1;
  padding: 0 3px;
  opacity: 0.65;
  font-weight: 900;
}
.persona-chip button:hover { opacity: 1; }

/* Con filtro activo solo quedan los hitos de esa persona, marcados con su color */
.nodo.resalta .tarjeta {
  opacity: 1;
  border-color: var(--p);
  box-shadow: 0 0 0 2px var(--p), 0 6px 18px rgba(0,0,0,0.55);
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

.revisando {
  background: rgba(236,239,244,0.06);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 15px;
  font-size: 0.78rem;
  line-height: 1.5;
  color: var(--text-muted);
}
.revisando button { display: block; margin-top: 8px; padding: 6px 11px; font-size: 0.76rem; }

/* Pantalla completa / presentacion */
/* En pantalla completa medir() recalcula el alto de carril al recibir resize. */
body.presenta header { padding: 9px 18px; }

@media (max-width: 1100px) {
  aside { width: 320px; }
}

/* La piel se inyecta aca y no al final del bloque: es cosmetica (colores y
   tipografia) y tiene que pisar al CSS base, pero no al layout de celular que
   viene despues, que es lo unico que hace que la pagina se pueda usar con el
   dedo. Si se colara despues, en la version noventera el panel volveria a ser
   una columna de 380 px dentro de una pantalla de 360. */
__PIEL__

/* ── Celular ────────────────────────────────────────────────────────
   En pantalla chica no caben header + carriles + panel al mismo tiempo, asi
   que el panel deja de ser una columna y pasa a ser una hoja que sube desde
   abajo cuando se toca un hito, y la navegacion baja a una barra fija con
   botones del tamano de un dedo. El diagrama en si no cambia: sigue siendo el
   mismo lienzo con scroll, solo con tarjetas y carriles mas apretados (eso lo
   decide medir() en JS, no el CSS). */
.barra-movil { display: none; }
.tapa { display: none; }

@media (max-width: 820px) {
  /* Los 100vh de iOS incluyen la barra de direcciones, que se retrae al hacer
     scroll: la barra de navegacion quedaba cortada abajo. 100dvh mide el alto
     que de verdad se ve. */
  body { height: 100vh; height: 100dvh; }

  header {
    flex-wrap: wrap;
    gap: 8px 12px;
    padding: 9px 12px;
  }
  /* Sin esto los hijos de un flex no bajan de su ancho de contenido: el
     contador y los botones se salian por la derecha en vez de encogerse. */
  header > * { min-width: 0; }
  h1 { font-size: 0.82rem; flex: 1 1 auto; overflow: hidden; text-overflow: ellipsis; }
  /* El subtitulo del h1 se come una linea entera y no dice nada que el titulo
     no diga ya. */
  h1 span, h1 .sep { display: none; }
  .progreso { font-size: 0.74rem; flex: 0 1 auto; overflow: hidden; }
  .controles { margin-left: auto; flex: none; }
  .barra { order: 3; flex-basis: 100%; height: 14px; }
  .personas { order: 4; flex-basis: 100%; flex-wrap: wrap; gap: 5px; }
  /* En el header solo queda el salto de version: el resto de los controles
     vive en la barra de abajo, al alcance del pulgar. */
  .controles { gap: 6px; }
  .controles #btn-reinicio,
  .controles #btn-atras,
  .controles #btn-sig,
  .controles #btn-auto,
  .controles #btn-full { display: none; }
  #btn-piel { padding: 6px 10px; font-size: 0.78rem; }

  .cuerpo { flex-direction: column; min-height: 0; }
  .lienzo { flex: 1; min-height: 0; }
  .etiquetas {
    width: 104px;
    background: linear-gradient(90deg, var(--bg) 68%, transparent);
    padding-top: 30px;
  }
  .etiqueta { padding-left: 9px; font-size: 0.62rem; }
  .etiqueta i { width: 7px; height: 7px; margin-right: 6px; }

  /* Arrastrar con el dedo por el lienzo tiene que mover el lienzo, no
     seleccionar texto ni disparar el zoom de doble toque. */
  .scroll { -webkit-overflow-scrolling: touch; overscroll-behavior: contain; }
  .nodo { -webkit-tap-highlight-color: transparent; }

  /* Sin mouse no hay hover, pero el navegador deja el ultimo estado pegado
     despues de tocar: se apaga para que no quede una tarjeta levantada. */
  .nodo:hover .tarjeta { transform: none; box-shadow: 0 2px 8px rgba(0,0,0,0.35); }

  /* Panel: hoja inferior. Fuera del flujo, tapando el lienzo solo mientras se
     lee un hito. */
  aside {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    width: auto;
    height: 74dvh;
    max-height: 74dvh;
    border-left: none;
    border-top: 1px solid var(--border);
    border-radius: 14px 14px 0 0;
    padding: 16px 16px 90px;
    box-shadow: 0 -8px 30px rgba(0,0,0,0.6);
    transform: translateY(101%);
    transition: transform 0.28s cubic-bezier(.2,.8,.3,1);
    z-index: 40;
    overscroll-behavior: contain;
  }
  body.hoja aside { transform: none; }
  /* Agarradera: la raya de arriba que dice "esto se cierra tirando" */
  aside::before {
    content: '';
    position: sticky;
    top: -6px;
    display: block;
    width: 42px; height: 4px;
    margin: -6px auto 12px;
    border-radius: 3px;
    background: var(--border);
  }

  .tapa {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.28s ease;
    z-index: 39;
  }
  body.hoja .tapa { opacity: 1; pointer-events: auto; }

  .p-titulo { font-size: 1rem; }
  .p-img { max-height: 190px; }
  .p-desc { font-size: 0.9rem; }
  /* Los intervinientes y las fuentes son los dos sitios donde se toca: con
     44 px de alto dejan de fallar los dedos. */
  .tag { font-size: 0.8rem; padding: 8px 12px; }
  .p-fuente { padding: 11px 12px; font-size: 0.8rem; }

  /* Barra de navegacion fija */
  .barra-movil {
    display: flex;
    flex: none;
    gap: 8px;
    padding: 9px 12px;
    padding-bottom: calc(9px + env(safe-area-inset-bottom));
    border-top: 1px solid var(--border);
    /* Variable y no color fijo: asi la barra acompana a la piel que este puesta
       en vez de quedar azul oscura sobre el verde noventero. */
    background: var(--bg-card);
    z-index: 45;
  }
  .barra-movil button {
    flex: none;
    min-width: 44px;
    min-height: 44px;
    font-size: 0.9rem;
    padding: 8px 10px;
  }
  /* "Siguiente" es el boton que se pulsa 111 veces: se queda con todo el ancho
     que sobre. Los otros dos encogen antes que desbordar. */
  .barra-movil #m-sig { flex: 1 1 0; min-width: 0; }
  .barra-movil #m-detalle { flex: 0 1 auto; min-width: 0; overflow: hidden; }
  /* Cerrar la hoja es la accion obvia mientras esta abierta, asi que el boton
     de detalle cambia de papel en vez de sumar otro boton. */
  body.hoja .barra-movil { position: relative; z-index: 45; }
}

/* Pantallas muy angostas: los rotulos de texto largo estorban mas que ayudan */
@media (max-width: 380px) {
  .etiquetas { width: 84px; }
  .etiqueta { font-size: 0.56rem; }
  .barra-movil #m-sig { font-size: 0.85rem; }
}
</style>
</head>
<body>

<header>
  <h1>Caso Hermosilla<i class="sep"> · </i><span>flujo de los hechos</span></h1>
  <div class="progreso">Hito <b id="n-hito">—</b><span class="avance">avance
    <span id="n-actual">0</span>/<span id="n-total">__TOTAL__</span></span></div>
  <div class="barra"><i id="barra"></i></div>
  <div class="personas" id="personas"></div>
  <div class="controles">
    <button id="btn-reinicio" title="Volver al inicio (Inicio)">⟲</button>
    <button id="btn-atras" title="Anterior (←)">‹ Atrás</button>
    <button id="btn-sig" class="primario" title="Siguiente (→ o Espacio)">Siguiente ›</button>
    <button id="btn-auto" title="Reproducir solo">▶ Auto</button>
    <button id="btn-piel" onclick="location.href='__OTRA__'"
            title="__OTRA_TIT__">__OTRA_TXT__</button>
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
  <div class="tapa" id="tapa"></div>
  <aside id="panel"></aside>
</div>

<nav class="barra-movil">
  <button id="m-reinicio" title="Volver al inicio">⟲</button>
  <button id="m-atras" title="Anterior">‹</button>
  <button id="m-sig" class="primario" title="Siguiente">Siguiente ›</button>
  <button id="m-detalle" title="Ver el detalle del hito">Detalle</button>
</nav>

<script>
const ARISTAS = __ARISTAS__;
const ORDEN   = __ORDEN__;
const NODOS   = __NODOS__;

const TOP = 34;

// Geometria del lienzo. En celular la tarjeta se angosta, los carriles se
// aprietan y el hueco de la izquierda se achica con las etiquetas, asi que
// nada de esto puede ser constante: lo fija medir() segun la pantalla real.
let CARD_W = 216, STEP = CARD_W + 30, X0 = 200 + CARD_W / 2;

// Alto de carril y de miniatura: se ajustan al alto de pantalla para que los
// 7 carriles quepan sin scroll vertical en la mayoria de los proyectores.
let LANE_H = 108, THUMB_H = 38;

const MQ_MOVIL = window.matchMedia('(max-width: 820px)');
let movil = MQ_MOVIL.matches;

let paso = -1;          // ultimo indice revelado
let seleccion = -1;     // hito que se esta mirando (-1 = el ultimo revelado)
let auto = null;
let tirando = false;    // arrastrando la barra de avance

/* Personas resaltadas: nombre normalizado -> etiqueta visible. Al activar una,
   se hilan con punteada todos los hitos revelados donde aparece. */
const personas = new Map();
const PALETA = ['#F4A261', '#7CD992', '#5AC8FA', '#FF7AB6', '#C9A0FF', '#FFD166'];
const colorDe = p => PALETA[[...personas.keys()].indexOf(p) % PALETA.length];

let pasoGuardado = null;   // avance del relato mientras dura el filtro

function aplicarFiltro() {
  if (personas.size) {
    // Al filtrar se muestran todos los hitos de esa persona de una vez: la
    // gracia es revisarlos juntos, no volver a avanzarlos de a uno.
    if (pasoGuardado === null) pasoGuardado = paso;
    paso = visibles().length - 1;
  } else if (pasoGuardado !== null) {
    paso = pasoGuardado;
    pasoGuardado = null;
  }
  seleccion = -1;
  pararAuto();
  pintarCarriles();
  redibujar(false);
  $('scroll').scrollTo({ left: 0 });
}

function alternarPersona(clave, etiqueta) {
  if (personas.has(clave)) personas.delete(clave);
  else if (personas.size < PALETA.length) personas.set(clave, etiqueta);
  aplicarFiltro();
}
function limpiarPersonas() { personas.clear(); aplicarFiltro(); }

const $ = id => document.getElementById(id);

// Con personas resaltadas el diagrama se reduce a los hitos donde aparecen, y
// se juntan: dejarlos en su sitio con el resto atenuado obligaba a barrer todo
// el ancho para encontrarlos.
const visibles = () => personas.size
  ? NODOS.filter(n => n.pers.some(p => personas.has(p)))
  : NODOS;

function medir() {
  movil = MQ_MOVIL.matches;
  const angosto = window.innerWidth <= 380;

  // Una tarjeta de 216 px en una pantalla de 360 ocupa el ancho entero: no se
  // alcanza a ver que hay un hito antes y otro despues, que es justo lo que el
  // diagrama tiene que mostrar.
  CARD_W = movil ? (angosto ? 132 : 146) : 216;
  STEP   = CARD_W + (movil ? 16 : 30);
  // Hueco de la izquierda: tan ancho como las etiquetas de carril, para que el
  // primer hito no nazca debajo de su rotulo.
  X0 = (movil ? (angosto ? 88 : 108) : 200) + CARD_W / 2;

  // El alto disponible es el del lienzo, no el de la ventana. En celular el
  // header envuelve a dos lineas y abajo va la barra de navegacion: restar
  // solo el header daba de mas y los ultimos carriles caian fuera de pantalla.
  const lienzo = document.querySelector('.lienzo');
  const alto = lienzo.clientHeight
    || (window.innerHeight - document.querySelector('header').offsetHeight);
  const disp = alto - TOP - 26;

  // Si ni al minimo caben los 7 carriles, el lienzo hace scroll vertical: es
  // preferible a encogerlos hasta que la tarjeta no se lea.
  LANE_H  = Math.max(movil ? 58 : 76, Math.min(122, Math.floor(disp / ORDEN.length)));
  THUMB_H = LANE_H >= 104 ? 38 : LANE_H >= 90 ? 30 : 0;   // 0 = sin foto
  const r = document.documentElement.style;
  r.setProperty('--lane-h', LANE_H + 'px');
  r.setProperty('--thumb-h', THUMB_H + 'px');
  r.setProperty('--card-w', CARD_W + 'px');
}

function laneY(arista) {
  return TOP + ORDEN.indexOf(arista) * LANE_H + LANE_H / 2;
}
function posX(pos) { return X0 + pos * STEP; }

/* ── Ajuste del titulo a la tarjeta ─────────────────────────────────
   Los titulos van de 44 a 127 caracteres, asi que un tamano fijo o los corta o
   desperdicia la tarjeta. Se estima cuantas lineas ocupa cada uno y se baja la
   letra hasta que entre entero. Es una estimacion por ancho medio de caracter
   en vez de medir el DOM: medir 112 tarjetas en cada paso provoca un reflow por
   tarjeta y la navegacion se siente pegajosa. */
const EM_CHAR = 0.53;          // ancho medio de caracter, en fracciones de em
const FS_MAX = 11.5, FS_MIN = 9;
const LH = 1.25;

function cajaTitulo(conFoto) {
  return {
    w: CARD_W - 14,                                            // padding lateral
    h: LANE_H - 4 - (conFoto ? THUMB_H : 0) - 14 - 10 - 4      // franja, foto, fecha, padding
  };
}

function lineasQueOcupa(texto, fs, w) {
  const porLinea = Math.max(6, Math.floor(w / (fs * EM_CHAR)));
  // Las palabras no se parten, asi que las lineas quedan irregulares: 6% de
  // holgura evita que un titulo se desborde por un salto desafortunado.
  return Math.ceil(texto.length / porLinea * 1.06);
}

function entra(texto, fs, conFoto) {
  const c = cajaTitulo(conFoto);
  return lineasQueOcupa(texto, fs, c.w) * fs * LH <= c.h;
}

function ajustarTitulo(texto, conFoto) {
  for (let fs = FS_MAX; fs > FS_MIN; fs -= 0.5) {
    if (entra(texto, fs, conFoto)) return fs;
  }
  return FS_MIN;
}

// Si ni al minimo entra el titulo completo, se usa el rotulo corto: preferible
// a dejarlo cortado con puntos suspensivos.
function tituloDeTarjeta(n, conFoto) {
  return entra(n.titulo, FS_MIN, conFoto) ? n.titulo : n.corto;
}

// Mismo criterio que norm() en Python: 'Ángela Vivanco (exministra)' -> 'ángela
// vivanco', para que la misma persona escrita distinto sea la misma persona.
function normJS(nombre) {
  return String(nombre).split('(')[0].trim().toLowerCase().split(/\s+/).join(' ');
}

function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

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
    d.dataset.a = a;
    d.style.top = (TOP + i * LANE_H) + 'px';
    d.style.color = ARISTAS[a].color;
    pista.appendChild(d);
  });

  const lista = visibles();
  pista.style.width = (posX(lista.length) + 260) + 'px';
  pista.style.height = (TOP + ORDEN.length * LANE_H + 24) + 'px';

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
  pista.querySelectorAll('.nodo,.cruce-marca').forEach(e => e.remove());
  svg.innerHTML = '';

  const lista = visibles();
  const hasta = Math.min(paso, lista.length - 1);
  // 'hasta' es hasta donde se revelo el diagrama; 'mirando' es el hito que se
  // esta leyendo en el panel. Son distintos para poder volver a revisar un
  // hecho anterior sin borrar lo que ya se conto.
  const mirando = Math.min(seleccion < 0 ? hasta : seleccion, hasta);
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
    const esActual   = i === mirando;
    const esFrontera = i === hasta && hasta !== mirando;

    // Hilo del propio carril
    const ant = ultimoPorArista[n.principal];
    if (ant !== undefined) {
      linea(posX(ant), y, x, y, color, 2.2, null, 0.5);
    }

    // Cruces explicitos: el hecho pertenece a otra arista tambien
    n.cruces.forEach(a => {
      const y2 = laneY(a);
      linea(x, y, x, y2, ARISTAS[a].color, 2, '4 3', esActual ? 0.9 : 0.5);
      // Marquita en el punto donde la vertical toca el otro carril: senala el
      // cruce sin parecer un hito aparte. El hecho se dibuja una sola vez.
      const c = document.createElement('div');
      c.className = 'cruce-marca';
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
      // Con tarjetas grandes estas lineas ensucian mucho: solo se destacan las
      // del hecho actual, el resto queda como rastro tenue.
      linea(posX(p), laneY(e.de), x, y, esActual ? '#8B97AB' : '#5A6474',
            esActual ? 1.6 : 1, '2 5', esActual ? 0.9 : 0.13);
    });

    const suyas = [...personas.keys()].filter(p => n.pers.includes(p));
    const d = document.createElement('div');
    // 'clave' ya no cambia como se ve la tarjeta, pero se sigue emitiendo
    // porque el dato viaja en NODOS y lo usan las correcciones.
    d.className = 'nodo' + (n.clave ? ' clave' : '')
                + (n.abre.length ? ' abre' : '')
                + (esActual ? ' actual' : '') + (esFrontera ? ' frontera' : '')
                + (suyas.length ? ' resalta' : '');
    if (n.abre.length) d.style.setProperty('--a', ARISTAS[n.abre[0]].color);
    if (suyas.length) d.style.setProperty('--p', colorDe(suyas[0]));
    d.style.left = x + 'px';
    d.style.top = y + 'px';
    d.style.setProperty('--c', color);
    d.title = n.fecha + ' — ' + n.titulo;

    const foto = (n.imagen && THUMB_H > 0)
      ? `<img src="${esc(n.imagen)}" alt="" loading="lazy"
              referrerpolicy="no-referrer" onerror="this.remove()">` : '';
    const nueva = n.abre.length
      ? `<span class="t-nueva">Abre ${esc(ARISTAS[n.abre[0]].label)}</span>` : '';

    // Franja: el carril propio primero, despues las otras aristas del hecho.
    const franja = [n.principal].concat(n.cruces)
      .map(a => `<i style="background:${ARISTAS[a].color}"></i>`).join('');

    const conFoto = foto !== '';
    const texto = tituloDeTarjeta(n, conFoto);
    d.innerHTML = `<div class="tarjeta">
        <div class="t-franja">${franja}</div>
        ${foto}${nueva}
        <div class="t-cab"><i></i><b>${n.n}</b>${esc(n.fecha)}</div>
        <div class="t-tit" style="font-size:${ajustarTitulo(texto, conFoto)}px">${esc(texto)}</div>
      </div>`;
    // Clic = mirar ese hito, no retroceder. El avance queda donde estaba.
    // En celular el detalle no esta a la vista, asi que tocar el hito ademas
    // sube la hoja: si no, el toque no parece hacer nada.
    d.onclick = () => { seleccion = i; redibujar(false); abrirHoja(); };
    pista.appendChild(d);

    ultimoPorArista[n.principal] = i;
  }

  // Hilo de cada persona resaltada: une en orden los hitos ya revelados donde
  // aparece. Se dibuja al final para que quede por encima del resto.
  personas.forEach((etiqueta, p) => {
    const col = colorDe(p);
    const pts = [];
    for (let i = 0; i <= hasta; i++) if (lista[i].pers.includes(p)) pts.push(i);
    for (let k = 0; k < pts.length - 1; k++) {
      const a = lista[pts[k]], b = lista[pts[k + 1]];
      linea(posX(pts[k]), laneY(a.principal), posX(pts[k + 1]), laneY(b.principal),
            col, 1.8, '3 4', 0.9);
    }
  });

  $('personas').innerHTML = personas.size
    ? [...personas].map(([p, et]) =>
        `<span class="persona-chip" style="background:${colorDe(p)}">${esc(et)}
           <button onclick="alternarPersona('${esc(p).replace(/'/g, "\\'")}')">✕</button>
         </span>`).join('') +
      (personas.size > 1 ? `<button onclick="limpiarPersonas()">Limpiar</button>` : '')
    : '';

  // Carriles y etiquetas de las aristas ya abiertas: los demas ni se dibujan.
  const abiertas = new Set();
  for (let i = 0; i <= hasta; i++) lista[i].aristas.forEach(a => abiertas.add(a));
  document.querySelectorAll('.etiqueta').forEach(el =>
    el.classList.toggle('viva', abiertas.has(el.dataset.a)));
  pista.querySelectorAll('.carril').forEach(el =>
    el.classList.toggle('abierta', abiertas.has(el.dataset.a)));

  $('n-hito').textContent = mirando >= 0 ? lista[mirando].n : '—';
  $('n-actual').textContent = hasta + 1 < 0 ? 0 : hasta + 1;
  $('n-total').textContent = lista.length;
  const pct = lista.length ? (hasta + 1) / lista.length * 100 : 0;
  $('barra').style.width = pct + '%';
  barra.style.setProperty('--pos', pct + '%');
  $('btn-atras').disabled = hasta < 0;
  $('btn-sig').disabled = hasta >= lista.length - 1;
  $('m-atras').disabled = hasta < 0;
  $('m-sig').disabled = hasta >= lista.length - 1;
  $('m-detalle').disabled = mirando < 0;
  sincHoja();

  panel(mirando >= 0 ? lista[mirando] : null, lista, posDe, mirando !== hasta);

  if (scrollTo && mirando >= 0) {
    const s = $('scroll');
    s.scrollTo({ left: posX(mirando) - s.clientWidth * 0.62, behavior: 'smooth' });
  }
}

/* ── Panel de detalle ───────────────────────────────────────────── */
function panel(n, lista, posDe, revisando) {
  const el = $('panel');
  if (!n) {
    el.innerHTML = `<div class="vacio">
      Pulsa <b>Siguiente</b> (o la flecha →) para ir levantando el caso hecho por hecho.<br><br>
      Cada carril es una arista, y aparece cuando entra el hito que la abre.
      Cuando un hecho pertenece a dos aristas, se dibuja la línea vertical que
      las cruza. Las líneas punteadas grises marcan de dónde sale un hecho.
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

  const volver = revisando ? `<div class="revisando">
      Estás revisando un hito anterior. El avance sigue más adelante.
      <button onclick="volverAlAvance()">Volver al punto actual</button>
    </div>` : '';

  el.innerHTML = `
    ${volver}
    <div class="p-fecha">Hito ${n.n} · ${n.fecha}</div>
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
      ${n.intervinientes.map((nom, k) => {
          const p = n.pers.find(x => x === normJS(nom)) || normJS(nom);
          const on = personas.has(p);
          return `<button class="tag${on ? ' activo' : ''}"
            ${on ? `style="--p:${colorDe(p)}"` : ''}
            title="Resaltar todos los hitos con esta persona"
            onclick="alternarPersona('${esc(p).replace(/'/g, "\\'")}', '${esc(nom).replace(/'/g, "\\'")}')"
            >${esc(nom)}</button>`;
        }).join('')}
    </div>
    <div class="p-bloque">
      <h3>Fuentes</h3>
      ${n.fuentes.map(f => `<a class="p-fuente" href="${f.url}" target="_blank" rel="noopener">
          ${f.titulo}<br><span style="opacity:.65">${f.medio}</span></a>`).join('')}
    </div>`;
}

/* ── Controles ──────────────────────────────────────────────────── */
// Avanzar y retroceder mueven el relato y sueltan la revision: si estabas
// mirando un hito viejo, la flecha te devuelve al hilo en vez de saltar.
function sig()   { const l = visibles(); if (paso < l.length - 1) { paso++; seleccion = -1; redibujar(true); } else pararAuto(); }
function atras() { if (paso >= 0) { paso--; seleccion = -1; redibujar(true); } }
function reinicio() {
  paso = -1; seleccion = -1; pasoGuardado = null;
  pararAuto(); redibujar(false);
  $('scroll').scrollTo({left: 0, behavior: 'smooth'});
}
function volverAlAvance() { seleccion = -1; redibujar(true); }

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
/* ── Celular: hoja de detalle y barra de navegacion ─────────────── */
// La hoja solo existe en celular; en escritorio el panel esta siempre a la
// vista y estas funciones no hacen nada.
function abrirHoja()  { if (movil) { document.body.classList.add('hoja'); sincHoja(); } }
function cerrarHoja() { document.body.classList.remove('hoja'); sincHoja(); }
function sincHoja() {
  const b = $('m-detalle');
  if (b) b.textContent = document.body.classList.contains('hoja') ? 'Cerrar' : 'Detalle';
}

$('tapa').onclick = cerrarHoja;
$('m-detalle').onclick = () =>
  document.body.classList.contains('hoja') ? cerrarHoja() : abrirHoja();
// Avanzar con la hoja abierta taparia el hito que acaba de entrar.
$('m-sig').onclick      = () => { pararAuto(); cerrarHoja(); sig(); };
$('m-atras').onclick    = () => { pararAuto(); cerrarHoja(); atras(); };
$('m-reinicio').onclick = () => { cerrarHoja(); reinicio(); };

/* ── Barra de avance: pinchar o arrastrar para saltar ───────────── */
const barra = document.querySelector('.barra');

function pasoDesde(e) {
  const r = barra.getBoundingClientRect();
  const cx = e.touches && e.touches.length ? e.touches[0].clientX : e.clientX;
  const f = Math.min(1, Math.max(0, (cx - r.left) / r.width));
  const total = visibles().length;
  const nuevo = Math.min(total - 1, Math.max(-1, Math.round(f * total) - 1));
  if (nuevo === paso) return;      // sin esto se redibuja en cada pixel
  paso = nuevo;
  seleccion = -1;
  redibujar(true);
}

barra.addEventListener('mousedown', e => {
  e.preventDefault();
  pararAuto();
  tirando = true;
  barra.classList.add('tirando');
  pasoDesde(e);
});
window.addEventListener('mousemove', e => { if (tirando) pasoDesde(e); });
window.addEventListener('mouseup', () => {
  if (!tirando) return;
  tirando = false;
  barra.classList.remove('tirando');
});

// Lo mismo con el dedo. passive:false porque hay que impedir que el gesto se
// lo lleve el scroll de la pagina mientras se arrastra la barra.
barra.addEventListener('touchstart', e => {
  pararAuto();
  tirando = true;
  barra.classList.add('tirando');
  pasoDesde(e);
}, { passive: true });
barra.addEventListener('touchmove', e => {
  if (!tirando) return;
  e.preventDefault();
  pasoDesde(e);
}, { passive: false });
barra.addEventListener('touchend', () => {
  tirando = false;
  barra.classList.remove('tirando');
});

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

let reajuste = null;
window.addEventListener('resize', () => {
  clearTimeout(reajuste);
  reajuste = setTimeout(() => {
    medir();
    // Al girar el telefono o al pasar a escritorio la hoja queda flotando sobre
    // un panel que ya es columna: se cierra y el detalle vuelve a su sitio.
    if (!movil) cerrarHoja();
    pintarCarriles();
    redibujar(false);
  }, 150);
});

medir();
pintarEtiquetas();
pintarCarriles();
redibujar(false);
</script>
</body>
</html>
"""


def orden_visual(nodos):
    """Carriles ordenados por cuando se abre cada arista, no por ORDEN.

    Asi el carril nuevo siempre entra por abajo y los que ya estaban no se
    mueven: si se apilaran segun ORDEN, audio-sii (que abre cuarta) tendria que
    insertarse arriba de tres carriles ya dibujados y empujarlos hacia abajo.
    """
    primero = {}
    for n in nodos:
        for a in n['abre']:
            primero.setdefault(a, n['idx'])
    return sorted(ARISTAS, key=lambda a: (primero.get(a, 10 ** 6), ORDEN.index(a)))


# ── Piel experimental: portal noventero, version legible ────────────────────
# Solo cosmetica: se superpone al CSS base sin tocar una clase ni un id, asi que
# el JS es identico. Para descartarla, borrar esta constante y la linea que
# genera OUT_PIEL en main().
#
# El intento anterior fallaba por la tipografia, no por lo retro: Courier New a
# 9-11 px es de trazo muy fino, y encima las lineas de barrido le comian
# contraste. Aca el texto va en Verdana, que Microsoft dibujo en 1996
# precisamente para leerse en pantalla chica: es tan noventera como la Courier y
# se lee. La Courier queda solo en los metadatos, que van en cuerpo mayor.
PIEL = r"""
/* ═══ PIEL: PORTAL 90s ════════════════════════════════════════════════ */
:root {
  --bg: #0A1214;
  --bg-card: #1A2328;
  --bg-card-hover: #222D33;
  --border: #4A5A62;
  --text: #FFFFFF;
  --text-muted: #9FB4BD;
  --accent: #FFD400;
  --gris: #C0C0C0;
  --navy: #000080;
  --teal: #008080;
  --v: Verdana, Geneva, Tahoma, sans-serif;
  --m: "Courier New", monospace;
}

body {
  font-family: var(--v);
  background:
    linear-gradient(180deg, #0D181B 0%, #060C0E 100%);
}

/* ── Barra de titulo Windows 95 ───────────────────────────────────── */
header {
  background: linear-gradient(90deg, var(--navy) 0%, #1084D0 100%);
  border-bottom: 2px solid var(--gris);
  box-shadow: inset 0 1px 0 #6BA6D6;
}
h1 { font-family: var(--v); font-size: 0.88rem; color: #FFF; text-shadow: 1px 1px 0 rgba(0,0,0,0.6); }
h1 span { color: var(--accent); }
h1::before { content: "\25A0\00A0"; }

.progreso { font-family: var(--v); font-size: 0.76rem; color: #E8F4FF; }
.progreso b {
  font-family: var(--v);
  background: var(--accent); color: #000;
  border: 1px solid #000;
  padding: 1px 7px;
}
.avance {
  border-left-color: #6BA6D6; color: #E8F4FF;
  font-size: 0.7rem; letter-spacing: 0.05em;
}

/* Botones con bisel */
button {
  font-family: var(--v);
  font-size: 0.76rem;
  font-weight: 700;
  background: var(--gris);
  color: #000;
  border: 2px outset var(--gris);
  border-radius: 0;
  text-shadow: none;
}
button:hover:not(:disabled) { background: #D4D4D4; border-color: #D4D4D4; }
button:active:not(:disabled) { border-style: inset; }
button.primario { background: var(--accent); border-color: var(--accent); color: #000; }
button.primario:hover:not(:disabled) { background: #FFE550; border-color: #FFE550; }

.barra {
  background: #0A1214;
  border: 2px inset var(--gris);
  border-radius: 0;
  height: 15px;
}
.barra i {
  border-radius: 0;
  background: repeating-linear-gradient(90deg, var(--teal) 0 7px, #0A1214 7px 9px);
}
.barra::after { border-radius: 0; background: var(--accent); border-color: #000; }

/* ── Carriles ─────────────────────────────────────────────────────── */
.carril { border-bottom: 1px dotted rgba(159,180,189,0.4); }
.carril::before { opacity: 0.05; }
.anio-linea { background: rgba(159,180,189,0.25); }
.anio-marca {
  font-family: var(--v);
  font-size: 0.68rem;
  color: #000;
  background: var(--gris);
  border: 2px outset var(--gris);
  padding: 1px 7px;
  letter-spacing: 0.05em;
}
.etiqueta {
  font-family: var(--v);
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}
.etiqueta i { border-radius: 0; width: 11px; height: 11px; border: 1px solid rgba(0,0,0,0.5); }

/* ── Tarjetas: ventanitas con bisel ───────────────────────────────── */
.tarjeta {
  border-radius: 0;
  border: 2px outset var(--gris);
  background: var(--bg-card);
  box-shadow: 2px 2px 0 rgba(0,0,0,0.7);
}
.t-franja { height: 4px; }
.tarjeta img { border-bottom: 1px solid #000; }

/* Franja de metadatos: barra de estado de la ventana */
.t-cab {
  font-family: var(--v);
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: none;
  color: #CFE4EE;
  background: rgba(0,0,0,0.35);
  padding: 4px 7px;
  border-bottom: 1px solid rgba(0,0,0,0.5);
}
.t-cab i { border-radius: 0; width: 7px; height: 7px; }
.t-cab b {
  font-family: var(--v);
  background: var(--accent); color: #000;
  border: 1px solid #000; border-radius: 0;
  padding: 0 4px;
}
.t-tit {
  font-family: var(--v);
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.32;
  padding-top: 5px;
}
.t-tit { color: #D6E4EA; font-weight: 700; }

.t-nueva {
  background: var(--teal); color: #FFF;
  font-family: var(--v); font-weight: 700;
  letter-spacing: 0.06em;
}

.nodo:hover .tarjeta { transform: translate(-2px, -2px); box-shadow: 4px 4px 0 rgba(0,0,0,0.8); }
.nodo.actual .tarjeta {
  border: 2px outset var(--accent);
  box-shadow: 3px 3px 0 rgba(255,212,0,0.55), 0 0 20px rgba(255,212,0,0.25);
}
.nodo.frontera .tarjeta { box-shadow: 2px 2px 0 rgba(255,255,255,0.65); }
.nodo.resalta .tarjeta { border-color: var(--p); box-shadow: 3px 3px 0 var(--p); }
.cruce-marca { border-radius: 0; border-color: #000; }

/* ── Panel: ventana de propiedades ────────────────────────────────── */
aside { background: #121D21; border-left: 2px solid var(--gris); }
.p-fecha {
  font-family: var(--v); font-size: 0.68rem;
  color: #000; background: var(--gris);
  display: block; padding: 4px 8px;
  border: 2px outset var(--gris);
  letter-spacing: 0.03em;
}
.p-titulo { font-family: var(--v); font-size: 1rem; font-weight: 700; color: #FFF; }
.p-img { border: 2px inset var(--gris); border-radius: 0; }
.p-desc { font-family: var(--v); font-size: 0.8rem; line-height: 1.68; color: #DDE9EE; }
.p-bloque h3 {
  font-family: var(--v); font-size: 0.62rem;
  color: #FFF; background: var(--navy);
  display: block; padding: 4px 8px;
  border: 1px solid #000;
  letter-spacing: 0.1em;
}
.pill { border-radius: 0; font-family: var(--v); font-weight: 700; border: 1px solid #000; }
.tag {
  border-radius: 0;
  font-family: var(--v); font-size: 0.68rem; font-weight: 700;
  background: var(--gris); color: #000;
  border: 2px outset var(--gris);
  padding: 3px 8px;
}
.tag:hover { background: #D4D4D4; color: #000; border-color: #D4D4D4; }
.tag.activo { border-style: inset; }
.p-fuente {
  border-radius: 0;
  font-family: var(--v); font-size: 0.7rem;
  border: 1px solid var(--border);
  color: #9FD8EE;
}
.p-fuente:hover { background: #17262C; color: #FFF; text-decoration: underline; }
.aviso, .revisando { border-radius: 0; }
.aviso { background: rgba(255,212,0,0.1); }
.revisando { border: 2px inset var(--gris); font-family: var(--v); font-size: 0.74rem; }
.vacio { font-family: var(--v); font-size: 0.82rem; line-height: 1.7; color: #DDE9EE; }
.vacio::before {
  content: "\25BA BIENVENIDO AL CASO HERMOSILLA";
  display: block;
  background: var(--navy); color: #FFF;
  font-size: 0.7rem; font-weight: 700;
  padding: 5px 8px; margin-bottom: 14px;
  border: 1px solid #000;
  letter-spacing: 0.06em;
}
.persona-chip { border-radius: 0; border: 1px solid #000; font-family: var(--v); font-weight: 700; }
"""


def main():
    eventos = asignar_refs(cargar())
    numeros = {ev['_ref']: i + 1 for i, ev in enumerate(eventos)}
    eventos, avisos = aplicar_correcciones(eventos)
    nodos = preparar(eventos, numeros)
    visual = orden_visual(nodos)

    def j(o):
        return json.dumps(o, ensure_ascii=False).replace('</', '<\\/')

    def armar(piel, otra, texto, titulo):
        return (PLANTILLA
                .replace('__ARISTAS__',  j(ARISTAS))
                .replace('__ORDEN__',    j(visual))
                .replace('__NODOS__',    j(nodos))
                .replace('__TOTAL__',    str(len(nodos)))
                .replace('__OTRA_TIT__', titulo)
                .replace('__OTRA_TXT__', texto)
                .replace('__OTRA__',     otra)
                .replace('__PIEL__',     piel))

    # Cada version lleva un boton que salta a la otra. Son dos archivos
    # independientes: mismo diagrama, misma data, solo cambia el CSS.
    OUT.write_text(
        armar('', OUT_PIEL.name, '▣ 90s', 'Ver la versión noventera'),
        encoding='utf-8')
    OUT_PIEL.write_text(
        armar(PIEL, OUT.name, '▣ Actual', 'Volver a la versión actual'),
        encoding='utf-8')

    claves  = sum(1 for n in nodos if n['clave'])
    cruces  = sum(1 for n in nodos if n['cruces'])
    enlaces = sum(len(n['enlaces']) for n in nodos)
    print(f"flujo.html generado: {len(nodos)} hechos")
    print(f"  hitos clave (modo resumen): {claves}")
    print(f"  cruces explicitos (2+ aristas): {cruces}")
    print(f"  conexiones por interviniente: {enlaces}")
    print(f"  peso: {OUT.stat().st_size/1024:.0f} KB")
    print(f"  variante estética: {OUT_PIEL.name} ({OUT_PIEL.stat().st_size/1024:.0f} KB)")
    if CORR.exists():
        n = len(json.loads(CORR.read_text(encoding='utf-8')).get('hitos', []))
        print(f"  correcciones del flujo aplicadas: {n}")
    if avisos:
        print("  AVISOS:")
        for a in avisos:
            print(f"    - {a}")


if __name__ == '__main__':
    main()
