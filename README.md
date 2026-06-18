# Cronología: Caso Hermosilla

Línea de tiempo interactiva del caso de corrupción más complejo de la última década en Chile, también conocido como **Caso Audios** o **Caso Factop**.

🔗 **[Ver cronología online](https://roberttson.github.io/cronologia-caso-hermosilla/cronologia.html)**

---

## ¿Qué es esto?

Una base de datos cronológica de los hitos del Caso Hermosilla, construida desde reportajes de CIPER Chile, La Tercera, El Mostrador, The Clinic, BioBioChile, Cooperativa y otros medios verificados.

- **101 hitos** documentados (2020–2026)
- **184 fuentes** citadas con URL
- **7 aristas** del caso cubiertas

## Aristas

| Tag | Descripción |
|---|---|
| `audio-sii` | Núcleo del caso: soborno a funcionarios del SII y la CMF |
| `factop` | ~10.000 facturas falsas, suspensión de STF Capital y Factop, lavado vía Inversiones Guayasamín |
| `parque-capital` | Tráfico de influencias para acelerar permisos inmobiliarios de Grupo Patio |
| `poder-judicial` | Red de influencias sobre jueces y fiscales revelada por los chats |
| `pdi` | Filtración de secretos de investigación por el director de la PDI a Hermosilla |
| `politico-diplomatico` | Vínculos con Chadwick, Zaliasnik, Caso Penta y fondos reservados |
| `bielorrusa` | Pagos del consorcio Belaz-Movitec a la exjueza Vivanco por fallos contra Codelco |

## Archivos

| Archivo | Descripción |
|---|---|
| `cronologia.jsonl` | Datos en formato JSONL (una línea por evento) |
| `cronologia.md` | Datos en Markdown legible por humanos |
| `cronologia.html` | Visualización interactiva (autocontenida) |
| `gen_html.py` | Script Python que genera el HTML desde el JSONL |

## Uso de los datos

Los datos en `cronologia.jsonl` son de libre uso con atribución. Cada evento tiene la estructura:

```json
{
  "fecha": "14 noviembre 2023",
  "anio": 2023,
  "titulo": "CIPER publica el audio: estalla el escándalo",
  "desc": "...",
  "intervinientes": ["Luis Hermosilla", "CIPER Chile", "..."],
  "categorias": ["mediático", "judicial"],
  "aristas": ["audio-sii"],
  "fuentes": [{"titulo": "...", "url": "...", "medio": "CIPER Chile, 14/11/2023"}]
}
```

## Regenerar el HTML

```bash
python gen_html.py
```

---

Construido con fuentes públicas. Las fuentes primarias son los reportajes de [CIPER Chile](https://ciperchile.cl).

## Licencia

**Autor:** roberttson

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/deed.es)

Este trabajo está bajo una [Licencia Creative Commons Atribución 4.0 Internacional](https://creativecommons.org/licenses/by/4.0/deed.es). Puedes usar, compartir y adaptar libremente el contenido siempre que des crédito al autor.
