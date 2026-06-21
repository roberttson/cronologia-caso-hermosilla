# Podcast — Caso Hermosilla
### Guion narrativo para TTS · Voz: **Kevin** (narrador único)

> Construido a partir de `cronologia.md` y de los reportajes de CIPER Chile (citas verbatim verificadas).
> Las líneas entre corchetes `[...]` y los títulos `##` / `—` son **indicaciones para el humano**: NO deben leerse en el TTS.
> El texto de narración va en prosa limpia, pensado para locución.

---

# PARTE 1 — Propuestas de estructura

## A. Arquitectura de la serie (recomendada)

El caso es demasiado grande para un solo audio: tiene **7 aristas**, más de 35 imputados y cinco años de hechos. La forma más digerible para un oyente es una **serie**, no un monólogo único. Propuesta:

| Ep. | Título tentativo | Qué cubre | Aristas |
|---|---|---|---|
| **1** | *«Aquí estamos haciendo una güeá que es delito»* — El audio que remeció a Chile | **(ESTE GUION)** Bienvenida + el caso a grandes rasgos + el problema de las aristas | panorama |
| 2 | *La máquina de facturas* | El fraude de origen: los Sauer, Factop, STF Capital, las ~10.000 facturas falsas, LarrainVial | `factop` |
| 3 | *La coima* | El núcleo: la reunión grabada, el plan de pago al SII y la CMF, prisión de Hermosilla y Villalobos | `audio-sii` |
| 4 | *El favor inmobiliario* | Tráfico de influencias: Chadwick, Ward, el Minvu y la aprobación exprés de Parque Capital | `parque-capital` |
| 5 | *La caja de Pandora* | La red sobre el Poder Judicial: Vivanco, Sabaj, Ulloa, Muñoz (CS), Guerra y las 5 destituciones | `poder-judicial` |
| 6 | *El policía que filtraba* | El director de la PDI Sergio Muñoz y los secretos de investigación | `pdi` |
| 7 | *La muñeca bielorrusa* | Coimas a una suprema: Belaz-Movitec, Codelco, los conservadores, Vivanco presa | `bielorrusa` |
| 8 | *Los hilos del poder* | Penta, Zaliasnik, Chadwick + el presente: cierre de investigación y juicio oral | `politico-diplomatico` |

> Alternativa más corta (si el TTS/producción es acotada): **3 episodios** — (1) Origen y audio [factop + audio-sii], (2) La red judicial [poder-judicial + pdi + bielorrusa], (3) La trama política [parque-capital + politico-diplomatico].

## B. Plantilla fija por episodio (para que todos «suenen» iguales)

1. **Cold open / gancho (30–45 s):** una cita potente y cruda, sin contexto, para enganchar.
2. **Bienvenida de Kevin (20 s):** identidad del podcast + promesa del episodio.
3. **Los protagonistas (1–2 min):** ¿quién es quién? en lenguaje simple.
4. **Desarrollo cronológico (cuerpo):** los hechos como relato, no como lista.
5. **Pausa pedagógica (recurrente):** cada vez que aparece un término jurídico, Kevin frena y lo explica con un ejemplo cotidiano. *(Marca: `[PAUSA PEDAGÓGICA]`)*
6. **Cierre + gancho al próximo episodio (45 s).**

## C. Tono de Kevin

Cercano, curioso, indignado a ratos pero **riguroso**. Habla de "tú" al oyente, hace preguntas retóricas, y siempre que usa una palabra de abogado la traduce. Nunca afirma culpabilidad: usa "según la Fiscalía", "los chats revelan", "está acusado de" — porque hay imputados, no condenados (salvo los que ya tienen sentencia, que se señalan).

## D. Convención fonética para TTS (¡aplicar en TODOS los episodios!)

Los motores de voz AI tropiezan con el español chileno coloquial. Regla: **se escribe como suena**, aunque la ortografía "correcta" sea otra. La cita sigue siendo fiel al audio; solo cambia la grafía para que la voz no la destroce.

