"""Prueba de conexión estándar del conector tenable.

Firma estándar Ruvic: def test_connection() -> tuple[bool, str]
- Lee la configuración EXCLUSIVAMENTE de las env vars RUVIC_TENABLE_*.
- Nunca lanza excepciones; retorna (ok, mensaje).

Ejecutable también como script para pruebas locales:
    python test_connection.py
"""

from __future__ import annotations


def test_connection() -> tuple[bool, str]:
    """Conecta a Tenable y consulta la sesión actual usando las env vars
    RUVIC_TENABLE_*."""
    try:
        from ruvic_tenable_connector import (
            TenableAuthError,
            TenableClient,
            TenableDataError,
            TenableNetworkError,
        )
    except ImportError:
        return (
            False,
            "La librería ruvic-tenable-connector no está instalada. "
            "Instala con: pip install git+https://github.com/Dgirto/"
            "Tenable-Nessus.git#subdirectory=lib",
        )

    try:
        client = TenableClient()  # valida que existan las env vars
    except ValueError as exc:
        return False, str(exc)

    try:
        client.ping()
    except TenableAuthError as exc:
        return False, f"Autenticación fallida: {exc}"
    except TenableNetworkError as exc:
        return False, f"Error de red: {exc}"
    except TenableDataError as exc:
        return False, f"Error de datos: {exc}"
    except Exception as exc:  # red de seguridad: jamás propagar
        return False, f"Error inesperado: {exc}"

    return (
        True,
        f"Conexión exitosa a Tenable ({client.config.base_url})",
    )


if __name__ == "__main__":
    ok, message = test_connection()
    print(f"{'OK' if ok else 'FALLO'}: {message}")
    raise SystemExit(0 if ok else 1)
