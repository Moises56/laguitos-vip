"""
Script para convertir el logo SVG a ICO para el ejecutable de Windows.
Como Cairo no está disponible fácilmente en Windows, vamos a crear
un PNG simple con Pillow y luego convertirlo a ICO.
"""
from pathlib import Path
from PIL import Image, ImageDraw

def create_logo_png():
    """Crea un logo PNG simple con Pillow - perfectamente centrado"""
    # Tamaño del logo
    size = 256
    center = size // 2  # 128
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Colores del gradiente (aproximados)
    purple = (102, 126, 234)  # #667eea
    pink = (245, 87, 108)     # #f5576c
    
    # Fondo circular suave - perfectamente centrado
    margin = 10
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(*purple, 25))
    
    # Rectángulo principal (pantalla/video) - centrado
    rect_width = 120
    rect_height = 80
    rect_x1 = center - rect_width // 2  # 68
    rect_y1 = 50
    rect_x2 = center + rect_width // 2  # 188
    rect_y2 = rect_y1 + rect_height     # 130
    
    draw.rounded_rectangle(
        [rect_x1, rect_y1, rect_x2, rect_y2],
        radius=8,
        fill=purple,
        outline=(255, 255, 255),
        width=3
    )
    
    # Triángulo de play - centrado en el rectángulo
    rect_center_y = rect_y1 + rect_height // 2  # 90
    play_width = 30
    play_height = 35
    play_x_start = center - 15
    
    play_points = [
        (play_x_start, rect_center_y - play_height // 2),      # Top
        (play_x_start, rect_center_y + play_height // 2),      # Bottom
        (play_x_start + play_width, rect_center_y)             # Right point
    ]
    draw.polygon(play_points, fill=(255, 255, 255, 230))
    
    # Flecha de descarga - línea vertical centrada
    arrow_y_start = rect_y2 + 15  # 145
    arrow_y_end = arrow_y_start + 35  # 180
    arrow_width = 8
    
    draw.rounded_rectangle(
        [center - arrow_width // 2, arrow_y_start, center + arrow_width // 2, arrow_y_end],
        radius=2,
        fill=pink
    )
    
    # Flecha de descarga - punta centrada
    arrow_tip_size = 15
    arrow_points = [
        (center - arrow_tip_size, arrow_y_end),      # Left
        (center, arrow_y_end + arrow_tip_size),      # Bottom point
        (center + arrow_tip_size, arrow_y_end)       # Right
    ]
    draw.polygon(arrow_points, fill=pink)
    
    # Puntos decorativos - perfectamente simétricos
    dot_radius = 4
    dot_margin = 30
    dots = [
        (dot_margin, dot_margin, purple),                    # Top-left
        (size - dot_margin, dot_margin, purple),            # Top-right
        (dot_margin, size - dot_margin, pink),              # Bottom-left
        (size - dot_margin, size - dot_margin, pink)        # Bottom-right
    ]
    for x, y, color in dots:
        draw.ellipse([x-dot_radius, y-dot_radius, x+dot_radius, y+dot_radius], 
                     fill=(*color, 153))
    
    return img

try:
    # Rutas
    logo_dir = Path(__file__).parent / "logo"
    png_file = logo_dir / "logoDownloader.png"
    ico_file = logo_dir / "logoDownloader.ico"
    
    print("🎨 Creando logo para el ejecutable...")
    
    # Crear directorio si no existe
    logo_dir.mkdir(exist_ok=True)
    
    # Crear PNG
    print("  �️  Generando PNG (256x256)...")
    img = create_logo_png()
    img.save(png_file, 'PNG')
    
    # Crear ICO con múltiples tamaños
    print("  � PNG → ICO (múltiples tamaños)...")
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save(
        ico_file,
        format='ICO',
        sizes=icon_sizes
    )
    
    print(f"\n✅ Logo convertido exitosamente!")
    print(f"   📁 ICO: {ico_file}")
    print(f"   📁 PNG: {png_file}")
    
except Exception as e:
    print(f"❌ Error al convertir logo: {e}")