| Original (no usar tal cual) | Escribir así en el guion | Por qué |
|---|---|---|
| hueá | **güeá** | el TTS no liga la "h" muda + diptongo |
| hueón | **gueón** | ídem |
| huevón / huevones | **güevón / güevones** | misma raíz |
| ¿cachái? | **¿cachái?** → mejor evitar; usar "¿ves?" / "¿entiendes?" | jerga ininteligible para TTS |
| po (muletilla) | eliminar | el TTS la lee como palabra suelta |
| al tiro | "de inmediato" / "altiro" pegado | separado suena raro |

**Otros tropiezos frecuentes y cómo prevenirlos:**
- **Siglas:** escríbelas separadas por puntos o en fonética entre paréntesis la primera vez. `SII` → riesgo de leerse "sí"; preferir **"el Servicio de Impuestos Internos, el ese-i-i"**. `CMF` → "ce-eme-efe". `PDI` → "pe-de-i". `UF` → "u-efe". `CDE`, `DDU`, `USS`: deletrear.
- **Números:** ya van escritos con palabras (ej. "setecientas setenta y siete mil") — mantener así, el TTS lee mejor texto que cifras.
- **`MP3`** → escribir "eme-pe-tres" si la voz lo mastica.
- **Garabatos fuertes:** si tu audiencia o plataforma los quiere suavizados, esta es la capa donde se censuran (ej. *gü\*á*), sin tocar el resto del guion.

---

# PARTE 2 — GUION EPISODIO 1

[Indicación TTS: lo que sigue es lo único que se lee en voz alta. Tono inicial: bajo, íntimo, casi en secreto.]

---

## [BLOQUE 0 — COLD OPEN]

«Porque aquí estamos haciendo una güeá que es delito. Esta güeá es delito… y es la única manera de hacerlo.»

[PAUSA 2 s]

Esa frase la dijo uno de los abogados más poderosos de Chile. Se llama Luis Hermosilla. La dijo en una oficina, en una reunión privada, sentado frente a un empresario y a otra abogada… sin saber que alguien estaba grabando.

Y cuando ese audio salió a la luz, no cayó solamente un abogado. Empezó a tambalear un pedazo entero del Estado de Chile: jueces de la Corte Suprema, fiscales, el director de la Policía de Investigaciones, exministros, un embajador…

¿Cómo es posible que una sola grabación de cien minutos haya hecho temblar a tres poderes del Estado? Quédate conmigo, porque esta historia recién empieza.

[PAUSA 2 s. Sube música de cabecera, luego baja.]

---

## [BLOQUE 1 — BIENVENIDA]

¡Hola, hola! Te doy la bienvenida. Yo soy Kevin, y este es el primer episodio de una serie en la que vamos a desarmar, pieza por pieza, el caso de corrupción más grande que ha vivido Chile en décadas. Lo vas a escuchar con tres nombres distintos: «Caso Audios», «Caso Factop» o, simplemente, «Caso Hermosilla». Son el mismo monstruo visto desde tres ángulos.

Te propongo un trato. Yo no voy a dar por hecho que tú sabes de leyes. Cada vez que aparezca una palabra de abogado —y van a aparecer hartas: cohecho, tráfico de influencias, prevaricación, lavado de activos— yo voy a frenar, te la voy a explicar con un ejemplo de la vida real, y seguimos. ¿Te parece? Así que no te asustes con los términos. Para eso estoy yo aquí.

Hoy, en este primer episodio, no vamos a entrar todavía al detalle de cada arista. Hoy quiero que te lleves el mapa completo en la cabeza: qué pasó, por qué importa, y por qué este caso, en vez de cerrarse, no para de crecer.

Vamos.

---

## [BLOQUE 2 — EL CASO A GRANDES RASGOS]

Empecemos por el principio. ¿Quién es Luis Hermosilla?

Hermosilla no era un abogado cualquiera. Era *el* abogado. El penalista de cabecera de la elite chilena, especialmente de la centroderecha. Cuando un poderoso tenía un problema serio con la justicia, lo llamaba a él. Tenía contactos en todas partes: en los tribunales, en las fiscalías, en la policía, en los gobiernos. Y esos contactos, como vamos a ver, no eran solo para tomar café.

