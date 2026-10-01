<#
.SYNOPSIS
  Respalda el catálogo de Yolitia FUERA de este equipo.

.DESCRIPTION
  Por qué existe este script
  --------------------------
  La base maestra del catálogo (data/yolitia_products_database.json) y las imágenes
  curadas viven SOLO en este equipo. Las copias .bak-* que se generan al lado están
  en el MISMO disco: si el disco muere, se pierden el original y las copias juntas.

  Nada de esto es reproducible desde el repositorio:
    - La base tiene nombres, precios, categorías y notas que se curaron a mano.
    - Las imágenes incluyen los renders en blanco y las fotos UGC que generamos.
  Las fotos de ORIGEN sí se pueden volver a bajar de MakerWorld, pero el trabajo
  de curación no.

  Qué hace
  --------
  1. Empaqueta los datos, las imágenes de producto y la documentación.
  2. Calcula el sha256 y lo sube a la Pi (otro equipo físico, no el mismo disco).
  3. Verifica que el hash coincida allá: un respaldo que no se verificó no es
     un respaldo, es una esperanza.
  4. Rota: deja los últimos N en la Pi para que no se acumulen sin control.

  Uso
  ---
    powershell -File respaldar.ps1                 # respalda y sube
    powershell -File respaldar.ps1 -SoloLocal      # sin subir (para probar)
    powershell -File respaldar.ps1 -Mantener 5     # cuántos conservar en la Pi

.NOTES
  La Pi NO es un destino ideal (está en la misma red), pero es un equipo distinto:
  ya cubre el caso "se murió el disco de la laptop", que es el riesgo real y
  frecuente. Lo ideal a futuro es un tercer destino fuera de la red (nube).
#>
[CmdletBinding()]
param(
  [switch]$SoloLocal,
  [int]$Mantener = 3,
  # Si no se indica, se deduce: kuway-agente vive al lado de este proyecto, dentro
  # de la carpeta IA. Así el script no lleva rutas absolutas con nombre de usuario
  # (esto se versiona en un repositorio público).
  [string]$PiScript = $env:YOLITIA_PI_SCRIPT,
  [string]$DestinoPi = '/home/kuway/deploy/respaldos-yolitia'
)

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$catalogo  = Split-Path -Parent $scriptDir          # yolitia_catalog
$raiz      = Split-Path -Parent $catalogo           # yolitia

if (-not $PiScript) {
  $ia = Split-Path -Parent $raiz                     # carpeta IA (contiene yolitia y KUWAY)
  $PiScript = Join-Path $ia 'KUWAY\kuway-agente\pi.ps1'
}

function Paso([string]$m) { Write-Host "`n$m" -ForegroundColor Cyan }
function Ok([string]$m)   { Write-Host "  $m" -ForegroundColor Green }
function Dato([string]$m) { Write-Host "  $m" }

# ---------------------------------------------------------------- 1. Armar
Paso '1/5 Empaquetando'

$fecha = Get-Date -Format 'yyyy-MM-dd-HHmm'
$nombre = "yolitia-catalogo-$fecha.tar.gz"
$tmp = Join-Path $env:TEMP "yolitia-respaldo-$fecha"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$tar = Join-Path $tmp $nombre

# Rutas RELATIVAS a la raiz del proyecto, para que se pueda extraer en cualquier
# lado sin adivinar la estructura.
#
# NO se incluye yolitia_catalog/assets/_incoming (39 MB de fotos de ORIGEN): tienen
# licencia de otro autor y se pueden volver a bajar de MakerWorld. Lo que no se
# puede volver a bajar es el trabajo de curacion.
$rutas = @(
  'yolitia_catalog/data',
  'yolitia_catalog/output/ugc',
  'yolitia_catalog/assets/images/productos',
  'yolitia-site/src/data/products.json'
)

foreach ($r in $rutas) {
  if (-not (Test-Path (Join-Path $raiz $r))) { Dato "aviso: no existe $r, se omite" }
}

Push-Location $raiz
try {
  # Un solo tar con varias rutas: todas son relativas a la raiz del proyecto.
  $salida = tar -czf $tar -C $raiz @rutas 2>&1
  if ($LASTEXITCODE -ne 0) {
    Dato ($salida | Out-String)
    throw "tar fallo (codigo $LASTEXITCODE)"
  }
}
finally { Pop-Location }

$mb = [math]::Round((Get-Item $tar).Length / 1MB, 1)
$sha = (Get-FileHash $tar -Algorithm SHA256).Hash.ToLower()
Ok "$nombre  ($mb MB)"
Dato "sha256: $($sha.Substring(0, 32))..."

# ---------------------------------------------------------------- 2. Guardar local
Paso '2/5 Copia local'

$respaldosLocales = Join-Path $raiz 'respaldos'
New-Item -ItemType Directory -Force -Path $respaldosLocales | Out-Null
# Fuera del repositorio en la medida de lo posible; 'respaldos/' está en .gitignore.
$localFinal = Join-Path $respaldosLocales $nombre
Move-Item $tar $localFinal -Force
Ok "guardado en respaldos\$nombre"

if ($SoloLocal) {
  Paso 'Listo (solo local)'
  Dato 'No se subió nada. Quita -SoloLocal para respaldar fuera del equipo.'
  exit 0
}

# ---------------------------------------------------------------- 3. Subir
Paso '3/5 Subiendo a la Pi'
if (-not (Test-Path $PiScript)) { throw "No encuentro $PiScript" }

& powershell -File $PiScript exec "mkdir -p $DestinoPi" | Out-Null
& powershell -File $PiScript push $localFinal "$DestinoPi/$nombre"
$remoto = & powershell -File $PiScript exec "sha256sum $DestinoPi/$nombre" | Out-String
$shaRemoto = ($remoto -split '\s+')[0].Trim().ToLower()

# ---------------------------------------------------------------- 4. Verificar
Paso '4/5 Verificando integridad'
if ($shaRemoto -eq $sha) {
  Ok 'el hash coincide: el respaldo llegó completo'
} else {
  Dato "local : $sha"
  Dato "remoto: $shaRemoto"
  throw 'EL HASH NO COINCIDE. El respaldo NO es de fiar: revisá la conexión y repetí.'
}

# ---------------------------------------------------------------- 5. Rotar
Paso "5/5 Rotando (se conservan los últimos $Mantener)"
$listado = & powershell -File $PiScript exec "ls -1t $DestinoPi/yolitia-catalogo-*.tar.gz 2>/dev/null" | Out-String
$archivos = $listado -split "`n" | Where-Object { $_.Trim() -ne '' } | ForEach-Object { $_.Trim() }

Dato "hay $($archivos.Count) respaldos en la Pi"
if ($archivos.Count -gt $Mantener) {
  $borrar = $archivos | Select-Object -Skip $Mantener
  foreach ($b in $borrar) {
    & powershell -File $PiScript exec "rm -f $b" | Out-Null
    Dato "borrado el más viejo: $(Split-Path $b -Leaf)"
  }
} else {
  Dato 'no hay nada que rotar'
}

Paso 'Respaldo terminado'
Dato "local : respaldos\$nombre"
Dato "remoto: $DestinoPi/$nombre  (verificado por sha256)"
