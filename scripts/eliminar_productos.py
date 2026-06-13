"""
Elimina productos específicos del catálogo.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRODUCTOS_A_ELIMINAR = [
    "Maceta Hogwarts",
    "Ultimate Koozie",
    "Pulsador Maestro",
    "Graduado",
]


def main():
    print("=" * 70)
    print("ELIMINACIÓN DE PRODUCTOS")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos antes: {len(productos)}")
    
    # Filtrar productos
    productos_filtrados = []
    eliminados = []
    
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        
        # Verificar si el nombre contiene alguno de los productos a eliminar
        debe_eliminar = False
        for prod_eliminar in PRODUCTOS_A_ELIMINAR:
            if prod_eliminar.lower() in nombre.lower():
                debe_eliminar = True
                eliminados.append(nombre)
                break
        
        if not debe_eliminar:
            productos_filtrados.append(prod)
    
    data["productos"] = productos_filtrados
    
    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nProductos eliminados: {len(eliminados)}")
    for nombre in eliminados:
        print(f"  - {nombre}")
    
    print(f"\nProductos restantes: {len(productos_filtrados)}")
    print(f"Archivo actualizado: {JSON_FILE}")
    print("=" * 70)


if __name__ == "__main__":
    main()
