# QA — Reubicación de la diapositiva de equipo

## Resultado

El HTML y el PDF contienen 19 diapositivas. «Quiénes impulsan AI PlayGrounds» pasó de la posición 12 a la 18; el cierre permanece en la 19. Las anteriores 13–18 ocupan ahora las posiciones 12–17. No se añadieron ni eliminaron diapositivas.

## Validaciones ejecutadas

- Se comparó el texto de las 19 diapositivas con el commit anterior `cb8387a`, siguiendo la nueva correspondencia y excluyendo únicamente el contador: todas coinciden.
- Se compararon las capturas a 1920 × 1080 con las del mismo commit. En las diapositivas reubicadas, incluida la nueva 18, los píxeles fuera de la zona del contador son idénticos. La slide 19 es idéntica. Las slides 01–11 son idénticas salvo nueve píxeles en una línea de la slide 08, diferencia mínima de rasterización sin cambio de contenido ni diseño. Detalle y correspondencias: `qa-reorder.json`; se puede repetir con `python deck/compare_reorder.py cb8387a`.
- Numeración consecutiva 01 / 19 a 19 / 19 e indicadores de modalidad en slides 13–17 comprobados. La participación comunitaria conserva sus dos bloques.
- Sin texto detectado fuera del lienzo a 1920 × 1080, 1366 × 768 y 1280 × 720. La prueba de intersecciones no detectó superposiciones entre textos distintos en las composiciones editables.
- Navegación por teclado, límites, pantalla completa en Chromium, movimiento reducido y presencia del contenido sin JavaScript comprobados. No se observaron errores JavaScript ni solicitudes HTTP externas.
- PDF de 19 páginas con texto extraíble; títulos y párrafos sin formato interno de las composiciones editables cotejados con su exportación. Resultados: `qa-results.json`.
- `qa-comparison.json` contiene la correspondencia actualizada con el PDF de referencia y compara las capturas con el PDF final.

## Limitaciones

La prueba automática de superposiciones cubre las composiciones HTML editables, no todos los trazados SVG. El gesto táctil no se ha probado en un dispositivo físico. El texto recuperado del PDF permanece seleccionable y editable, pero cambios futuros de longitud pueden requerir ajustes de posición.
