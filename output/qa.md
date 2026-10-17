# AI PlayGrounds — QA de la primera versión HTML

## Entregables

- `output/deck.html`: 24 slides autocontenidas; HTML, CSS, SVG, JavaScript y fuentes integradas. Sin dependencias de red durante uso.
- `output/screenshots/slide-01.png` a `slide-24.png`: 24 renders individuales, cada uno de 1920 × 1080, con la animación completada y sin controles superpuestos.
- Construcción reproducible: `tmp/build_deck.py`.
- QA automatizado y render: `tmp/qa_deck.py`; resultados detallados en `tmp/deck-qa.json`.

## Narrativa

- Exactamente 24 secciones, mismo orden, títulos, contenido y themes del storyboard.
- Copy extraído directamente de los campos `Content` de `deck/deck-spec.md`; títulos contrastados literalmente y cada línea de cuerpo, listas, notas y flujos comprobada en texto visible. Solo cambia la composición espacial y el salto de línea.
- El statement completo de slide 08 se conserva literalmente.
- Cuatro áreas con idéntica jerarquía, tamaño y tratamiento en slide 09. Relaciones abiertas y bidireccionales en slide 10, sin asignaciones 1:1.
- AI Labs presenta las cinco etapas aprobadas; Products y Research permanecen como formas emergentes, no frentes equivalentes.
- Maduración conserva las siete etapas; no se transforma en fórmula obligatoria.
- AI Academy conserva su condición de nombre provisional en slide 14; no se crea identidad gráfica independiente.
- Slide 16 diferencia Association y S.A.C.; AI Academy está contenida dentro de la operación de la S.A.C., no es una tercera entidad jurídica.
- Slide 19 separa ida/licencia y retorno/royalty. No añade porcentajes ni bases de cálculo.
- Slide 20 conserva las cautelas tributarias; slide 21 muestra dos mecanismos convergiendo en una sola experiencia sin jerarquizar estudiantes.
- Las formulaciones de posibilidad, hipótesis y validación profesional permanecen visibles. No se agregan recomendaciones jurídicas.
- El término genérico «labs» de los ejemplos de conocimiento de slide 17 se conserva literalmente porque está en el copy aprobado; el frente organizativo se denomina AI Labs.

## Sistema visual

- Dark: **01, 04, 08, 12, 16, 19, 23, 24** (8 slides).
- Light: **02, 03, 05, 06, 07, 09, 10, 11, 13, 14, 15, 17, 18, 20, 21, 22** (16 slides).
- Light basado en candidato A `#F5F3EC`; superficies secundarias `#ECEAE2` en explicación densa/diagramas; cortes claros `#E3E2DA` en slides 14 y 22.
- Space Grotesk 500/600, Inter Tight 400/500 y Geist Mono 400/500 integradas en el HTML. Sin fuentes de sistema como sustituto previsto.
- Recursos propios: módulos cuadrados, retícula 5 × 5 del símbolo, corchetes, marcos abiertos, campo de órbitas, índices y metadata monoespaciados, conectores ortogonales y flujos direccionales.
- Halo como principal. Menta limitada a resultados/progreso y flujo de retorno/acceso cuando lo autoriza el storyboard; sin uso de Lima sin propósito.
- Sin iconos externos, ilustración stock, rasterización de diagramas, tarjetas redondeadas sistemáticas, sombras, gradientes decorativos, glow o estética futurista genérica.

## Símbolo y procedencia

`assets/` no contenía vectores oficiales. El símbolo se reconstruyó como SVG conforme a la geometría del PDF (pp. 4–6): retícula de 5 × 5, 14 posiciones perimetrales ocupadas de 16, puertas superior/inferior abiertas en reposo, separación de 1/8 u y núcleo Halo fijo. Se conserva el lado de 5 u situando los módulos dentro de sus celdas; no se suman huecos por fuera. No se convierte esta reconstrucción en nuevo asset oficial.

El nombre se presenta como texto de la presentación con Space Grotesk, no como un nuevo logotipo vectorial. No se inventó un wordmark ni un logo para AI Academy. Las variantes de las puertas en campos son vocabulario gráfico, no rotación libre del símbolo maestro.

