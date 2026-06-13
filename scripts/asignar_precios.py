"""
Asigna precios a productos específicos del catálogo.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRECIOS = {
    "Maceta de Pared": 250,
    "Aretes Serpiente de Seda": 20,
    "Aretes Nodo Infinito de Amor": 20,
    "Joyero Organizador": 100,
    "Aretes Hongo del Bosque": 20,
    "Aretes Esqueleto de Gato": 30,
    "Aretes Medusa": 30,
    "Aretes Noche de Brujas": 20,
    "Aretes Telaraña de Amor": 20,
    "Aretes Grito": 30,
    "Aretes Jason": 30,
    "Aretes Medusa Mortal": 30,
    "Aretes Barco de Papel": 30,
    "Aretes Gatito": 20,
    "Aretes Árbol de la Vida": 20,
    "Aretes Eclipse": 30,
    "Aretes Mariposa": 20,
    "Aretes Patita": 20,
    "Aretes Perro Globo": 30,
    "Aretes Silueta Gato": 20,
    "Aretes Araña Colgante": 20,
    "Aretes Luna y Gato": 20,
    "Aretes Taza de Café": 30,
    "Aretes Sol": 20,
    "Aretes Corazón Tejido": 30,
    "Aretes Mandala Laberinto": 20,
    "Aretes Avión de Papel": 30,
    "Llavero Flor de Sakura": 30,
    "Aretes Gran Ola de Kanagawa": 30,
    "Organizador Joyero Árbol": 100,
    "Kpop Demon Hunters Coloring Panel": 100,
    "Soporte Joyero Mano 3D": 150,
}


def main():
    print("=" * 70)
    print("ASIGNACIÓN DE PRECIOS")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos totales: {len(productos)}")
    
    asignados = 0
    for prod in productos:
        nombre = prod["nombre_yolitia"]
        
        # Buscar coincidencia en el diccionario de precios
        for nombre_precio, precio in PRECIOS.items():
            if nombre_precio.lower() in nombre.lower() or nombre.lower() in nombre_precio.lower():
                prod["precio"] = precio
                asignados += 1
                print(f"  {nombre[:45]:<45} ${precio}")
                break
    
    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Precios asignados: {asignados}/{len(PRECIOS)}")
    print(f"Archivo actualizado: {JSON_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