Ahora, la chispa que prende todo el incendio no fue Hermosilla. Fue un fraude financiero. Te lo resumo simple.

Existían dos empresas, controladas por los hermanos Daniel y Ariel Sauer: una corredora de bolsa llamada **STF Capital** y una empresa de *factoring* llamada **Factop**.

[PAUSA PEDAGÓGICA] ¿Qué es el *factoring*? Imagínate que tú tienes un negocio y le vendes mercadería a un cliente que te va a pagar en noventa días. Pero tú necesitas la plata *ahora*. Entonces vas a una empresa de factoring, le entregas esa factura, y ella te adelanta el dinero a cambio de una comisión. Es un negocio legítimo… cuando las facturas son de verdad. ¿Y cuál era el problema acá? Que muchas de esas facturas eran **falsas**. Inventadas. Cerca de **diez mil facturas falsas**, por un perjuicio de más de doce mil millones de pesos. Una máquina de fabricar deuda de mentira para conseguir plata de verdad.

Cuando el regulador financiero —la CMF, la Comisión para el Mercado Financiero, que es como el árbitro que vigila a bancos y corredoras— empezó a meter las narices y suspendió a estas empresas en marzo de 2023, los involucrados entraron en pánico. ¿Y a quién llaman cuando están en pánico? A Luis Hermosilla.

Y acá llegamos a la escena del crimen. Mediados de 2023. Una oficina del Grupo Patio, en Vitacura. Se reúnen tres personas: Luis Hermosilla, la abogada María Leonarda Villalobos, y el empresario Daniel Sauer. Hablan durante casi dos horas sobre cómo frenar la investigación. Y en esa conversación, Hermosilla propone algo muy concreto: pagarles a funcionarios del Servicio de Impuestos Internos y de la CMF para conseguir información y enfriar el caso.

Escucha sus propias palabras, porque esto es textual de la grabación:

«Necesitamos una caja para gastos. Una caja negra… porque parte importante de esta güeá se arregla con plata, que se pasa así, en un sobre.»

Y más adelante:

«Hay un gueón de la CMF al que le debemos plata también.»

Y la frase que lo resume todo, la que tú ya escuchaste al principio:

«Aquí estamos haciendo una güeá que es delito.»

Él *sabía*. Lo dice él mismo. No es interpretación de un fiscal, no es la teoría de un periodista: es el propio Hermosilla reconociendo, en voz alta, que lo que estaban planeando era un delito.

[PAUSA PEDAGÓGICA] Y ese delito tiene nombre: se llama **cohecho**. En lenguaje de la calle, cohecho es coima, es soborno. Es ofrecerle o pagarle dinero a un funcionario público para que haga —o para que *no* haga— algo propio de su cargo. Ejemplo simple: si tú le pasas plata a un inspector para que no te curse un parte, eso es cohecho. Los dos cometen delito: el que paga y el que recibe. Bueno, multiplica eso por funcionarios del SII y de la CMF, y tienes el corazón de este caso.

¿Y cómo se supo todo esto? Acá entra un personaje clave: **Rodrigo Topelberg**, socio de los Sauer, que estaba enemistado con ellos. El 13 de noviembre de 2023, un archivo de audio MP3 de ciento cinco minutos, llamado «Némesis», le llega al Ministerio Público, a la CMF y a un medio de prensa: **CIPER Chile**. Al día siguiente, el 14 de noviembre, CIPER lo publica. Y Chile amanece distinto.

---

## [BLOQUE 3 — POR QUÉ CIPER ES EL HILO CONDUCTOR]

Acá quiero detenerme un segundo, porque a lo largo de toda esta serie vas a escucharme repetir un nombre: **CIPER**, el Centro de Investigación Periodística.

