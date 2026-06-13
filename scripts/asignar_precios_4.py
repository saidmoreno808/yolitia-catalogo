import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRECIOS = {
    "Soporte Cepillos Moonwalk": 80,
    "Organizador de Escritorio": 200,
    "Soporte Teléfono Recaro": 120,
    "Organizador de Pared": 250,
    "Porta Incienso Voyager": 150,
    "Organizador de Entrada": 220,
    "Porta Tazas Paramétrico": 200,
    "Porta Vino Vinograce": 200,
}

with open(JSON_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

productos = data["productos"]
asignados = 0
for prod in productos:
    nombre = prod["nombre_yolitia"]
    for key, precio in PRECIOS.items():
        if key.lower() in nombre.lower():
            prod["precio"] = precio
            asignados += 1
            print(f"  {nombre[:45]:<45} ${precio}")
            break

with open(JSON_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nPrecios asignados: {asignados}/{len(PRECIOS)}")
