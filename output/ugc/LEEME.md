# Fotos UGC de los aretes (arete puesto)

Fotos estilo UGC — como si la clienta se hubiera tomado la foto con el celular —
del arete **puesto en la oreja**, de perfil y **sin cara**.

## Qué hay aquí

| Archivo | Qué es |
|---|---|
| `manifest.json` | El registro completo: por producto, el look usado, los prompts exactos, el tamaño y la fecha |
| `notas.json` | Correcciones por producto que se agregan al prompt (color y tamaño del arete, sobre todo cuando se manda una silueta) |
| `aislados/` | Siluetas de los aretes que hubo que aislar porque su foto traía una tarjeta con el nombre de otra marca o un fondo con textura |
| `contacto-27-aretes.jpg` | Hoja de contacto con las 27 fotos |
| `prueba-ugc-arete.jpg` | La prueba inicial: producto original + dos variantes |

Las fotos del lote **no viven aquí**: se guardan junto al producto, en
`assets/images/productos/YOL-XXX/YOL-XXX_ugc_04.jpg`, y quedan registradas en la
galería de su ficha.

## Estado

- **26 de 27 aretes** tienen su foto UGC, verificada y registrada en la galería.
- **YOL-024 (Aretes Patita) queda pendiente.** El modelo no logra ponerlo: la
  forma de huella lo lleva a generar imágenes donde no hay ninguna parte del
  cuerpo, y ya se intentó con la silueta, con el recorte a color y con notas de
  tamaño y color en el prompt. Es el único caso rebelde de los 27.

## Lo que NO se puede automatizar

El verificador de visión caza el fallo grueso (que no haya oreja) pero **no juzga
realismo ni composición**. En este lote, dos fotos pasaron el verificador y
estaban mal: una con el arete inventado en color crema y tamaño gigante, y otra
que era un collage con una oreja ilustrada pegada sobre un fondo.

**Hay que verlas con el ojo, una por una.** El verificador ahorra tiempo, no
reemplaza la revisión.

## Cómo se hicieron

Dos pasos, porque pedirlo de una sola vez sale mal:

1. **La oreja.** Modelo `qwen-image` (texto → imagen) en Alibaba Model Studio.
   Genera la base: de perfil, solo la oreja, el borde de la mandíbula y el cuello.
2. **El arete.** Modelo `qwen-image-edit`, mandándole **dos imágenes a la vez**:
   la foto de la oreja y la foto del producto. Así el arete que aparece es el
   real, no una invención.

```bash
NODE_PATH=yolitia_agente/node_modules \
  node yolitia-site/scripts/ugc-aretes-lote.mjs [--solo YOL-014] [--limite 5] [--rehacer]
```

Es **reanudable**: lo que ya está hecho se salta, y el manifiesto se va escribiendo
sobre la marcha.

## Las decisiones del prompt que importan

- **"La cara NO se ve: queda fuera del encuadre"**, en positivo y en el negativo.
  Si no se dice, el modelo mete media cara — y ahí la IA se cae.
- **"Piel real sin retocar, con textura visible, poros y vello fino"**. En un
  primer plano de oreja, la piel es lo único que delata. Sin esto sale piel de
  cera.
- **"Que el arete quede completo dentro del encuadre, con aire por debajo"**. Si
  no, lo corta en el borde inferior.
- **"No la reemplaces por una foto del arete solo"**, en el prompt y en el
  negativo. Sin esto a veces devuelve el producto sobre fondo blanco y se pierde
  el trabajo (pasó con YOL-028 en el primer intento).
- El tamaño real: *"no lo agrandes"*. Un arete gigante vende más pero engaña.

## Cómo se comprueba que salió bien

El script **no confía en que la API devuelva lo que se le pidió**. Mide la
**fracción de píxeles color piel** de la imagen resultante:

- Una foto de una oreja tiene mucha piel (más del 15%).
- Una foto del producto sobre fondo liso, casi nada.

Si no llega al 15%, considera que falló y **reintenta hasta 3 veces**. Es la
diferencia entre 27 fotos buenas y 27 fotos donde algunas son el arete solo.

## Los "looks"

Mandar el mismo prompt 27 veces devuelve **la misma mujer 27 veces** y la tienda
se ve falsa. El script rota 9 looks (tono de piel, pelo, fondo y luz) tomando el
índice del producto, de forma determinista: el mismo producto siempre recibe el
mismo look.

## Lo que hay que revisar con el ojo

El detector caza el fallo grueso (que no haya oreja), pero **no** juzga estética.
Antes de publicar, ver las fotos de corrido:

- que el arete sea el del producto;
- que esté enganchado al lóbulo y no flotando ni sobre la oreja;
- que el pelo no lo tape;
- que no se vea nada de cara.

## Qué decidir como negocio

Estas fotos muestran **una modelo que no existe**. Es práctica común en
e-commerce, pero es una decisión del negocio, no técnica. Lo que sí es cierto es
que **el arete que aparece es el producto real**, no una versión inventada.
