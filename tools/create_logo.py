#!/usr/bin/env python3
"""
Generador de Logo para ANTARCTIC
Crea un logo PNG profesional con efectos y diseño moderno
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_antarctic_logo():
    # Dimensiones del logo
    width = 500
    height = 150

    # Crear imagen con transparencia
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Colores
    red = (204, 0, 0, 255)  # #CC0000
    dark_red = (153, 0, 0, 255)  # #990000
    gray = (102, 102, 102, 255)  # #666666
    light_gray = (153, 153, 153, 255)  # #999999

    # Intentar usar una fuente system (fallback a default)
    try:
        # Intentar fuentes comunes en Windows
        font_paths = [
            "C:/Windows/Fonts/consola.ttf",  # Consolas
            "C:/Windows/Fonts/arial.ttf",     # Arial
            "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
        ]

        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 48)
                subtitle_font = ImageFont.truetype(font_path, 14)
                break

        if title_font is None:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Texto principal
    main_text = "A N T A R C T I C"

    # Calcular posición centrada
    bbox = draw.textbbox((0, 0), main_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = 30

    # Efecto de sombra (múltiples capas para profundidad)
    shadow_offset = 3
    for i in range(3, 0, -1):
        shadow_color = (0, 0, 0, 50 * i)
        draw.text((x + shadow_offset * i, y + shadow_offset * i),
                 main_text, font=title_font, fill=shadow_color)

    # Texto principal en rojo
    draw.text((x, y), main_text, font=title_font, fill=red)

    # Línea decorativa superior
    line_y = y - 10
    line_start_x = 50
    line_end_x = width - 50

    # Línea con degradado (simulado con múltiples líneas)
    for i in range(3):
        alpha = 255 - (i * 60)
        draw.line([(line_start_x, line_y - i), (line_end_x, line_y - i)],
                 fill=(204, 0, 0, alpha), width=1)

    # Subtítulo
    subtitle = "━━━━━━━━━━ ULTRA CLICKER ━━━━━━━━━━"
    bbox_sub = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox_sub[2] - bbox_sub[0]
    sub_x = (width - subtitle_width) // 2
    sub_y = y + text_height + 15

    # Subtítulo en gris
    draw.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=gray)

    # Línea decorativa inferior
    line_bottom_y = sub_y + 25
    for i in range(2):
        alpha = 255 - (i * 80)
        draw.line([(line_start_x, line_bottom_y + i), (line_end_x, line_bottom_y + i)],
                 fill=(102, 102, 102, alpha), width=1)

    # Añadir detalles decorativos (esquinas)
    corner_size = 15
    corner_color = (204, 0, 0, 150)

    # Esquina superior izquierda
    draw.line([(20, 20), (20 + corner_size, 20)], fill=corner_color, width=2)
    draw.line([(20, 20), (20, 20 + corner_size)], fill=corner_color, width=2)

    # Esquina superior derecha
    draw.line([(width - 20 - corner_size, 20), (width - 20, 20)], fill=corner_color, width=2)
    draw.line([(width - 20, 20), (width - 20, 20 + corner_size)], fill=corner_color, width=2)

    # Esquina inferior izquierda
    draw.line([(20, height - 20), (20 + corner_size, height - 20)], fill=corner_color, width=2)
    draw.line([(20, height - 20 - corner_size), (20, height - 20)], fill=corner_color, width=2)

    # Esquina inferior derecha
    draw.line([(width - 20 - corner_size, height - 20), (width - 20, height - 20)], fill=corner_color, width=2)
    draw.line([(width - 20, height - 20 - corner_size), (width - 20, height - 20)], fill=corner_color, width=2)

    # Guardar logo
    img.save('logo.png', 'PNG')
    print("[OK] Logo creado exitosamente: logo.png")
    print(f"  Dimensiones: {width}x{height}")
    print(f"  Formato: PNG con transparencia")
    return img


def create_compact_logo():
    """Crea una versión compacta del logo para la ventana de activación"""
    width = 400
    height = 100

    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    red = (204, 0, 0, 255)
    gray = (102, 102, 102, 255)

    try:
        font_paths = [
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]

        title_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                title_font = ImageFont.truetype(font_path, 42)
                subtitle_font = ImageFont.truetype(font_path, 12)
                break

        if title_font is None:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    main_text = "A N T A R C T I C"

    bbox = draw.textbbox((0, 0), main_text, font=title_font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = 15

    # Sombra
    shadow_offset = 2
    for i in range(2, 0, -1):
        shadow_color = (0, 0, 0, 60 * i)
        draw.text((x + shadow_offset * i, y + shadow_offset * i),
                 main_text, font=title_font, fill=shadow_color)

    draw.text((x, y), main_text, font=title_font, fill=red)

    # Subtítulo
    subtitle = "━━━━━━━ LICENSE ACTIVATION ━━━━━━━"
    bbox_sub = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = bbox_sub[2] - bbox_sub[0]
    sub_x = (width - subtitle_width) // 2
    sub_y = y + text_height + 8

    draw.text((sub_x, sub_y), subtitle, font=subtitle_font, fill=gray)

    img.save('logo_compact.png', 'PNG')
    print("[OK] Logo compacto creado: logo_compact.png")
    print(f"  Dimensiones: {width}x{height}")
    return img


if __name__ == "__main__":
    print("\n" + "="*50)
    print("ANTARCTIC - GENERADOR DE LOGOS")
    print("="*50 + "\n")

    print("Generando logos...")
    print()

    # Crear logo principal
    create_antarctic_logo()

    # Crear logo compacto
    create_compact_logo()

    print()
    print("="*50)
    print("COMPLETADO")
    print("="*50)
    print()
    print("Archivos generados:")
    print("  - logo.png         -> Para ventana principal")
    print("  - logo_compact.png -> Para ventana de activacion")
    print()
    print("Los logos estan listos para usar en Antarctic!")
    print()
