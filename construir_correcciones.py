#!/usr/bin/env python3
"""Escribe flujo_correcciones.json resolviendo numeros de hito a claves estables.

Las correcciones se dictan por numero, que es como se leen en pantalla y como se
conversan, y aca se traducen a la clave estable (URL de la primera fuente) que es
lo unico que aguanta que el JSONL se regenere desde cronologia.md.

Este es el archivo que se edita. flujo_correcciones.json es su salida.

  python construir_correcciones.py && python gen_flujo.py
"""

import io
import json
from pathlib import Path

import gen_flujo as g

BASE = Path(__file__).parent
EVS = g.asignar_refs(g.cargar())


def r(n):
    """Clave estable del hito numero n (1-based, como el contador en pantalla)."""
    return EVS[n - 1]['_ref']


def enlace(n, razon):
    """Linea punteada hacia el hito n, con el motivo que se muestra en el panel."""
    return {'ref': r(n), 'razon': razon, '_hito': n}


# ── Correcciones ────────────────────────────────────────────────────────────
# Campos: aristas, suma, quita, principal, clave, omitir, enlaces.
# 'enlaces': [] significa "no se vincula con nada", distinto de no revisado.
CORRECCIONES = [
    {'n': 2, 'aristas': ['parque-capital'],
     '_por_que': 'sigue enmarcado en Parque Capital; no es politico-diplomatico'},

    {'n': 5, 'aristas': ['factop'],
     '_por_que': 'todavia no abre el Caso Hermosilla: en este punto es solo Factop'},

    {'n': 6, 'enlaces': [enlace(5, 'el audio sale de esta reunión')],
     '_por_que': 'este es el que abre el Caso Hermosilla; su unico nexo real es la reunion grabada'},

    {'n': 7, 'enlaces': [],
     '_por_que': 'el vinculo con el 5 no existe'},

    {'n': 12, 'enlaces': [],
     '_por_que': 'no se vincula directamente con nada anterior'},

    {'n': 14, 'aristas': ['factop'], 'enlaces': [],
     '_por_que': 'pertenece solo a Factop y la punteada estaba de mas'},

    {'n': 15, 'enlaces': [],
     '_por_que': 'no se relaciona por linea punteada'},

    {'n': 16, 'enlaces': [],
     '_por_que': 'no se relaciona por linea punteada'},

    {'n': 18, 'enlaces': [],
     '_por_que': 'el vinculo con PDI era solo porque ambos reportajes son de CIPER'},

    {'n': 19, 'enlaces': [],
     '_por_que': 'mismo caso que el 18: el unico nexo era CIPER'},

    {'n': 20, 'aristas': ['bielorrusa'],
     'enlaces': [enlace(8, 'de la incautación del iPhone sale la acusación contra Vivanco')],
     '_por_que': 'abre Muñeca Bielorrusa, no Poder Judicial; su origen es el allanamiento'},

    {'n': 21, 'aristas': ['bielorrusa'],
     '_por_que': 'sale Poder Judicial'},

    {'n': 22, 'aristas': ['audio-sii'], 'enlaces': [],
     '_por_que': 'pertenece al Caso Hermosilla porque es de los chats'},

    {'n': 23, 'enlaces': [],
     '_por_que': 'no se vincula por linea punteada con nada'},

    {'n': 24, 'aristas': ['parque-capital'], 'enlaces': [],
     '_por_que': 'solo Parque Capital, sin linea punteada'},

    {'n': 25, 'enlaces': [],
     '_por_que': 'al corregir el 24 quedan vinculados en el mismo carril'},

    {'n': 26, 'aristas': ['bielorrusa'], 'enlaces': [],
     '_por_que': 'la destitucion de Vivanco es Muñeca Bielorrusa'},

    {'n': 27, 'aristas': ['poder-judicial'],
     'enlaces': [enlace(26, 'la destitución de Vivanco antecede a la de Muñoz')],
     '_por_que': 'este es el que abre Poder Judicial; se vincula con el 26'},

    {'n': 28, 'aristas': ['audio-sii'], 'enlaces': [],
     '_por_que': 'va en Caso Hermosilla'},

    {'n': 29, 'aristas': ['audio-sii'],
     '_por_que': 'va en Caso Hermosilla'},

    {'n': 30, 'aristas': ['audio-sii'],
     '_por_que': 'va en Caso Hermosilla'},

    {'n': 32, 'aristas': ['audio-sii'],
     '_por_que': 'va en Caso Hermosilla'},

    {'n': 33, 'aristas': ['parque-capital'],
     '_por_que': 'solo Parque Capital'},

    {'n': 35, 'enlaces': [],
     '_por_que': 'no se vincula por linea punteada con nada'},

    {'n': 38, 'omitir': True,
     '_por_que': 'hito malo: sale del diagrama (sigue en la cronologia)'},

    # Dictados leyendo el contador del diagrama, que iba corrido en +1 por la
    # omision del 38. Aca ya estan traducidos a numero de cronologia.
    {'n': 39, 'enlaces': [],
     '_por_que': 'no se vincula por linea punteada con nada'},

    {'n': 40, 'aristas': ['factop'],
     '_por_que': 'solo Factop'},

    {'n': 42, 'enlaces': [],
     '_por_que': 'no se vincula con nada'},

    {'n': 43, 'enlaces': [],
     '_por_que': 'quitar linea punteada'},

    {'n': 44, 'enlaces': [],
     '_por_que': 'quitar lineas punteadas'},

    {'n': 45, 'enlaces': [],
     '_por_que': 'quitar lineas punteadas'},

    {'n': 46, 'enlaces': [enlace(30, 'las gestiones salen de la lista de "La caja de Pandora"')],
     '_por_que': 'solo se vincula con La caja de Pandora'},

    {'n': 47, 'aristas': ['poder-judicial'], 'enlaces': [],
     '_por_que': 'Chadwick y el exfiscal Guerra: son gestiones ante fiscales, no '
                 'politico-diplomatico, que todavia no se abre aqui'},

    {'n': 48, 'aristas': ['audio-sii'],
     '_por_que': 'va solo en Caso Hermosilla'},

    {'n': 49, 'enlaces': [],
     '_por_que': 'quitar lineas punteadas'},

    {'n': 50, 'enlaces': [],
     '_por_que': 'va solo'},

    {'n': 51, 'enlaces': [],
     '_por_que': 'sin lineas punteadas'},

    {'n': 52, 'enlaces': [],
     '_por_que': 'sin lineas punteadas'},

    {'n': 53, 'enlaces': [],
     '_por_que': 'sin lineas punteadas'},
]

for c in CORRECCIONES:
    c['ref'] = r(c['n'])
    c['titulo'] = EVS[c['n'] - 1]['titulo']

salida = {
    '_ayuda': [
        "GENERADO por construir_correcciones.py — no editar a mano.",
        "",
        "Correcciones que valen SOLO para flujo.html. La linea de tiempo",
        "(cronologia.md / cronologia.jsonl / cronologia.html) no se toca desde aqui:",
        "gen_flujo.py lee el JSONL y aplica esto encima al vuelo, sin escribirlo.",
        "",
        "'ref' es la clave estable del hito: la URL de su primera fuente, mas el",
        "titulo cuando dos hitos comparten fuente. Aguanta que el JSONL se",
        "regenere; el numero de hito no, porque se corre al insertar uno nuevo.",
    ],
    'hitos': CORRECCIONES,
}

io.open(BASE / 'flujo_correcciones.json', 'w', encoding='utf-8').write(
    json.dumps(salida, ensure_ascii=False, indent=2) + '\n')

print('flujo_correcciones.json: %d hitos' % len(CORRECCIONES))
for c in CORRECCIONES:
    print('  %3d  %s' % (c['n'], c['titulo'][:58]))
