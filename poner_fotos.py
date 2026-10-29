"""Mete las fotos reales del cliente en la demo.

Uso:  python poner_fotos.py <carpeta-con-fotos> [--portada N]

- Comprime cada foto a WebP (1200 px de ancho como mucho) en img/trabajos/.
- Sustituye la galería de ejemplo (entre <!--GALERIA--> y <!--/GALERIA-->) por las fotos reales.
- Con --portada N, la foto número N pasa a ser el fondo de la cabecera y la imagen al compartir.
No borra nada: las fotos de ejemplo se quedan en img/ por si hay que volver atrás.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

AQUI = Path(__file__).resolve().parent
EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic"}


def comprimir(origen: Path, destino: Path, ancho: int = 1200) -> None:
    img = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    if img.width > ancho:
        img = img.resize((ancho, round(img.height * ancho / img.width)), Image.LANCZOS)
    img.save(destino, "WEBP", quality=80, method=6)


def imagen_compartir(origen: Path, destino: Path) -> None:
    img = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    ImageOps.fit(img, (1200, 630), Image.LANCZOS).save(destino, "JPEG", quality=82, optimize=True)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    carpeta = Path(sys.argv[1])
    portada = int(sys.argv[sys.argv.index("--portada") + 1]) if "--portada" in sys.argv else None
    fotos = sorted(p for p in carpeta.iterdir() if p.suffix.lower() in EXT)
    if not fotos:
        sys.exit(f"No hay fotos en {carpeta}")

    salida = AQUI / "img" / "trabajos"
    salida.mkdir(parents=True, exist_ok=True)
    figuras = []
    for n, foto in enumerate(fotos, 1):
        destino = salida / f"{n:02d}.webp"
        comprimir(foto, destino)
        figuras.append(
            f'   <figure><img src="img/trabajos/{n:02d}.webp" loading="lazy" '
            f'alt="Trabajo de tapicería de Tapisseria Gama, foto {n}"></figure>'
        )
        print(f"{foto.name} -> {destino.name} ({destino.stat().st_size // 1024} KB)")

    html_path = AQUI / "index.html"
    html = html_path.read_text(encoding="utf-8")
    html, cambios = re.subn(
        r"<!--GALERIA-->.*?<!--/GALERIA-->",
        "<!--GALERIA-->\n" + "\n".join(figuras) + "\n<!--/GALERIA-->",
        html,
        flags=re.S,
    )
    if not cambios:
        sys.exit("No encuentro las marcas <!--GALERIA--> en index.html")
    html = html.replace(
        '<span class="eyebrow">Inspiración</span><h2>Galería</h2><p>Imágenes de ejemplo. Aquí irán las fotos de los trabajos de Tapisseria Gama.</p>',
        '<span class="eyebrow">Nuestro taller</span><h2>Trabajos reales</h2><p>Algunos de los muebles que han pasado por Tapisseria Gama.</p>',
    )
    html = html.replace(
        "las fotos son de banco de imágenes y se sustituyen por trabajos reales",
        "la galería ya muestra trabajos reales del taller",
    )
    if portada:
        elegida = salida / f"{portada:02d}.webp"
        html = re.sub(r"url\(img/[^)]+\) center/cover", f"url(img/trabajos/{portada:02d}.webp) center/cover", html, count=1)
        imagen_compartir(elegida, AQUI / "img" / "og.jpg")
        print(f"Portada y vista previa: foto {portada}")
    html_path.write_text(html, encoding="utf-8")
    print(f"Hecho: {len(fotos)} fotos en la galería.")


if __name__ == "__main__":
    main()
