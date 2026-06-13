import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

ELIMINAR = ["Comedero Moderno para Aves"]

PRECIOS = {
    "Maceta Isabella": 250,
    "Maceta Luna con Base": 250,
    "Maceta Espiral": 250,
    "Maceta Irregular": 250,
    "Maceta Fósil": 250,
}

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

productos = data["productos"]
print(f"Antes: {len(productos)}")

filtrados = []
eliminados = []
for prod in productos:
    nombre = prod["nombre_yolitia"]
    debe_eliminar = any(e.lower() in nombre.lower() for e in ELIMINAR)
    if debe_eliminar:
        eliminados.append(nombre)
    else:
        filtrados.append(prod)

productos = filtrados
print(f"Eliminados: {eliminados}")

asignados = 0
for prod in productos:
    nombre = prod["nombre_yolitia"]
    for key, precio in PRECIOS.items():
        if key.lower() in nombre.lower():
            prod["precio"] = precio
            asignados += 1
            print(f"  {nombre[:45]:<45} ${precio}")
            break

data["productos"] = productos

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nDespués: {len(productos)} | Precios asignados: {asignados}")
