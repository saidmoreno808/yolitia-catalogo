"""
Traduce nombres de productos al español de forma más natural.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
JSON_FILE = DATA_DIR / "yolitia_products_database.json"


TRADUCCIONES_COMPLETAS = {
    # Joyería
    "Serpent Of Silk Vows Earrings": "Aretes Serpiente de Seda",
    "Infinite Node Of Love Earrings": "Aretes Nodo Infinito de Amor",
    "Mushroom Earrings": "Aretes Hongo del Bosque",
    "Cat Skeleton Earrings": "Aretes Esqueleto de Gato",
    "Medusa Earrings": "Aretes Medusa",
    "Earrings Halloween": "Aretes Noche de Brujas",
    "Heart Web Earring Halloween": "Aretes Telaraña de Amor",
    "Scream Earrings Halloween": "Aretes Grito",
    "Halloween Jason Earring": "Aretes Jason",
    "Deadly Jelly Dangling Earrings": "Aretes Medusa Mortal",
    "Paper Boat Origami Earrings": "Aretes Barco de Papel",
    "Cute Cat Earring": "Aretes Gatito",
    "Earrings Tree Of Life": "Aretes Árbol de la Vida",
    "Eclipse Earrings": "Aretes Eclipse",
    "Earrings Butterfly": "Aretes Mariposa",
    "Paw Earrings": "Aretes Patita",
    "3D Balloon Dog Earrings": "Aretes Perro Globo",
    "Earrings Cat": "Aretes Silueta Gato",
    "Spider Dangle Earrings": "Aretes Araña Colgante",
    "Moon Cat Earring Halloween": "Aretes Luna y Gato",
    "Coffee Cup Earrings": "Aretes Taza de Café",
    "Sun Earrings": "Aretes Sol",
    "Woven Heart Earrings": "Aretes Corazón Tejido",
    "Mandala Maze Earrings 0 4 Nozzle": "Aretes Mandala Laberinto",
    "Paper Plane Origami Earrings": "Aretes Avión de Papel",
    "Sakura Cherry Blossom Earring Keychain": "Llavero Flor de Sakura",
    "The Great Wave Off Kanagawa Earrings": "Aretes Gran Ola de Kanagawa",
    "Jewelry Organizer For Earrings Rings Necklaces": "Joyero Organizador",
    
    # Fidgets
    "Fidget Clicker": "Pulsador Zen",
    "Turning Fidget Death Star Keychain": "Llavero Estrella Mortal",
    "Print In Place Fidget Toggle Switch": "Interruptor Fidget",
    "Star Wars Fidget Clicker 2": "Pulsador Star Wars",
    "Spray Paint Can Fidget": "Lata de Spray Fidget",
    "Clicker Master The Heart Of The Fidget": "Pulsador Maestro",
    "Otf Fidget Knife Only 3 Parts": "Navaja Fidget OTF",
    "Gear Shift Fidget Toy Print In Place": "Palanca de Cambios Fidget",
    "Fidget Click Flick Swoosh Print In Place": "Fidget Swoosh",
    
    # Hogar y decoración
    "Indoor Plant Pot The Arcadia With Hidden": "Maceta Arcadia",
    "Veil Petal Sculptural Decor": "Velo de Pétalos",
    "Calavera Skull Ornament With Heart Pattern": "Calavera del Corazón",
    "Heart Of Eternal Motion": "Corazón de Movimiento Eterno",
    "Origami Spiral Of Life Clock": "Reloj Espiral de la Vida",
    "Table Tealight Lamp Set 2": "Lámparas Vela para Mesa",
    "Ammonite Fossil": "Fósil de Ammonite",
    "Giganotosaurus Fossil": "Fósil de Giganotosaurio",
    "Unicorn Skull Fossil": "Fósil Cráneo de Unicornio",
    "Spiral An Ammonite Fossil Sculpture": "Espiral Ammonite",
    "Angled Toothbrush Holder Moonwalk Michael": "Soporte Cepillos Moonwalk",
    "Solar System Lithophane Planet Lamps 150Mm": "Lámparas Sistema Solar",
    "Illuminated Nativity Scene": "Nacimiento Iluminado",
    "Deathstar Lamp Kit Adapter": "Lámpara Estrella Mortal",
    "Modern Wall Clock Clock Components Kit": "Reloj de Pared Moderno",
    "Porsche Wall Clock": "Reloj Porsche",
    "Cube Clock For Kit 011 Ikea": "Reloj Cubo",
    "James Webb Wall Clock Now With Add On": "Reloj James Webb",
    "Wall Clock Two Tone Minimalist Satisfying": "Reloj Minimalista Bicolor",
    "Dali Wall Clock": "Reloj Dalí de Pared",
    "Arri 650W Plus Fresnel Spot Light Lamp": "Lámpara Arri",
    "Butterfly Drawer Jewelry Box": "Joyero Mariposa",
    "Popocatepetl Mexico City Volcano Topography": "Volcán Popocatépetl",
    "2026 Graduation Cake Topper": "Topper Graduación 2026",
    "Maya Pyramid": "Pirámide Maya",
    "Chichen Itza Pyramid Sand Castle Mold": "Pirámide Chichén Itzá",
    "Balloon Unicorn Llama Figures Decorative": "Figuras Unicornio y Llama",
    "Christ The Redeemer Rio De Janeiro Brazil": "Cristo Redentor",
    "Florence Cathedral Italy": "Catedral de Florencia",
    "Great Wall Of China": "Gran Muralla China",
    "Great Pyramids Of Giza Egypt": "Pirámides de Giza",
    "Parthenon Reconstruction Athens Greece": "Partenón",
    "Chichen Itza El Castillo Yucatan Mexico": "Castillo de Chichén Itzá",
    "Desk Edge Cup And Headphone Holder": "Organizador de Escritorio",
    "Recaro Racing Seat Phone Holder": "Soporte Teléfono Recaro",
    "Tie Fighter Kit Card": "Tarjeta Tie Fighter",
    "T Rex Skeleton Kit Card": "Tarjeta Esqueleto T-Rex",
    "At St Walker Kit Card": "Tarjeta AT-ST Walker",
    "Moon Lamp For Led Lamp 001 Hires": "Lámpara Luna",
    "Charizard Elemental Voronoi Art Edition": "Charizard Voronoi",
    "Wall Organizer With Hooks And Shelf": "Organizador de Pared",
    "The High Voyager Incense Holder": "Porta Incienso Voyager",
    "Modern Entryway Organizer Shelf With Key": "Organizador de Entrada",
    "World Globe Minimalist Line Art Wall Decor": "Globo Terráqueo Minimalista",
    "Graduate": "Graduado",
    "Dripping Wall Shelf Bold Statement Piece": "Estante Goteo",
    "Mushroom Shelves Easy Installation": "Estantes Hongo",
    "Cute Valentines Statue": "Estatua San Valentín",
    "Minimalist Father S Day Statue Father Son": "Estatua Día del Padre",
    "Ethereal Kiss Statuette": "Estatua Beso Etéreo",
    "Minimalist Father S Day Statue Father Daughter": "Estatua Día del Padre",
    "Eternal Duo Love Sculpture": "Escultura Amor Eterno",
    "Wedding Topper Hochzeitstorten Deko": "Topper Boda",
    "Abc Elasmosaurus Educational Alphabet Puzzle": "Rompecabezas ABC Elasmosaurio",
    "Ikea Lampshade Hemma Strala Sunneby Havs": "Pantalla Lámpara IKEA",
    "Parametric Foldable Under Desk Cup Holder": "Porta Tazas Paramétrico",
    "Halloween Skull Lantern Dia De Los Muertos": "Lámpara Calavera",
    "Ornamental Angel Lantern Tealight": "Lámpara Ángel",
    "Delorean Dmc 12 Back To The Future Kit Card": "Tarjeta DeLorean",
    "Golf Mk1 Kit Card": "Tarjeta Golf Mk1",
    "Key Jewelry Organizer Tree": "Organizador Joyero Árbol",
    "Dog Kit Card Multiple Breeds": "Tarjeta Perros",
    "Wildlife Kit Card Multiple Species": "Tarjeta Vida Silvestre",
    "Nobody Prayer Sculpture Of Contemplation": "Escultura Oración",
    "Vinograce Elegance Wine Holder": "Porta Vino Vinograce",
    "Celestial Resonance Beyond Sight": "Resonancia Celestial",
    "Interlocking Toroidal Vases Minimalist Modern": "Jarrones Toroidales",
    "Moto Kit Card 2": "Tarjeta Motos",
    "Hogwarts Harry Potter": "Maceta Hogwarts",
    "Igloo Glow Lamp Led Candle Cover": "Lámpara Iglú",
    "Pokeball Keychain Needed": "Llavero Pokeball",
    "Plyometric Box Storage Crossfit": "Caja Plyométrica Crossfit",
    "Gym Sis Kettlebell Keychain": "Llavero Kettlebell Gym",
    "Turntable With Vinyl Coasters Coffee Coasters": "Tornamesa con Posavasos",
    "Nike Calm Slides Keychain": "Llavero Nike",
    "Cycling Helmet Keychain": "Llavero Casco Ciclismo",
    "Gym Bro Kettlebell Keychain": "Llavero Kettlebell Gym",
    "Golden Glove Trophy Customizable Needed": "Trofeo Guante de Oro",
    "Golden Boot Trophy Customizable Needed": "Trofeo Bota de Oro",
    "Playstation 1 Ps1 Keychain": "Llavero PlayStation",
    "Nintendo Game Boy Keychain": "Llavero Game Boy",
    "Super Nintendo Controller Keychain": "Llavero Super Nintendo",
    "Line 6 Guitar Pick Holder 5 Picks": "Porta Púas Line 6",
    "Ibanez Pia Guitar Pick Holder": "Porta Púas Ibanez",
    "Gibson Les Paul Guitar Pick Holder": "Porta Púas Gibson",
    "Fender Frontman Amp Nfc Tag Keychain": "Llavero NFC Fender",
    "Marshall Amp Nfc Tag Keychain": "Llavero NFC Marshall",
    "Fraction Learning Puzzle": "Rompecabezas Fracciones",
    "Deco Pot Isabella Valentine S Day": "Maceta Isabella",
    "Moon Planter With Base": "Maceta Luna con Base",
    "Wall Mounted Planter Pot With Drip Tray": "Maceta de Pared",
    "Wavy Lamp E27 E26 Base Petg": "Lámpara Ondulada",
    "Minimalist Portable Chess Set": "Ajedrez Portátil Minimalista",
    "Customizable Checklist For Children": "Lista de Tareas para Niños",
    "Activity Board For Babies": "Tablero de Actividades para Bebés",
    "Numbers Puzzle And Counting Tray For Toddlers": "Rompecabezas Números",
    "Activity Board Montessori Digital Numbers": "Tablero Montessori Números",
    "Kpop Demon Hunters Coloring Panel 2 Crafts": "Panel Colorear Kpop",
    "Fractions For Montessori Learning": "Fracciones Montessori",
    "Kids Educational Human Body": "Cuerpo Humano Educativo",
    "Mother Child Statue": "Estatua Madre e Hijo",
    "Swirly Plant Pot": "Maceta Espiral",
    "Irregular Flower Pot": "Maceta Irregular",
    "Modern Bird Feeder": "Comedero Moderno para Aves",
    "Plant Watering Globe": "Globo Regador",
    "Fossil Planter": "Maceta Fósil",
    "Schmuckstander": "Soporte para Joyería",
    "Human Body Jigsaw Puzzle For Kids": "Rompecabezas Cuerpo Humano",
    "3D Scanned Hand Jewelry Holder Supports": "Soporte Joyero Mano 3D",
    "Bow Pen And Makeup Brush Organizer Q Craft": "Organizador Brochas con Moño",
    "Makeup Brush Holder Surreal Decorative Vase": "Soporte Brochas Maquillaje",
    "Puzzle Animal Silhouette Africa": "Rompecabezas Animales África",
    "Jewelry Deer Box": "Joyero Ciervo",
    "Rounded Conch Container": "Contenedor Concha Redondeada",
    "Animal Puzzle Learning": "Rompecabezas Animales",
    "Fender Stratocaster Key Hanger Guitar Key Holder": "Llavero Guitarra Stratocaster",
    "Ultimate Koozie V2": "Funda Térmica Ultimate",
    "Customizable Baseball Bat": "Bat de Béisbol Personalizable",
    "Mini Baseball Glove Keychain": "Llavero Guante de Béisbol",
}


def traducir_nombre(nombre_original):
    """Busca traducción completa o genera una versión en español."""
    
    # Buscar traducción exacta
    if nombre_original in TRADUCCIONES_COMPLETAS:
        return TRADUCCIONES_COMPLETAS[nombre_original]
    
    # Buscar coincidencia parcial
    for key, value in TRADUCCIONES_COMPLETAS.items():
        if key.lower() in nombre_original.lower():
            return value
    
    # Traducciones automáticas básicas
    nombre_lower = nombre_original.lower()
    
    if "earring" in nombre_lower:
        return "Aretes"
    elif "keychain" in nombre_lower or "key chain" in nombre_lower:
        return "Llavero"
    elif "pot" in nombre_lower or "planter" in nombre_lower:
        return "Maceta"
    elif "clock" in nombre_lower:
        return "Reloj"
    elif "fidget" in nombre_lower:
        return "Fidget"
    elif "organizer" in nombre_lower or "holder" in nombre_lower:
        return "Organizador"
    elif "lamp" in nombre_lower or "light" in nombre_lower:
        return "Lámpara"
    elif "sculpture" in nombre_lower or "figure" in nombre_lower or "statue" in nombre_lower:
        return "Figura Decorativa"
    elif "box" in nombre_lower:
        return "Caja"
    elif "toy" in nombre_lower:
        return "Juguete"
    elif "puzzle" in nombre_lower:
        return "Rompecabezas"
    
    # Si no hay traducción, usar el nombre original
    return nombre_original


def main():
    print("=" * 70)
    print("TRADUCCIÓN COMPLETA DE NOMBRES AL ESPAÑOL")
    print("=" * 70)
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    productos = data["productos"]
    print(f"\nProductos a procesar: {len(productos)}")
    
    traducidos = 0
    for prod in productos:
        nombre_original = prod["nombre_original"]
        nombre_actual = prod["nombre_yolitia"]
        
        # Siempre actualizar con la mejor traducción
        nuevo_nombre = traducir_nombre(nombre_original)
        if nuevo_nombre != nombre_actual:
            prod["nombre_yolitia"] = nuevo_nombre
            traducidos += 1
            print(f"  {nombre_original[:45]:<45} → {nuevo_nombre[:40]}")
    
    # Guardar cambios
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'=' * 70}")
    print(f"Traducidos: {traducidos}/{len(productos)} productos")
    print(f"Archivo actualizado: {JSON_FILE}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
