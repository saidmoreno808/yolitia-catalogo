"""
Asigna precios adicionales a productos del catálogo.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRECIOS_ADICIONALES = {
    "Soporte Brochas Maquillaje": 150,
    "Joyero Ciervo": 150,
    "Maceta Arcadia": 250,
    "Velo de Pétalos": 150,
    "Reloj Espiral de la Vida": 380,
    "Lámparas Vela para Mesa": 350,
    "Fósil de Ammonite": 250,
    "Fósil de Giganotosaurio": 250,
    "Fósil Cráneo de Unicornio": 250,
    "Lámparas Sistema Solar": 350,
    "Reloj de Pared Moderno": 350,
    "Reloj Porsche": 540,
}


def main():
    print("=" * 70)
    print("ASIGNACIÓN DE PRECIOS ADICIONALES")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos totales: {len(productos)}")
    
    asignados = 0
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        
        for nombre_precio, precio in PRECIOS_ADICIONALES.items():
            if nombre_precio.lower() in nombre.lower() or nombre.lower() in nombre_precio.lower():
                prod["precio"] = precio
                asignados += 1
                print(f"  {nombre[:45]:<45} ${precio}")
                break
    
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Precios asignados: {asignados}/{len(PRECIOS_ADICIONALES)}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
