import json

d = json.load(open('yolitia_catalog/data/scraping_processed.json', 'r', encoding='utf-8'))
productos = d['productos']

print('=' * 70)
print('RESUMEN CICLO 1: SCRAPING MAKERWORLD')
print('=' * 70)
print(f'Total productos: {len(productos)}')
total_imgs = sum(1 for p in productos if p.get('imagenes'))
print(f'Total con imagen: {total_imgs}')
print()

cats = {}
for p in productos:
    cat = p['categoria']
    cats[cat] = cats.get(cat, 0) + 1

print('DISTRIBUCION POR CATEGORIA:')
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    pct = count / len(productos) * 100
    print(f'  {cat:<30} {count:>3} ({pct:.1f}%)')

print()
print('MUESTRA DE PRODUCTOS (30 de 158):')
print('-' * 70)
for p in productos[:30]:
    pid = p['id']
    nombre = p['nombre_yolitia'][:33]
    sub = p['subcategoria'][:16]
    cat = p['categoria'][:25]
    print(f'  {pid:<8} {nombre:<35} {sub:<18} {cat}')
print(f'  ... y {len(productos) - 30} productos mas')
print()

print('PRODUCTOS POR SUBCATEGORIA:')
subcats = {}
for p in productos:
    sc = p['subcategoria']
    if sc:
        subcats[sc] = subcats.get(sc, 0) + 1
for sc, count in sorted(subcats.items(), key=lambda x: -x[1]):
    print(f'  {sc:<25} {count:>3}')