¿Por qué? Porque buena parte de lo que sabemos de este caso no lo destapó un tribunal: lo destapó el periodismo de investigación. CIPER fue quien publicó el audio original. Y después, reportaje tras reportaje, fue revelando los chats, las filtraciones, los favores entre jueces. Cada vez que parecía que el caso se iba a calmar, aparecía un nuevo reportaje de CIPER —o de The Clinic, o de Reportea— y se abría una puerta nueva.

Por eso, en este podcast, las citas y los hechos se apoyan una y otra vez en ese trabajo. No es relleno: es la columna vertebral de la historia.

---

## [BLOQUE 4 — EL PROBLEMA DE LAS ARISTAS]

Y ahora sí, llegamos al punto más importante de este episodio. Al problema que hace que este caso sea tan difícil de seguir… y tan difícil de cerrar.

Cuando la Fiscalía allanó la oficina de Hermosilla, le incautó el teléfono. Un iPhone. Y de ese teléfono extrajeron algo monstruoso: más de **setecientas setenta y siete mil páginas** de conversaciones, fotos, audios y archivos.

Piénsalo. Setecientas setenta y siete mil páginas. Ahí estaba todo. Años de favores, de gestiones, de conversaciones con gente del poder. Ese teléfono fue como abrir una caja de Pandora.

[PAUSA PEDAGÓGICA] Y acá aparece la palabra que le da título a este episodio y que vas a escuchar todo el rato: **arista**. ¿Qué es una arista? En lenguaje judicial, una arista es una *ramificación* de la investigación. Imagínate el caso como un árbol: el tronco es el audio, el soborno al SII. Pero de ese tronco empiezan a salir ramas, y de cada rama salen más ramas. Cada una es una historia distinta, con personas distintas, delitos distintos… pero todas nacen del mismo tronco, del mismo teléfono. A cada una de esas ramas la llamamos arista.

¿Y cuántas ramas tiene este árbol? Hoy, al menos **siete**. Déjame mostrártelas rápido, como un mapa, para que sepas hacia dónde vamos en los próximos episodios:

**Una.** La arista del audio y el SII. El tronco. El plan de soborno a funcionarios públicos. Por esto, Hermosilla y Villalobos terminaron en prisión preventiva.

**Dos.** La arista Factop. El fraude original: las diez mil facturas falsas, los Sauer, la corredora LarrainVial —que recibió la multa más alta en la historia del regulador financiero chileno— y el lavado de la plata.

[PAUSA PEDAGÓGICA] Espera, ¿qué es **lavado de activos**? Es tomar dinero que viene de un delito —dinero "sucio"— y hacerlo pasar por dinero legítimo, "limpio", moviéndolo entre empresas, cuentas y negocios hasta que ya no se nota de dónde salió. Como echar la ropa sucia a la lavadora para que salga impecable. Por eso se llama "lavado".

**Tres.** La arista Parque Capital. Acá Hermosilla deja de ser solo el abogado del soborno y aparece como **operador político**: habría presionado a un ministro de Vivienda y a un seremi para que aprobaran, en tiempo récord, los permisos de un negocio inmobiliario millonario. Un trámite que normalmente demora dieciocho meses… se aprobó en dos meses y medio.

[PAUSA PEDAGÓGICA] Esto ya no es cohecho; es otro delito: **tráfico de influencias**. ¿La diferencia? En el cohecho hay plata de por medio para torcer a un funcionario. En el tráfico de influencias, lo que se usa es el *peso del contacto*, la cercanía, el "yo conozco a fulano". Es usar tu influencia sobre una autoridad para conseguir una decisión que te beneficia. Ejemplo: si un asesor del gobierno llama a un funcionario y le dice "apúrame este permiso porque es de un amigo", y el permiso se aprueba a la rápida y saltándose las reglas… eso huele a tráfico de influencias.

**Cuatro.** La arista del Poder Judicial. Y esta, te adelanto, es la más grave para las instituciones. Los chats revelaron que Hermosilla tenía una red de favores con **jueces y fiscales**. Le pedía a una ministra de la Corte Suprema que integrara cierta sala en cierto día. Coordinaba nombramientos de jueces. Recibía información reservada. El resultado: hasta hoy, **cinco** altos magistrados removidos de sus cargos. Cinco.

