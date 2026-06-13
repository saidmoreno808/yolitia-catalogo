import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

ELIMINAR = ["Bat de Béisbol Personalizable"]

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

data["productos"] = filtrados

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Eliminados: {len(eliminados)}")
for n in eliminados:
    print(f"  - {n}")
print(f"Después: {len(filtrados)}")