Se revisaron visualmente las páginas 4, 5, 8, 10, 13 y 15 del PDF para comprobar símbolo, versiones, movimiento, contraste, sistema gráfico y aplicación sobre blanco. No se encontró una contradicción nueva que requiera alterar las fuentes. Se mantienen las excepciones/ambigüedades ya registradas en `brand-spec.md`.

La skill remite a un preset de una skill padre `slide-design` que no está instalado. Se aplicó el sistema específico de AI PlayGrounds, que además tiene prioridad explícita en esta tarea, junto con el CSS base obligatorio de `html-slides`.

## Movimiento y navegación

- Revelaciones finitas por secuencia de lectura o diagrama; cadencia derivada de 160 ms, equivalente a dos pasos de 80 ms, con entrada de 180 ms. Sin bucles de reposo, parallax, floating ni pulsos constantes.
- Slide 08: eyebrow → título → campo → núcleo → statement.
- Slide 16: Association → S.A.C. → línea AI Academy → conexión.
- Slide 19: flujo de ida y después retorno. Slide 21: dos fuentes y después experiencia convergente.
- No se usa el zoom opcional Profundidad en la slide de statement: se resuelve la profundidad por composición y marcos abiertos.
- Navegación probada: flechas, espacio, Page Up/Down, Home/End, botones, límites 01/24 y swipe horizontal sintético.
- Controles al mover el puntero o con foco de teclado. Botón de pantalla completa disponible cuando el navegador lo permite.
- `prefers-reduced-motion` revela todo inmediatamente; Escape completa la animación en curso.
- Sin JavaScript siguen presentes las 24 slides completas, navegables mediante scroll externo entre slides; nunca hay scroll interno.

## QA visual y técnico

- Se abrieron y revisaron individualmente los 24 screenshots. Se volvió a renderizar tras las correcciones.
- Correcciones: retirada de campo que interfería con el símbolo en portada; marcos de profundidad abiertos en lugar de rectángulos cerrados; mayor respiración en las cuatro áreas; nombres AI PlayGrounds sin salto interno en titulares; campo de síntesis apartado del texto; conexiones modulares explícitas en Community.
- Render principal: Chromium, viewport exacto 1920 × 1080 y escala de dispositivo 1.
- Viewports adicionales: 2560 × 1440, 1920 × 1200, 1600 × 900, 1366 × 768, 1280 × 720, 1024 × 768 y 844 × 390. Las 24 slides se comprobaron en cada tamaño: sin desbordamiento de contenido, texto fuera del lienzo ni interferencia con el footer detectados.
- Se preserva composición 16:9 con bandas exteriores cuando cambia la proporción; no se convierte en web vertical ni se reescribe contenido para móvil.
- Cero errores JavaScript y cero solicitudes HTTP/HTTPS durante carga/navegación. Fuentes integradas verificadas como cargadas.
- Títulos, cuerpo, metadata, notas legales y pares de color revisados contra la especificación; acentos claros no usados como texto sobre light.
- Hashes SHA-256 de los 26 archivos de entrada/protegidos comprobados sin cambios: deck-spec, brand-spec, PDF, lockfile y contenido instalado de `.agents/`.

## Limitaciones restantes

- QA funcional y renders realizados en Chromium. No se ha probado de forma independiente Safari o Firefox; se requiere un navegador moderno con unidades de contenedor CSS.
- En ventanas muy pequeñas el lienzo completo se reduce proporcionalmente; la presentación está optimizada para proyección y escritorio, no lectura de cuerpo en móvil vertical.
- Símbolo reconstruido geométricamente, pendiente de sustitución si se entregan assets maestros oficiales. Las animaciones son adaptaciones narrativas derivadas, no recuperación de fotogramas originales del PDF estático.
- La validación legal, tributaria y contable externa continúa pendiente, tal como indican las slides; no se realiza en esta tarea.

No se ha generado PPTX ni una segunda variante de presentación.
