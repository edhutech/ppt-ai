# QA — AI PlayGrounds, 22 diapositivas

## Resultado y revisión visual

Se generaron el HTML autocontenido, el PDF y las capturas 01–22. Se revisaron las 22 composiciones a 1920 × 1080, con inspección ampliada de las nuevas slides 09, 11 y 20 y de las slides 04, 17 y 18. Las nuevas páginas usan, respectivamente, una tipología modular de cuatro resultados, una vitrina de productos ilustrativos y dos columnas editoriales para beneficios actuales y futuros.

Se retiró la repetición de +30 de la slide 04, conservando la cifra en la 05. Se actualizaron los pies de sección y las etiquetas profesionales de las slides 17–18. La asociación se identifica como no constituida; no se anuncian descuentos, cuentas o reconocimientos externos garantizados.

## Pruebas ejecutadas

- Exactamente 22 diapositivas y 22 páginas PDF, numeración 01 / 22 a 22 / 22 y orden editorial comprobados. Se verificaron las cuatro categorías en la 09, la vitrina en la 11, los seis beneficios en la 20, el equipo en la 21 y el cierre en la 22.
- Indicadores de modalidad comprobados en las slides 15–19; la contribución comunitaria conserva dos bloques. No se recuperó el antiguo flujo de AI Labs.
- Navegación por flechas, espacio, Page Up/Down, Home/End y límites comprobados. Pantalla completa activada y desactivada en Chromium sin interfaz. Se comprobó la presencia del contenido con JavaScript desactivado y con movimiento reducido.
- En 1920 × 1080, 1366 × 768 y 1280 × 720 no se detectaron textos fuera del lienzo. No se detectaron superposiciones entre textos distintos en las composiciones HTML. Sin errores JavaScript ni solicitudes HTTP externas observadas.
- El PDF contiene texto seleccionable y sus títulos y párrafos sin formato interno de las composiciones HTML se cotejaron con la exportación. Resultados automáticos en `qa-results.json`.
- `qa-comparison.json` compara capturas y PDF final y documenta la correspondencia con las páginas recuperadas del PDF de referencia. `qa-reorder.json` compara las 19 diapositivas conservadas con el commit `11edd4c`, excluyendo las áreas de numeración, pies y los ajustes editoriales indicados. Fuera de esas áreas, las capturas son idénticas salvo pequeñas variaciones de rasterización en las slides 08 y 12; sus composiciones se revisaron visualmente.

## Alcance y limitaciones

La detección automática de superposiciones cubre los textos HTML de las composiciones editables, no todos los trazados SVG. La comparación de píxeles no sustituye una revisión en un proyector físico; no se ha probado el gesto táctil en un dispositivo físico. Las fuentes de beneficios tecnológicos no se verificaron externamente porque no se afirma disponibilidad, proveedor, precio ni porcentaje concretos.

La construcción y las pruebas son reproducibles con los comandos de `README.md`; la comparación visual anterior se ejecutó con `python deck/compare_reorder.py 11edd4c`.
