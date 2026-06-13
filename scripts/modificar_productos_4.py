import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

DATA_DIR = Path(__file__).parent.parent / "data"
BASE_DIR = Path(__file__).parent.parent
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

# Cambiar nombre
NOMBRE_CAMBIAR = {
    "Llavero Flor de Sakura": "Aretes Flor de Sakura",
}

# Precios a asignar
PRECIOS = {
    "Rompecabezas ABC Elasmosa": 150,
    "Trofeo Guante de Oro": 250,
    "Calavera del Corazón": 150,
    "Nacimiento Iluminado": 350,
    "Popocatepetl Mexico City Volca": 250,
    "Topper Graduación 2026": 100,
    "Pirámide Maya": 350,
    "Pirámide Chichén Itzá": 200,
    "Cristo Redentor": 250,
    "Catedral de Florencia": 250,
    "Gran Muralla China": 250,
    "Pirámides de Giza": 250,
    "Partenón": 250,
    "Castillo de Chichén Itzá": 250,
    "Tarjeta Tie Fighter": 100,
    "Tarjeta Esqueleto T-Rex": 100,
    "Tarjeta AT-ST Walker": 150,
    "Charizard Voronoi": 250,
    "Globo Terráqueo Minimalista": 150,
    "Estante Goteo": 150,
    "Estantes Hongo": 150,
    "Topper Boda": 100,
    "Lámpara Calavera": 350,
    "Tarjeta DeLorean": 100,
    "Tarjeta Perros": 100,
    "Tarjeta Vida Silvestre": 100,
    "Resonancia Celestia": 150,
    "Tarjeta Motos": 100,
    "Llavero Pokeball": 50,
    "Llavero Kettlebell Gym": 60,
    "Llavero Nike": 50,
    "Llavero Casco Ciclismo": 50,
    "Trofeo Bota de Oro": 250,
    "Llavero PlayStation": 50,
}

# Productos que necesitan imagen de modelo en blanco
PRODUCTOS_IMAGEN_BLANCA = [
    "Popocatepetl Mexico City Volca",
    "Gran Muralla China",
    "Partenón",
    "Castillo de Chichén Itzá",
]


def generar_imagen_blanca(producto_id, nombre):
    """Genera una imagen placeholder blanca con el nombre del producto."""
    img = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(img)
    
    # Dibujar borde sutil
    draw.rectangle([10, 10, 790, 790], outline='#E0E0E0', width=2)
    
    # Texto del nombre
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # Centrar texto
    bbox = draw.textbbox((0, 0), nombre, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (800 - text_width) / 2
    y = (800 - text_height) / 2
    
    draw.text((x, y), nombre, fill='#666666', font=font)
    
    # Guardar imagen
    ruta_imagen = IMAGES_DIR / producto_id / f"{producto_id}_modelo_blanco.jpg"
    ruta_imagen.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(ruta_imagen), 'JPEG', quality=95)
    
    return str(ruta_imagen)


def main():
    print("=" * 70)
    print("MODIFICACIÓN DE PRODUCTOS - NOMBRES, PRECIOS E IMÁGENES")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos totales: {len(productos)}")
    
    # 1. Cambiar nombres
    nombres_cambiados = 0
    for prod in productos:
        for viejo, nuevo in NOMBRE_CAMBIAR.items():
            if prod["nombre_yolitia"] == viejo:
                prod["nombre_yolitia"] = nuevo
                nombres_cambiados += 1
                print(f"  Nombre cambiado: {viejo} → {nuevo}")
    
    # 2. Asignar precios
    precios_asignados = 0
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        for key, precio in PRECIOS.items():
            if key.lower() in nombre.lower():
                prod["precio"] = precio
                precios_asignados += 1
                print(f"  {nombre[:45]:<45} ${precio}")
                break
    
    # 3. Generar imágenes blancas para productos específicos
    imagenes_generadas = 0
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        for key in PRODUCTOS_IMAGEN_BLANCA:
            if key.lower() in nombre.lower():
                producto_id = prod["id"]
                ruta = generar_imagen_blanca(producto_id, nombre)
                
                # Actualizar la imagen principal del producto
                if prod["imagenes"]:
                    prod["imagenes"][0]["ruta_local"] = ruta
                    prod["imagenes"][0]["filename"] = f"{producto_id}_modelo_blanco.jpg"
                    prod["imagen_principal"] = f"{producto_id}_modelo_blanco.jpg"
                
                imagenes_generadas += 1
                print(f"  Imagen blanca generada: {nombre[:40]}")
                break
    
    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Nombres cambiados: {nombres_cambiados}")
    print(f"Precios asignados: {precios_asignados}")
    print(f"Imágenes blancas generadas: {imagenes_generadas}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
