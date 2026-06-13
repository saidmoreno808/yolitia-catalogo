import json
data = json.load(open('yolitia_catalog/data/yolitia_products_database.json','r',encoding='utf-8'))
productos = data['productos']
con_precio = [p for p in productos if p.get('precio')]
sin_precio = [p for p in productos if not p.get('precio')]
print(f'Productos con precio: {len(con_precio)}')
print(f'Productos sin precio: {len(sin_precio)}')
print()
print('PRODUCTOS CON PRECIO:')
for p in sorted(con_precio, key=lambda x: x.get('precio', 0)):
    nombre = p['nombre_yolitia']
    precio = p['precio']
    print(f'  {nombre:<45} ${precio:.0f}')
