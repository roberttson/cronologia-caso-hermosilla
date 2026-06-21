# Protocolo de actualización — Cronología + Audios (Caso Hermosilla)

> Guía para la **próxima sesión de Claude Code**. Objetivo: agregar hitos/aristas
> y regenerar los audios **sin volver a sintetizar todo**, para **ahorrar tokens de
> Inworld TTS**. Cambiar **lo mínimo** del relato para mantener coherencia.

---

## 0. Principio de ahorro (leer antes de tocar nada)

Los audios se generan por **fragmentos** (trozos de párrafo). Cada fragmento se
guarda en una **caché indexada por el hash de su texto**:

```
audio_kevin/cache/<sha1>.wav
audio_relator/cache/<sha1>.wav
audio_salva/cache/<sha1>.wav
```

El hash = `voiceId | modelo | velocidad | temperatura | texto en minúsculas`.

➡️ **Si el texto de un párrafo no cambia, su hash no cambia y se reutiliza sin
llamar al API.** Solo los párrafos **nuevos o editados** cuestan tokens.

**Regla de oro de coherencia:** al agregar un hito, **NO reescribas párrafos que
no lo necesitan**. Cada párrafo que toques (aunque sea una coma) se vuelve a
sintetizar en las 3 voces. Edita el mínimo de párrafos posible y deja el resto
**idéntico carácter por carácter**.

> ⚠️ Nunca borres las carpetas `audio_*/cache/` — son el "banco de tokens".
> Están en `.gitignore` (no se suben), pero deben permanecer en el disco local.

---

## 1. Archivos que intervienen

| Archivo | Rol |
|---|---|
| `cronologia.md` / `cronologia.jsonl` | Datos de la línea de tiempo (hitos) |
| `gen_html.py` | Regenera el array de eventos dentro de `cronologia.html` |
| `cronologia.html` | El sitio (timeline + reproductor de pódcast) |
| `guion_tts_caso_hermosilla_v2.md` | **Guion del relato — voz Kevin** (canónico) |
| `guion_tts_relator.md` | Mismo relato, narrador anónimo (**Pudito** en la web) |
| `guion_tts_salva.md` | Mismo relato, narrador **Salvador** |
| `actualizar_audios.py` | **Pipeline incremental**: sintetiza solo lo nuevo, ensambla y exporta MP3 |
| `audio/kevin.mp3` `audio/relator.mp3` `audio/salva.mp3` | MP3 finales que usa el sitio |

Diferencias entre los 3 guiones (mantenerlas al editar):
- **Kevin**: dice "Yo soy Kevin…" en la bienvenida y el cierre.
- **Relator/Pudito**: narrador **sin nombre** (no se presenta).
- **Salva**: dice "Yo soy Salvador…".
- Todo lo demás es **idéntico** entre los tres. Si agregas un párrafo, agrégalo
  **igual en los tres** (salvo que mencione el nombre del narrador).

Convención fonética obligatoria (Inworld lee mal el chileno):
- Escribir **`hueá`** y **`hueón`** (NO `güeá`/`gueón`).
- Siglas conflictivas en palabras: "Servicio de Impuestos Internos", "Comisión
  para el Mercado Financiero", etc. (no `SII`/`CMF` sueltas dentro del relato).

---

## 2. Pasos para agregar UN HITO (caso normal)

1. **Línea de tiempo**
   - Agrega el evento en `cronologia.md` siguiendo el formato existente.
   - Regenera el HTML:
     ```bash
     cd "F:/roberttson/Caso Hermosilla"
     python gen_html.py --migrate     # MD -> JSONL -> reconstruye el array
     ```
   - (Esto NO toca el reproductor ni el resto del HTML, solo el array `EVENTOS`.)

2. **Relato (solo si el hito merece estar en el pódcast)**
   - Decide en qué **arista/tema** encaja y edita **un solo párrafo** (o agrega
     uno corto) en los **3 guiones**. No reescribas párrafos vecinos.
   - Respeta `hueá`/`hueón` y las diferencias de nombre por voz.

3. **Regenerar audios incrementalmente** (clave del ahorro)
   - Ejecutar **desde la carpeta de streamatron** (para que cargue la API key):
     ```bash
     cd "F:/roberttson/streamatron"
     venv/Scripts/python.exe "F:/roberttson/Caso Hermosilla/actualizar_audios.py"
     ```
   - El script informa por voz: `NUEVOS(API)=N  reutilizados=M`. Con un hito
     bien acotado, **N debería ser 1–3 por voz** (no 79).
   - Reconstruye `audio_<voz>/<voz>_completo.wav` y exporta `audio/<voz>.mp3`.

4. **Subir a GitHub**
   ```bash
   cd "F:/roberttson/Caso Hermosilla"
   git add cronologia.md cronologia.jsonl cronologia.html \
           audio/kevin.mp3 audio/relator.mp3 audio/salva.mp3 \
           guion_tts_caso_hermosilla_v2.md guion_tts_relator.md guion_tts_salva.md
   git commit -m "Agrega hito <fecha> y actualiza audios del pódcast"
   git push origin main
   ```
   > GitHub Pages publica en ~1–2 min. Avisar al usuario que recargue con Ctrl+F5.

---

## 3. Pasos para agregar UNA NUEVA ARISTA

Igual que un hito, **más** un ajuste en el ensamblado:

- En `actualizar_audios.py`, agrega a la lista **`TRIGGERS_TEMA`** el **inicio
  exacto** del párrafo que abre la nueva arista (p. ej. `"Octava arista"`).
  Eso inserta el **1 segundo de silencio** antes de ese bloque, como las demás.
- Mantén el patrón narrativo: una frase de transición que nombre la arista, su
  explicación pedagógica si hay un término jurídico nuevo, y de vuelta al relato.

---

## 4. Si Inworld devuelve 402 (sin crédito)

- El script se detiene e indica el 402. **Lo ya sintetizado queda en caché.**
- El usuario recarga crédito en Inworld y se **reejecuta el mismo comando**:
  como la caché está poblada, solo reintenta los fragmentos que faltaban.

---

## 5. Verificación rápida antes de subir

- `actualizar_audios.py` imprime la duración de cada voz y el tamaño del MP3.
- Confirmar que `git status` muestra los 3 `audio/*.mp3` modificados (si tocaste
  el relato) y `cronologia.html` (si tocaste la timeline).
- Las carpetas `audio_*/` y los `*.wav` NO deben aparecer en `git status`
  (están en `.gitignore`).

---

## 6. Mantenimiento de la caché (opcional)

- Para **migrar/poblar** la caché desde fragmentos ya existentes sin gastar API:
  ```bash
  venv/Scripts/python.exe "F:/roberttson/Caso Hermosilla/actualizar_audios.py" --seed-only
  ```
- Con el tiempo, la caché acumula audios de versiones viejas de párrafos editados.
  No estorban (se ignoran), pero se pueden limpiar borrando los `.wav` de
  `audio_*/cache/` cuyo hash ya no esté en `audio_*/manifest.json`.

---

### Resumen de una línea
**Edita el mínimo de párrafos → corre `actualizar_audios.py` (solo paga lo nuevo)
→ `git add audio/*.mp3 cronologia.html …` → commit → push.**