**Cinco.** La arista PDI. El propio director de la Policía de Investigaciones, Sergio Muñoz, le filtraba a Hermosilla secretos de investigaciones en curso.

**Seis.** La arista bielorrusa, o «muñeca bielorrusa». Esta es de novela: una exministra de la Corte Suprema acusada de recibir pagos de un consorcio chileno-bielorruso para fallar a favor de ellos en un juicio contra Codelco, el cobre de todos los chilenos.

**Y siete.** La arista político-diplomática. Los hilos que conectan todo esto con exministros, con el Caso Penta, con un embajador. La política, al fondo de la sala.

¿Te das cuenta del problema? Este no es *un* caso. Son siete casos entrelazados, con decenas de imputados, repartidos en fiscalías de distintas regiones del país. Por eso cuesta tanto seguirlo. Por eso, cada vez que crees que entendiste, aparece un nombre nuevo.

---

## [BLOQUE 5 — POR QUÉ ESTO IMPORTA / EL PRESENTE]

Y quizás te estés preguntando: Kevin, ¿y a mí qué? ¿Por qué debería importarme un pelo este enredo de abogados ricos?

Te respondo con una pregunta. ¿Tú confías en que, si mañana llegas a un tribunal, el juez que te toque va a decidir tu caso por la ley… y no por una conversación de WhatsApp con un abogado bien conectado?

De eso se trata. Este caso no es un chisme de la elite. Es la radiografía de cómo el dinero y los contactos pueden meterse adentro de las instituciones que se supone deben tratarnos a todos por igual: los tribunales, la policía, los reguladores. Cuando un juez de la Corte Suprema le pregunta a un abogado qué le conviene fallar, lo que se rompe no es la carrera de ese juez. Es la promesa de que la justicia es pareja.

[PAUSA PEDAGÓGICA] Una última palabra antes de cerrar, para que escuches las noticias con oído crítico. Vas a oír mucho "Hermosilla fue **formalizado**", "lo dejaron en **prisión preventiva**". ¿Qué significan? **Formalizar** es el momento en que la Fiscalía le comunica oficialmente a una persona, ante un juez, que está siendo investigada por un delito. Ojo: formalizar *no* es condenar. Es el pitazo inicial, no el resultado del partido. Y la **prisión preventiva** es cuando, mientras dura la investigación, mandan a la persona a la cárcel porque se la considera un peligro para la sociedad o para la investigación. Tampoco es una condena: es una medida *cautelar*, una precaución. Por eso, en este caso, vas a ver a Hermosilla entrar y salir de la cárcel varias veces, según lo que vayan decidiendo los tribunales. Sigue siendo, hasta que haya sentencia, un **imputado**: alguien acusado, no alguien condenado.

¿En qué está la historia hoy? Después de cinco años, decenas de imputados y cinco jueces caídos, la Fiscalía por fin **cerró la investigación** del núcleo del caso y presentó su acusación. ¿Las penas que pide? Hasta **veinte años de cárcel** para algunos. Para Hermosilla, catorce. Como dijo uno de los fiscales: el destino final de todo esto es, sin ninguna duda, un **juicio oral**. La etapa donde, por fin, todo se resuelve frente a un tribunal.

---

## [BLOQUE 6 — CIERRE Y GANCHO]

Así que ese es el mapa. Un audio de cien minutos. Un teléfono con setecientas setenta y siete mil páginas. Siete aristas. Y un país mirándose en el espejo, preguntándose hasta dónde llegaba la podredumbre.

En el próximo episodio vamos a volver al principio de todo: a la máquina de facturas falsas. Vamos a conocer a los Sauer, a Factop, y a entender cómo un fraude financiero terminó arrastrando a media justicia chilena. Porque antes del audio… ya había fuego.

Yo soy Kevin. Esto fue el primer episodio. Si esta historia te dejó con la mandíbula en el suelo —como nos pasó a todos— acompáñame en el siguiente. Nos escuchamos pronto. ¡Cuídate!

