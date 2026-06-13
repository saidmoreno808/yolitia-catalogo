import json
data = json.load(open('yolitia_catalog/data/yolitia_products_database.json','r',encoding='utf-8'))
productos = data['productos']

cats = {}
for p in productos:
    cat = p.get('categoria','?')
    has_img = any(img.get('ruta_local') for img in p.get('imagenes',[]))
    if cat not in cats:
        cats[cat] = {'total': 0, 'con_img': 0}
    cats[cat]['total'] += 1
    if has_img:
        cats[cat]['con_img'] += 1

print('PRODUCTOS POR CATEGORIA:')
for cat, counts in sorted(cats.items()):
    con = counts['con_img']
    tot = counts['total']
    print(f'  {cat:<30} {con:>3}/{tot:>3} con imagen')
