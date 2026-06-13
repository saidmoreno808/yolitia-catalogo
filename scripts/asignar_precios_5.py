import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"

PRECIOS = {
    "Porta Púas Line 6": 100,
    "Porta Púas Ibanez": 100,
    "Porta Púas Gibson": 100,
    "Rompecabezas Números": 250,
    "Organizador Brochas con Moño": 200,
    "Pulsador Zen": 40,
    "Llavero Estrella Mortal": 60,
    "Interruptor Fidget": 20,
    "Fidget Swoosh": 30,
    "Corazón de Movimiento Eterno": 20,
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
