"""
Modifica productos: precios, nombres y eliminaciones.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRODUCTOS_A_ELIMINAR = [
    "Lámpara Ángel",
    "Estatua Madre e Hijo",
]

MODIFICACIONES = {
    "Pantalla Lámpara IKEA": {
        "nuevo_nombre": "Pantalla Lámpara Escandinava",
        "precio": 250,
    },
    "Interlocking Toroidal Vases": {
        "nuevo_nombre": "Jarrones Toroidales Entrelazados",
        "precio": 250,
    },
}

PRECIOS = {
    "Escultura Amor Eterno": 150,
    "Escultura Oración": 150,
    "Lámpara Iglú": 100,
    "Lámpara Ondulada": 380,
}


def main():
    print("=" * 70)
    print("MODIFICACIÓN DE PRODUCTOS")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos antes: {len(productos)}")
    
    # 1. Eliminar productos
    productos_filtrados = []
    eliminados = []
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        debe_eliminar = False
        for prod_elim in PRODUCTOS_A_ELIMINAR:
            if prod_elim.lower() in nombre.lower():
                debe_eliminar = True
                eliminados.append(nombre)
                break
        if not debe_eliminar:
            productos_filtrados.append(prod)
    
    productos = productos_filtrados
    print(f"\nEliminados: {len(eliminados)}")
    for n in eliminados:
        print(f"  - {n}")
    
    # 2. Modificar nombres y precios
    modificados = 0
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        
        for key, mod in MODIFICACIONES.items():
            if key.lower() in nombre.lower():
                prod["nombre_yolitia"] = mod["nuevo_nombre"]
                prod["precio"] = mod["precio"]
                modificados += 1
                print(f"  {nombre[:40]:<40} → {mod['nuevo_nombre'][:40]} ${mod['precio']}")
                break
        
        for key, precio in PRECIOS.items():
            if key.lower() in nombre.lower():
                prod["precio"] = precio
                modificados += 1
                print(f"  {nombre[:40]:<40} ${precio}")
                break
    
    data["productos"] = productos
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Productos restantes: {len(productos)}")
    print(f"Modificaciones: {modificados}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
