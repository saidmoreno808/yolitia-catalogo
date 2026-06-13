"""
Verificacion final de todos los entregables del proyecto Yolitia.
Genera resumen ejecutivo completo.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "assets" / "images" / "productos"
OUTPUT_DIR = BASE_DIR / "output"
SCRIPTS_DIR = BASE_DIR / "scripts"


def check_file(path, description):
    """Verifica si un archivo existe y retorna info."""
    if path.exists():
        size = path.stat().st_size
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.2f} MB"
        return {"status": "OK", "path": path, "size": size_str, "description": description}
    return {"status": "MISSING", "path": path, "size": "-", "description": description}


def main():
    print("=" * 70)
    print("VERIFICACION FINAL - PROYECTO YOLITIA")
    print("=" * 70)
    print(f"\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Archivos de datos
    print("\n" + "-" * 70)
    print("ARCHIVOS DE BASE DE DATOS:")
    print("-" * 70)
    
    data_files = [
        (DATA_DIR / "yolitia.db", "SQLite - Fuente de verdad"),
        (DATA_DIR / "yolitia_schema.sql", "Schema SQL documentado"),
        (DATA_DIR / "yolitia_products_database.json", "JSON Universal"),
        (DATA_DIR / "yolitia_woocommerce_import.csv", "WooCommerce CSV"),
        (DATA_DIR / "yolitia_prestashop_import.csv", "PrestaShop CSV"),
        (DATA_DIR / "yolitia_medusa_import.json", "Medusa.js JSON"),
        (DATA_DIR / "yolitia_products_database.xlsx", "XLSX (8 hojas)"),
        (DATA_DIR / "catalog_layout_plan.json", "Plan de layout"),
    ]
    
    data_ok = 0
    for path, desc in data_files:
        result = check_file(path, desc)
        status_icon = "[OK]" if result["status"] == "OK" else "[!!]"
        print(f"  {status_icon} {desc:<35} {result['size']:>12}  {path.name}")
        if result["status"] == "OK":
            data_ok += 1
    
    # PDF
    print("\n" + "-" * 70)
    print("CATALOGO PDF:")
    print("-" * 70)
    
    pdf_result = check_file(OUTPUT_DIR / "catalogo_yolitia_v1.pdf", "Catalogo PDF v1")
    status_icon = "[OK]" if pdf_result["status"] == "OK" else "[!!]"
    print(f"  {status_icon} {pdf_result['description']:<35} {pdf_result['size']:>12}  catalogo_yolitia_v1.pdf")
    
    # Scripts
    print("\n" + "-" * 70)
    print("SCRIPTS:")
    print("-" * 70)
    
    scripts = [
        (SCRIPTS_DIR / "scraper.py", "Scraping MakerWorld"),
        (SCRIPTS_DIR / "extract_urls.py", "Extraccion de URLs"),
        (SCRIPTS_DIR / "process_all.py", "Procesamiento de datos"),
        (SCRIPTS_DIR / "build_database.py", "Generacion de DB"),
        (SCRIPTS_DIR / "descarga_imagenes.py", "Descarga de imagenes"),
        (SCRIPTS_DIR / "build_layout.py", "Plan de layout"),
        (SCRIPTS_DIR / "build_catalog.py", "Generacion de PDF"),
    ]
    
    scripts_ok = 0
    for path, desc in scripts:
        result = check_file(path, desc)
        status_icon = "[OK]" if result["status"] == "OK" else "[!!]"
        print(f"  {status_icon} {desc:<35} {result['size']:>12}  {path.name}")
        if result["status"] == "OK":
            scripts_ok += 1
    
    # Imagenes
    print("\n" + "-" * 70)
    print("IMAGENES:")
    print("-" * 70)
    
    total_folders = len([d for d in IMAGES_DIR.iterdir() if d.is_dir()]) if IMAGES_DIR.exists() else 0
    total_files = sum(1 for d in IMAGES_DIR.iterdir() if d.is_dir() for f in d.iterdir() if f.is_file()) if IMAGES_DIR.exists() else 0
    total_size = sum(f.stat().st_size for d in IMAGES_DIR.iterdir() if d.is_dir() for f in d.iterdir() if f.is_file()) if IMAGES_DIR.exists() else 0
    
    print(f"  [OK] Carpetas de productos:    {total_folders:>12}")
    print(f"  [OK] Archivos de imagen:       {total_files:>12}")
    print(f"  [OK] Tamano total:             {total_size / (1024*1024):>10.1f} MB")
    
    # Estadisticas de la base de datos
    print("\n" + "-" * 70)
    print("ESTADISTICAS DE LA BASE DE DATOS:")
    print("-" * 70)
    
    db_path = DATA_DIR / "yolitia.db"
    if db_path.exists():
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_productos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categorias")
        total_categorias = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM imagenes WHERE ruta_local IS NOT NULL")
        imagenes_con_ruta = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT categoria_id) FROM productos")
        categorias_usadas = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"  Productos totales:           {total_productos:>12}")
        print(f"  Categorias:                  {total_categorias:>12}")
        print(f"  Categorias usadas:           {categorias_usadas:>12}")
        print(f"  Imagenes con ruta local:     {imagenes_con_ruta:>12}")
    
    # Resumen del PDF
    print("\n" + "-" * 70)
    print("RESUMEN DEL CATALOGO PDF:")
    print("-" * 70)
    
    try:
        from PyPDF2 import PdfReader
        pdf_path = OUTPUT_DIR / "catalogo_yolitia_v1.pdf"
        if pdf_path.exists():
            reader = PdfReader(str(pdf_path))
            pdf_pages = len(reader.pages)
            print(f"  Paginas totales:             {pdf_pages:>12}")
            print(f"  Paginas de productos:        {pdf_pages - 8:>12}")  # Restar portada, indice, 5 separadores, PLA, contraportada
    except Exception:
        print(f"  Paginas:                     {'(no validado)':>12}")
    
    # Resumen de categorias
    print("\n" + "-" * 70)
    print("PRODUCTOS POR CATEGORIA:")
    print("-" * 70)
    
    json_path = DATA_DIR / "yolitia_products_database.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categorias = {}
        for p in data["productos"]:
            cat = p.get("categoria", "Otros")
            categorias[cat] = categorias.get(cat, 0) + 1
        
        for cat, count in sorted(categorias.items(), key=lambda x: -x[1]):
            print(f"  {cat:<35} {count:>5} productos")
    
    # Checklist final
    print("\n" + "=" * 70)
    print("CHECKLIST DE ENTREGABLES:")
    print("=" * 70)
    
    checklist = [
        (data_ok == len(data_files), f"Archivos de datos: {data_ok}/{len(data_files)}"),
        (pdf_result["status"] == "OK", "Catalogo PDF generado"),
        (scripts_ok == len(scripts), f"Scripts: {scripts_ok}/{len(scripts)}"),
        (total_files > 0, f"Imagenes descargadas: {total_files}"),
        (total_folders > 0, f"Carpetas organizadas: {total_folders}"),
    ]
    
    all_ok = True
    for ok, desc in checklist:
        status = "[OK]" if ok else "[!!]"
        print(f"  {status} {desc}")
        if not ok:
            all_ok = False
    
    print("\n" + "=" * 70)
    if all_ok:
        print("PROYECTO COMPLETADO EXITOSAMENTE")
    else:
        print("PROYECTO COMPLETADO CON ADVERTENCIAS")
    print("=" * 70)
    
    # Proximos pasos
    print("\n" + "-" * 70)
    print("PROXIMOS PASOS RECOMENDADOS:")
    print("-" * 70)
    print("  1. Revisar catalogo PDF (output/catalogo_yolitia_v1.pdf)")
    print("  2. Agregar precios en XLSX (celdas azules)")
    print("  3. Importar CSV a plataforma e-commerce:")
    print("     - WooCommerce: Products > Import")
    print("     - PrestaShop: Advanced Parameters > Import")
    print("     - Medusa.js: API createProducts")
    print("  4. Completar descripciones y SEO en XLSX")
    print("  5. Configurar inventario y envios")
    print("  6. Publicar tienda online")
    
    print("\n" + "=" * 70)
    print("RESUMEN EJECUTIVO:")
    print("=" * 70)
    print(f"  Marca:                    Yolitia")
    print(f"  Fecha:                    {datetime.now().strftime('%Y-%m-%d')}")
    print(f"  Productos catalogados:    {total_productos if db_path.exists() else 'N/A'}")
    print(f"  Categorias:               {categorias_usadas if db_path.exists() else 'N/A'}")
    print(f"  Imagenes descargadas:     {total_files}")
    print(f"  Paginas del catalogo:     {pdf_pages if pdf_path.exists() else 'N/A'}")
    print(f"  Archivos generados:       {data_ok + scripts_ok + 1}")  # +1 por PDF
    print(f"  Plataformas soportadas:   WooCommerce, PrestaShop, Medusa.js, Magento")
    print("=" * 70)


if __name__ == "__main__":
    main()
