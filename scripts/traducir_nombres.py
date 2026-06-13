"""
Traduce todos los nombres de productos al español.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"


TRADUCCIONES = {
    "Rounded Conch Container": "Contenedor Concha Redondeada",
    "Schmuckstander": "Soporte para Joyería",
    "Kids Educational Human Body": "Cuerpo Humano Educativo para Niños",
    "Fractions For Montessori Learn": "Fracciones para Aprendizaje Montessori",
    "Activity Board For Babies": "Tablero de Actividades para Bebés",
    "Fender Frontman Amp Nfc Tag Ke": "Llavero NFC Amplificador Fender",
    "Makeup Brush Holder Surreal De": "Soporte para Brochas de Maquillaje",
    "Bow Pen And Makeup Brush Organ": "Organizador de Plumas y Brochas con Moño",
    "Ultimate Koozie": "Funda Térmica Ultimate",
    "Golf Mk1 Kit Card": "Tarjeta Kit Golf Mk1",
    "Turntable With Vinyl Coasters Coffee Coa": "Tornamesa con Posavasos de Vinilo",
    "Marshall Amp Nfc Tag Keychain": "Llavero NFC Amplificador Marshall",
    "Modern Bird Feeder": "Comedero Moderno para Aves",
    "Wall Clock Two Tone Minimalist Satisfying Clock": "Reloj Minimalista Bicolor",
    "Nobody Prayer Sculpture Of Contemplation": "Escultura Oración de Contemplación",
    "Dali Wall Clock": "Reloj Dalí de Pared",
    "Jewelry Deer Box": "Joyero Ciervo",
    "Plyometric Box Storage Crossfit": "Caja Plyométrica Crossfit",
    "Solar System Lithophane Planet Lamps 150Mm": "Lámparas Sistema Solar Litofanía",
    "Moon Planter With Base": "Maceta Luna con Base",
    "Gym Bro Kettlebell Keychain": "Llavero Kettlebell Gym",
    "Otf Fidget Knife Only 3 Parts": "Navaja Fidget OTF de 3 Piezas",
    "Gear Shift Fidget Toy Print In Place": "Juguete Fidget Palanca de Cambios",
    "Customizable Baseball Bat": "Bat de Béisbol Personalizable",
    "Mini Baseball Glove Keychain": "Llavero Guante de Béisbol Mini",
    "1132655-Spray Paint Can Fidget": "Lata de Spray Fidget",
    "1496019-Customizable Baseball Bat": "Bat de Béisbol Personalizable",
    "1864468-Mini Baseball Glove Keychain": "Llavero Guante de Béisbol Mini",
    "1276383-Plyometric Box Storage Crossfit": "Caja Plyométrica Crossfit",
    "1492864-Ultimate Koozie V2": "Funda Térmica Ultimate V2",
    "1352373-Gym Bro Kettlebell Keychain": "Llavero Kettlebell Gym",
}


def traducir_nombre(nombre_original):
    """Busca traducción o genera una versión en español."""
    
    # Buscar en diccionario exacto
    if nombre_original in TRADUCCIONES:
        return TRADUCCIONES[nombre_original]
    
    # Buscar coincidencia parcial
    for key, value in TRADUCCIONES.items():
        if key.lower() in nombre_original.lower() or nombre_original.lower() in key.lower():
            return value
    
    # Traducciones automáticas básicas
    nombre_lower = nombre_original.lower()
    
    if "earring" in nombre_lower:
        return f"Aretes {nombre_original.split()[-1].title()}" if len(nombre_original.split()) > 1 else "Aretes"
    elif "keychain" in nombre_lower or "key chain" in nombre_lower:
        return f"Llavero {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Llavero"
    elif "pot" in nombre_lower or "planter" in nombre_lower:
        return f"Maceta {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Maceta"
    elif "clock" in nombre_lower:
        return f"Reloj {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Reloj"
    elif "fidget" in nombre_lower:
        return f"Fidget {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Fidget"
    elif "organizer" in nombre_lower or "holder" in nombre_lower:
        return f"Organizador {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Organizador"
    elif "lamp" in nombre_lower or "light" in nombre_lower:
        return f"Lámpara {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Lámpara"
    elif "sculpture" in nombre_lower or "figure" in nombre_lower:
        return f"Figura {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Figura Decorativa"
    elif "box" in nombre_lower:
        return f"Caja {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Caja"
    elif "toy" in nombre_lower:
        return f"Juguete {nombre_original.split()[0].title()}" if len(nombre_original.split()) > 1 else "Juguete"
    
    # Si no hay traducción, usar el nombre original pero capitalizado
    return nombre_original.title()


def main():
    print("=" * 70)
    print("TRADUCCIÓN DE NOMBRES AL ESPAÑOL")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos a procesar: {len(productos)}")
    
    traducidos = 0
    for prod in productos:
        nombre_original = prod["nombre_original"]
        nombre_actual = prod["nombre_yolitia"]
        
        # Si el nombre actual es igual al original o está en inglés, traducir
        if nombre_actual == nombre_original or any(c.isascii() and c.isalpha() for c in nombre_actual):
            nuevo_nombre = traducir_nombre(nombre_original)
            prod["nombre_yolitia"] = nuevo_nombre
            traducidos += 1
            print(f"  {nombre_original[:40]:<40} → {nuevo_nombre[:40]}")
    
    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Traducidos: {traducidos}/{len(productos)} productos")
    print(f"Archivo actualizado: {JSON_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
