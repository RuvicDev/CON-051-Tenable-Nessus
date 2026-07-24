"""Validación local del conector tenable: ejercita las 3 capacidades.

Uso:
    python validate_local.py

Requiere las variables RUVIC_TENABLE_* exportadas en el entorno, y edita
ASSET_ID / SCAN_ID abajo con valores reales de tu cuenta de prueba.
"""

from ruvic_tenable_connector import TenableClient, setup_logging

ASSET_ID = "REEMPLAZA-CON-UN-UUID-DE-ACTIVO-REAL"
SCAN_ID = 1  # REEMPLAZA con un ID de escaneo real, ya completado

setup_logging("INFO")
client = TenableClient()

print("== 1. Listar vulnerabilidades de un activo ==")
vulns = client.list_vulnerabilities_by_asset(ASSET_ID)
for v in vulns[:5]:
    print(f"  {v.get('plugin_name')} ({v.get('severity')}) x{v.get('count')}")

print("== 2. Consultar escaneo ==")
scan = client.get_scan(SCAN_ID)
print(f"  status={scan['info'].get('status')}")

print("== 3. Exportar resultados del escaneo ==")
content = client.export_scan_results(SCAN_ID, export_format="csv")
print(f"  {len(content)} bytes descargados")

print("\nTodo OK: list_vulnerabilities_by_asset, get_scan y export_scan_results funcionan.")
