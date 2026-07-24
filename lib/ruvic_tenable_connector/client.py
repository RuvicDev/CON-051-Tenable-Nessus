"""Cliente de consulta de solo lectura para Tenable.io (Vulnerability Management).

Capacidades:
- list_vulnerabilities_by_asset(): listar vulnerabilidades detectadas en un activo.
- get_scan():                       consultar el estado/resumen de un escaneo.
- export_scan_results():            exportar y descargar los resultados de un escaneo.

Las credenciales SIEMPRE provienen de variables de entorno RUVIC_TENABLE_*
(ver config.TenableConfig.from_env). Prohibido hardcodearlas.
"""

from __future__ import annotations

import time
from typing import Any

import requests

from .config import TenableConfig
from .exceptions import TenableAuthError, TenableDataError, TenableNetworkError
from .logging_utils import get_logger

_EXPORT_POLL_INTERVAL = 2
_EXPORT_MAX_WAIT = 60


class TenableClient:
    """Cliente de consulta de solo lectura sobre Tenable.io.

    Args:
        config: configuración de conexión. Si se omite, se lee de las
            variables de entorno RUVIC_TENABLE_* (comportamiento
            estándar en el runtime de la plataforma).

    Ejemplo:
        >>> client = TenableClient()  # lee RUVIC_TENABLE_* del entorno
        >>> client.get_scan(123)
        {'info': {'status': 'completed', ...}, ...}
    """

    def __init__(self, config: TenableConfig | None = None) -> None:
        self.config = config or TenableConfig.from_env()
        self._logger = get_logger()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "X-ApiKeys": f"accessKey={self.config.access_key};secretKey={self.config.secret_key}",
                "Accept": "application/json",
            }
        )

    # ------------------------------------------------------------------ #
    # Conexión
    # ------------------------------------------------------------------ #

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.config.base_url}{path}"
        try:
            response = self._session.request(
                method, url, timeout=self.config.connect_timeout, **kwargs
            )
        except requests.exceptions.RequestException as exc:
            raise TenableNetworkError(
                f"No se pudo alcanzar Tenable en {self.config.base_url!r}: {exc}"
            ) from exc

        if response.status_code in (401, 403):
            raise TenableAuthError(
                "Credenciales inválidas o sin permiso suficiente para esta operación."
            )
        if response.status_code == 404:
            raise TenableDataError("El activo/escaneo solicitado no existe.")
        if response.status_code >= 400:
            raise TenableDataError(
                f"Tenable respondió {response.status_code}: {response.text[:300]}"
            )
        return response

    def ping(self) -> bool:
        """Verifica la conexión consultando la sesión actual.

        Returns:
            True si la conexión funciona.

        Raises:
            TenableAuthError / TenableNetworkError / TenableDataError según
            el fallo.
        """
        self._request("GET", "/session")
        self._logger.info("Ping exitoso a Tenable %s", self.config.base_url)
        return True

    # ------------------------------------------------------------------ #
    # Capacidad 1: listar vulnerabilidades por activo
    # ------------------------------------------------------------------ #

    def list_vulnerabilities_by_asset(self, asset_id: str) -> list[dict[str, Any]]:
        """Lista las vulnerabilidades detectadas en un activo.

        Args:
            asset_id: UUID del activo en Tenable.io.

        Returns:
            Lista de dicts, uno por vulnerabilidad (plugin_id, plugin_name,
            severity, count).

        Ejemplo:
            >>> client.list_vulnerabilities_by_asset("a1b2c3d4-...")
            [{'plugin_id': 12345, 'plugin_name': 'OpenSSL...', 'severity': 'high', 'count': 1}]
        """
        asset_id = (asset_id or "").strip()
        if not asset_id:
            raise TenableDataError("asset_id no puede estar vacío.")
        response = self._request("GET", f"/workbenches/asset/{asset_id}/vulnerabilities")
        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        self._logger.info(
            "Se listaron %d vulnerabilidades para el activo %s", len(vulnerabilities), asset_id
        )
        return vulnerabilities

    # ------------------------------------------------------------------ #
    # Capacidad 2: consultar un escaneo
    # ------------------------------------------------------------------ #

    def get_scan(self, scan_id: int | str) -> dict[str, Any]:
        """Consulta el estado y resumen de un escaneo.

        Args:
            scan_id: ID numérico del escaneo.

        Returns:
            Dict con la info del escaneo (incluye "info" con status,
            targets, scan_start, scan_end).

        Ejemplo:
            >>> client.get_scan(123)
            {'info': {'status': 'completed', 'targets': '10.0.0.0/24', ...}, 'hosts': [...]}
        """
        response = self._request("GET", f"/scans/{scan_id}")
        return response.json()

    # ------------------------------------------------------------------ #
    # Capacidad 3: exportar resultados de un escaneo
    # ------------------------------------------------------------------ #

    def export_scan_results(self, scan_id: int | str, export_format: str = "csv") -> bytes:
        """Exporta y descarga los resultados de un escaneo completado.

        Args:
            scan_id: ID numérico del escaneo.
            export_format: "csv", "nessus", "html" o "pdf". Default "csv".

        Returns:
            Contenido del archivo exportado en bytes.

        Ejemplo:
            >>> content = client.export_scan_results(123, "csv")
            >>> open("resultados.csv", "wb").write(content)
        """
        if export_format not in {"csv", "nessus", "html", "pdf"}:
            raise TenableDataError(
                f"export_format {export_format!r} inválido. Usa csv, nessus, html o pdf."
            )
        response = self._request(
            "POST", f"/scans/{scan_id}/export", json={"format": export_format}
        )
        file_id = response.json().get("file")
        if file_id is None:
            raise TenableDataError("Tenable no retornó un file_id para la exportación.")

        waited = 0
        while waited < _EXPORT_MAX_WAIT:
            status_response = self._request("GET", f"/scans/{scan_id}/export/{file_id}/status")
            status = status_response.json().get("status")
            if status == "ready":
                break
            time.sleep(_EXPORT_POLL_INTERVAL)
            waited += _EXPORT_POLL_INTERVAL
        else:
            raise TenableDataError(
                f"La exportación del escaneo {scan_id} no terminó en {_EXPORT_MAX_WAIT}s."
            )

        download_response = self._request(
            "GET", f"/scans/{scan_id}/export/{file_id}/download"
        )
        self._logger.info(
            "Exportación del escaneo %s descargada (%d bytes, formato %s)",
            scan_id,
            len(download_response.content),
            export_format,
        )
        return download_response.content
