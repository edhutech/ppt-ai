# Auditoría inicial de la referencia vigente

Auditoría inicial de la fuente. El resultado y las validaciones posteriores están documentados en `output/qa.md`; este documento no certifica el deck antiguo.

## Fuente

`reference/AI_PlayGrounds_deck.pdf`: 16 páginas, 1152 × 648 pt (16:9), PDF 1.4 generado con Chromium/Skia. El texto es extraíble. Fuentes incrustadas como subconjuntos: Geist Mono Regular/Medium, Space Grotesk Medium/SemiBold e Inter Tight Regular.

Se renderizaron las 16 páginas con Poppler a 960 × 540 para inspección; las imágenes y el texto extraído se encuentran temporalmente en `/tmp/opencode/aipg-reference/` y `/tmp/opencode/aipg-reference.txt`, respectivamente. Estos archivos temporales no son entregables finales.

## Estructura y composición observadas

| Página | Contenido | Fondo y disposición |
| --- | --- | --- |
| 01 | Portada institucional | Negro; logotipo y texto a la izquierda, campo modular a la derecha. |
| 02 | Recorrido | Claro cálido; agenda 2 × 2. El cuarto punto debe cambiar a «Cómo participamos». |
| 03 | Quiénes somos | Negro; declaración a la izquierda, campo modular a la derecha. |
| 04 | Comunidad y trayectoria | Claro; relato y +30 a la izquierda, lista de actividades a la derecha. |
| 05 | Profundidad técnica | Negro; relato a la izquierda y cita enmarcada a la derecha. |
| 06 | Tres principios | Claro; tres columnas con símbolos y separadores. |
| 07 | Cuatro verticales | Claro; retícula 2 × 2 con símbolos cromáticos. |
| 08 | Actividades de las verticales | Claro; etiquetas laterales, retícula central y conectores bidireccionales. |
| 09 | Community | Claro; relato a la izquierda, red geométrica a la derecha. |
| 10 | AI Labs | Negro; secuencia horizontal de cinco etapas. |
| 11 | AI Academy | Claro contrastado; explicación y antecedente separados por una línea vertical. |
| 12 | hack@latam | Negro; datos del evento y tracks. |
| 13 | Más eventos | Negro; dos columnas con datos de IA Hackathon y The Real AI. |
| 14 | Equipo | Claro; tres fundadores y retícula Dream Team. Corregir «Edhú Nuñes» a «Edhú Núñez». |
| 15 | Cómo participar | Claro; tres columnas. Se reemplazará por cinco diapositivas aprobadas. |
| 16 | Cierre | Negro; marca, título y texto a la izquierda. Se trasladará a la posición 20. |

Las páginas usan negro, blanco cálido y acentos Halo, menta y lima; se observan corchetes, líneas finas, cuadros modulares, conectores y un pie de sección con una línea de progreso. Las cifras, nombres y fechas deben contrastarse directamente con el texto extraído del PDF al reconstruir.

## Infraestructura anterior

- `tmp/build_deck.py` interpreta `deck/deck-spec.md`, exige 24 diapositivas y genera `output/deck.html`. Contiene componentes geométricos, CSS escalable, navegación, modo de movimiento reducido y fuentes incrustadas. Es material reutilizable, no la fuente editorial del PDF actualizado.
- `tmp/qa_deck.py` también exige 24 diapositivas y comprueba navegación, dimensiones, copy, carga local de fuentes y capturas. Depende de Playwright y de `/tmp/opencode/aipg-input-hashes.json`, por lo que no es reproducible tal como está en este entorno.
- El storyboard y `output/` representan el deck histórico; no deben considerarse la reconstrucción vigente. Las capturas 21–24 son antiguas.
- El PDF de referencia es un archivo no seguido por Git en el momento de la auditoría. No se ha modificado ni incorporado al repositorio.

## Resultado posterior

La reconstrucción inicial fue ampliada posteriormente; el generador vigente es `deck/build.py` y la especificación actual de 22 diapositivas está en `deck/deck-spec.md`. Las fuentes anteriores se han archivado en `archive/legacy-20/`, `archive/legacy-24/` y el historial Git.
