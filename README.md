# AI PlayGrounds — presentación interna

La versión vigente tiene **22 diapositivas**. Abre `output/deck.html` directamente en el navegador para presentar sin conexión. `output/deck.pdf` y `output/screenshots/` permiten revisar la exportación y las capturas.

## Fuentes y construcción

- `deck/narrativa.html` y `deck/adiciones.html`: contenido y estructura de las diapositivas editables.
- `deck/narrativa.css`: estilos y diagramas de la versión vigente.
- `deck/reference/*.json`: texto editable y posiciones de las diapositivas recuperadas; los gráficos están en SVG junto a esos archivos.
- `deck/build.py`: composición y ajustes de numeración y copy; `deck/fonts.css` integra las tipografías; `deck/navigation.js` controla la presentación.
- `deck/deck-spec.md`: especificación editorial vigente. Las versiones anteriores están en `archive/`.

```sh
python deck/build.py
python -m pip install playwright pillow
python deck/render_qa.py
python deck/compare_reference.py
python deck/compare_reorder.py 11edd4c
```

El HTML se construye con la biblioteca estándar de Python. El QA requiere Chromium en `/usr/bin/chromium-browser` y Poppler (`pdfinfo`, `pdftotext`, `pdftoppm`); genera el PDF, 22 capturas y resultados JSON. El comparador necesita Pillow. El PDF de referencia y `deck/extract_reference.py` documentan la recuperación inicial: ejecutarlo requiere PyMuPDF y sobrescribe los JSON/SVG recuperados.

## Presentación

Flechas, espacio y Page Up/Down navegan; Home y End saltan a los extremos. Los botones aparecen al pasar el cursor por la esquina inferior derecha y permiten navegar y activar pantalla completa. También hay navegación táctil. La presentación usa fuentes integradas, no solicita recursos de red y no oculta contenido con animaciones.
