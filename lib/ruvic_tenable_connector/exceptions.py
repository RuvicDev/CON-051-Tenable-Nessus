"""Excepciones propias del conector Tenable.

Separan los tres tipos de fallo que el usuario debe distinguir:
autenticación, red/servidor y datos. Nunca exponemos excepciones
crípticas del cliente HTTP subyacente.
"""


class TenableConnectorError(Exception):
    """Error base del conector."""


class TenableAuthError(TenableConnectorError):
    """Credenciales inválidas o permisos insuficientes."""


class TenableNetworkError(TenableConnectorError):
    """No se pudo alcanzar la API de Tenable (red/timeout)."""


class TenableDataError(TenableConnectorError):
    """La operación es válida pero el activo/escaneo es inválido."""
