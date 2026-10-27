# QA — AI PlayGrounds, 19 diapositivas

## Resultado y revisión visual

Se generaron el HTML autocontenido, el PDF y las capturas 01–19. Se revisaron las 19 capturas a 1920 × 1080 y la composición del PDF mediante una hoja de contacto renderizada. Se verificaron numeración, pies, jerarquía, contraste, espaciados e indicadores de modalidad. La página de AI Labs no está presente; la participación comunitaria tiene dos bloques. La slide 05 distingue el agregado de eventos organizados de los tres eventos identificados como coorganizados.

En la primera pasada, una línea de AI Academy cruzaba el separador y las condiciones de la slide 18 se acercaban al pie. Se ajustaron y se repitieron la generación y las pruebas. Los resultados de las pruebas están en `qa-results.json`.

## Pruebas ejecutadas

- Exactamente 19 diapositivas, numeradas 01 / 19 a 19 / 19; PDF de 19 páginas y texto seleccionable, comprobado con `pdfinfo` y `pdftotext`.
- Los títulos y párrafos sin formato interno de las diapositivas nuevas se cotejaron con el texto exportado del PDF. Se verificó individualmente el contenido visual de los ejemplos y las condiciones.
- Sin texto detectado fuera del lienzo a 1920 × 1080, 1366 × 768 y 1280 × 720; la prueba de intersecciones no detectó superposiciones entre textos distintos en las ocho composiciones nuevas.
- Indicadores 01/03, 02/03 y 03/03 comprobados en las slides 14–18; slide 14 con dos bloques.
- Flechas, espacio, Page Up/Down, Home/End y límites: comprobados. Se entró y salió de pantalla completa en Chromium sin interfaz.
- Movimiento reducido activado durante las pruebas; no hay animaciones de entrada que oculten contenido. También se comprobó que los 19 elementos y el cierre siguen presentes sin JavaScript.
- Sin errores JavaScript ni solicitudes HTTP externas observadas. Fuentes y gráficos están integrados en el HTML.
- Se eliminaron las capturas obsoletas 20–24. El resultado es reproducible con los comandos del `README.md`.

## Comparación y limitaciones

`qa-comparison.json` compara las diapositivas recuperadas con las páginas correspondientes del PDF original y las 19 capturas con el PDF exportado, ambas rasterizadas a 960 × 540. Las diferencias incluyen antialiasing, texto HTML reposicionado, numeración y ajustes editoriales intencionales; el error medio por canal no demuestra equivalencia perceptual exacta.

Las diapositivas recuperadas utilizan líneas de texto HTML posicionadas sobre trazados SVG. El texto sigue siendo seleccionable y editable desde JSON, pero cambiar su longitud puede exigir ajustar posición o diseño. El análisis automático de superposición cubre las composiciones nuevas, no todos los trazados SVG. No se ha probado el gesto táctil en un dispositivo físico ni la lectura en proyectores concretos.
