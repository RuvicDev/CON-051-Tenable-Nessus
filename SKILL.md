---
name: tenable
description: >
  Usa la librería ruvic_tenable_connector para consultar vulnerabilidades
  en Tenable.io en modo solo lectura - listar vulnerabilidades detectadas
  en un activo (list_vulnerabilities_by_asset), consultar el estado y
  resumen de un escaneo (get_scan), y exportar los resultados de un
  escaneo completado (export_scan_results). Úsala cuando el usuario pida
  consultar vulnerabilidades, revisar un escaneo o exportar resultados
  de Tenable/Nessus.
triggers:
- tenable
- nessus
- vulnerabilidades
- escaneo de seguridad
---

# Conector Tenable / Nessus (ruvic_tenable_connector)

Librería Python de solo lectura para Tenable.io. Está **preinstalada en el runtime** cuando el conector está configurado (si no, instálala con `pip install git+https://github.com/Dgirto/Tenable-Nessus.git#subdirectory=lib`).

## Regla crítica de credenciales

El código generado **NUNCA hardcodea credenciales**. Siempre se leen de variables de entorno, disponibles cuando el conector `tenable` está configurado:

| Variable | Contenido |
|----------|-----------|
| `RUVIC_TENABLE_BASE_URL` | (opcional) URL base, default `https://cloud.tenable.com` |
| `RUVIC_TENABLE_ACCESS_KEY` | Access Key |
| `RUVIC_TENABLE_SECRET_KEY` | Secret Key |
| `RUVIC_TENABLE_CONNECT_TIMEOUT` | (opcional) timeout en segundos |

Si estas variables NO existen, el conector no está configurado: no generes código que lo use; indica al usuario que lo configure en **Settings → Conectores**.

## Conexión (siempre igual)

```python
from ruvic_tenable_connector import TenableClient

client = TenableClient()  # lee RUVIC_TENABLE_* del entorno automáticamente
```

## Capacidad 1 — Listar vulnerabilidades de un activo

```python
vulns = client.list_vulnerabilities_by_asset("a1b2c3d4-5678-90ab-cdef-1234567890ab")
for v in vulns:
    print(f"{v['plugin_name']} ({v['severity']}) x{v['count']}")
```

## Capacidad 2 — Consultar un escaneo

```python
scan = client.get_scan(123)
print(scan["info"]["status"])  # "completed", "running", "aborted", etc.
```

## Capacidad 3 — Exportar resultados de un escaneo

```python
content = client.export_scan_results(123, export_format="csv")
with open("resultados.csv", "wb") as f:
    f.write(content)
```

`export_scan_results` inicia la exportación, espera a que Tenable la prepare (hasta 60s) y descarga el archivo. Formatos soportados: `csv`, `nessus`, `html`, `pdf`.

## Manejo de errores

```python
from ruvic_tenable_connector import (
    TenableAuthError, TenableDataError, TenableNetworkError,
)

try:
    scan = client.get_scan(123)
except TenableAuthError:
    print("Credenciales inválidas o sin permiso suficiente")
except TenableNetworkError:
    print("No se pudo alcanzar Tenable — reintenta en unos segundos")
except TenableDataError as e:
    print(f"Error de datos: {e}")  # ej. el activo/escaneo no existe
```

## Buenas prácticas al generar código

1. Lee credenciales SOLO de las variables `RUVIC_TENABLE_*` (el constructor de `TenableClient` ya lo hace).
2. Nunca imprimas `RUVIC_TENABLE_SECRET_KEY` en logs ni en la salida.
3. La librería es de SOLO LECTURA: no intenta lanzar, pausar ni eliminar escaneos.
4. `export_scan_results` puede tardar hasta 60 segundos si Tenable tarda en preparar el archivo — informa al usuario que la operación puede tomar un momento.
5. Antes de exportar un escaneo, verifica con `get_scan` que su estado sea `completed`; exportar un escaneo en curso puede dar resultados parciales.