[PAUSA 2 s. Sube música de cierre.]

---

## [APÉNDICE — Banco de citas verbatim para próximos episodios]

> Todas verificadas contra CIPER / la cronología. Úsalas como cold opens o golpes de efecto.

- **Audio (Ep. 3):** «Necesitamos una caja negra… porque parte importante de esta güeá se arregla con plata, que se pasa así, en un sobre.» — Hermosilla.
- **Audio (Ep. 3):** «De este gueón dependemos… el que tiene la llave de esa puerta es un gueón al que le debemos, en este minuto, 10 millones de pesos.» — Hermosilla.
- **Vivanco / Poder Judicial (Ep. 5):** «¿Alguna posibilidad que integres la Sala Penal mañana?» — Hermosilla a la ministra Vivanco. Ella: «Por supuesto, si la sala me pide voy.»
- **Vivanco (Ep. 5):** «Estimado Luis, buenos días… quisiera conversar con usted acerca de mi postulación a la Corte Suprema.» — primer mensaje de Vivanco a Hermosilla.
- **Sabaj (Ep. 5):** «Sabes que tenemos pacto forever.»
- **Sabaj / Zaliasnik (Ep. 8):** «Y borramos x fa después.»
- **Parque Capital (Ep. 4):** «El énfasis del tema DDU me parece importante. Es lo que puede blindar jurídicamente la decisión.» — Hermosilla.
- **Parque Capital (Ep. 4):** «Hay que sacarlo sí o sí ese día.» — supervisores de la Seremi, según funcionarios.
- **Fiscal Palma (Ep. 5):** «Vine a hablar con Andrés [Chadwick].»
- **José Ramón Correa (Ep. 5):** un ministro descrito como «absolutamente nuestro».
- **Sergio Muñoz, PDI (Ep. 6):** «Soy un hombre honesto que cometió un error fatal que he asumido.» — al ser condenado (primera sentencia del caso).
- **Hermosilla, defensa (Ep. 4):** «No gané ni recibí 5.000 UF.»
- **Guerra (Ep. 5):** según el juez, «Guerra condicionaba sus decisiones a la postura de la UDI».
- **Vivanco, arista bielorrusa (Ep. 7):** «No soy una persona que se pueda catalogar de peligro para la sociedad.»

---

## [APÉNDICE — Glosario pedagógico (para no repetir explicaciones)]

| Término | Traducción de Kevin | Ejemplo cotidiano |
|---|---|---|
| **Arista** | Una rama de la investigación | Las ramas que salen de un mismo tronco |
| **Cohecho** | Coima, soborno | Pasarle plata a un inspector para que no te curse el parte |
| **Tráfico de influencias** | Usar el peso del contacto, no la plata | "Apúrame este permiso porque es de un amigo" |
| **Prevaricación** | Cuando un juez o fiscal falla a sabiendas contra la ley | El árbitro que cobra penal sabiendo que no lo fue |
| **Lavado de activos** | Limpiar plata sucia haciéndola pasar por legítima | Echar la ropa sucia a la lavadora |
| **Formalización** | Aviso oficial de que te investigan | El pitazo inicial, no el resultado del partido |
| **Prisión preventiva** | Cárcel mientras dura la investigación (medida cautelar) | Una precaución, no una condena |
| **Imputado** | Acusado, todavía no condenado | El sospechoso, no el culpable declarado |
| **Acusación constitucional** | Juicio político del Congreso para destituir a una autoridad | El Congreso "echando" a un alto cargo |
| **Procedimiento abreviado** | El imputado reconoce el delito a cambio de menos pena | Negociar la cuenta para no ir a juicio |
| **Revelación de secreto** | Filtrar información reservada de una investigación | El árbitro pasándole la estrategia a un equipo |

---

*Fuentes primarias: reportajes de CIPER Chile (2023–2026) y base cronológica del proyecto. Citas del audio: CIPER, 14/11/2023. Citas de chats Vivanco: CIPER, 07/09/2024.*
