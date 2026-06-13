import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
IMAGES_DIR = Path(__file__).parent.parent / "assets" / "images" / "productos"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

# Productos a restaurar
PRODUCTOS_RESTAURAR = [
    "Popocatepetl Mexico City Volca",
    "Gran Muralla China",
    "Partenón",
    "Castillo de Chichén Itzá",
]

LEYENDA_COLOR = "Disponible únicamente en color blanco o negro matte"

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

productos = data["productos"]
restaurados = 0

for prod in productos:
    nombre = prod["nombre_yolitia"]
    producto_id = prod["id"]
    
    for key in PRODUCTOS_RESTAURAR:
        if key.lower() in nombre.lower():
            # Buscar imagen original en la carpeta del producto
            carpeta = IMAGES_DIR / producto_id
            if carpeta.exists():
                # Buscar archivos de imagen (jpg, png)
                imagenes = list(carpeta.glob("*.jpg")) + list(carpeta.glob("*.png"))
                
                # Filtrar para no usar la imagen blanca
                imagenes_originales = [img for img in imagenes if "modelo_blanco" not in img.name]
                
                if imagenes_originales:
                    # Usar la primera imagen original encontrada
                    imagen_original = imagenes_originales[0]
                    ruta_relativa = f"assets/images/productos/{producto_id}/{imagen_original.name}"
                    
                    # Actualizar la imagen principal
                    if prod["imagenes"]:
                        prod["imagenes"][0]["ruta_local"] = ruta_relativa
                        prod["imagenes"][0]["filename"] = imagen_original.name
                        prod["imagen_principal"] = imagen_original.name
                    
                    # Agregar leyenda a la descripción
                    descripcion_actual = prod.get("descripcion_corta", "") or ""
                    if LEYENDA_COLOR not in descripcion_actual:
                        prod["descripcion_corta"] = f"{descripcion_actual} {LEYENDA_COLOR}" if descripcion_actual else LEYENDA_COLOR
                    
                    restaurados += 1
                    print(f"  ✓ {nombre[:45]}")
                    print(f"    Imagen: {imagen_original.name}")
                    print(f"    Leyenda agregada")
            
            break

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n{'=' * 70}")
print(f"Productos restaurados: {restaurados}")
print(f"{'=' * 70}")
