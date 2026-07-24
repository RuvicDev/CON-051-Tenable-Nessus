# Conector Tenable / Nessus (CON-051)

Conector Ruvic de consulta de solo lectura para Tenable.io (Vulnerability
Management). Permite listar vulnerabilidades detectadas en un activo,
consultar el estado/resumen de un escaneo, y exportar sus resultados.

## Instalación

```bash
pip install git+https://github.com/Dgirto/Tenable-Nessus.git#subdirectory=lib
```

Python 3.10+. Dependencia única: `requests>=2.31,<3.0`.

## Permisos requeridos en Tenable.io

Genera un par de API Keys dedicado (Settings → My Account → API Keys)
para un usuario con rol de solo lectura:

- Rol de usuario **Basic** o **Standard** (no Administrator).
- Acceso a los grupos de activos/escaneos que quieras consultar (Tenable
  permite restringir la visibilidad por "Access Groups").

El conector no crea, modifica, lanza ni elimina escaneos — solo
consulta datos y exporta resultados ya generados.

## Variables de entorno (`RUVIC_TENABLE_*`)

| Variable | Obligatoria | Descripción |
|----------|-------------|-------------|
| `RUVIC_TENABLE_BASE_URL` | No (default `https://cloud.tenable.com`) | URL base (para instancias autoalojadas) |
| `RUVIC_TENABLE_ACCESS_KEY` | Sí | Access Key |
| `RUVIC_TENABLE_SECRET_KEY` | Sí | Secret Key |
| `RUVIC_TENABLE_CONNECT_TIMEOUT` | No (default `15`) | Timeout de conexión en segundos |

## Pruebas locales

Con una cuenta Tenable.io real (Tenable no es viable en Docker local;
usa el free trial):

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ./lib

export RUVIC_TENABLE_ACCESS_KEY=tu-access-key
export RUVIC_TENABLE_SECRET_KEY=tu-secret-key

python test_connection.py
python validate_local.py
```

`validate_local.py` requiere un `asset_id` y `scan_id` reales de tu
cuenta de prueba — edítalos en el script antes de correrlo. Prueba
también los casos de error (API Keys inválidas, activo/escaneo
inexistente) y verifica que los mensajes sean claros.

## Notas de integración

- Es un conector de **solo lectura**: no lanza, pausa ni elimina
  escaneos, y no modifica configuración de la cuenta.
- `export_scan_results` es asíncrono en la API de Tenable: el conector
  inicia la exportación, sondea el estado cada 2 segundos (hasta 60s en
  total) y descarga el archivo cuando está listo.
- `list_vulnerabilities_by_asset` usa el endpoint de "workbenches", que
  agrega los hallazgos de todos los escaneos recientes sobre ese activo
  (no de un escaneo específico).
