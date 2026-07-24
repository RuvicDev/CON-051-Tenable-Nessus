"""Configuración del conector leída desde variables de entorno.

Convención de la plataforma: cada campo del formulario de configuración
llega como variable de entorno {ENV_PREFIX}{CAMPO} en mayúsculas.
Para este conector el prefijo es RUVIC_TENABLE_.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ENV_PREFIX = "RUVIC_TENABLE_"


@dataclass(frozen=True)
class TenableConfig:
    """Parámetros de conexión a Tenable.io / Tenable Vulnerability Management."""

    base_url: str
    access_key: str
    secret_key: str
    connect_timeout: int = 15

    @classmethod
    def from_env(cls) -> "TenableConfig":
        """Construye la configuración desde las variables RUVIC_TENABLE_*.

        Raises:
            ValueError: si falta alguna variable obligatoria.

        Ejemplo:
            >>> config = TenableConfig.from_env()
            >>> config.base_url
            'https://cloud.tenable.com'
        """
        missing = [
            f"{ENV_PREFIX}{name}"
            for name in ("ACCESS_KEY", "SECRET_KEY")
            if not os.environ.get(f"{ENV_PREFIX}{name}")
        ]
        if missing:
            raise ValueError(
                "Faltan variables de entorno del conector tenable: "
                + ", ".join(missing)
                + ". Configura el conector en Settings → Conectores."
            )
        return cls(
            base_url=os.environ.get(f"{ENV_PREFIX}BASE_URL", "https://cloud.tenable.com").rstrip("/"),
            access_key=os.environ[f"{ENV_PREFIX}ACCESS_KEY"],
            secret_key=os.environ[f"{ENV_PREFIX}SECRET_KEY"],
            connect_timeout=int(os.environ.get(f"{ENV_PREFIX}CONNECT_TIMEOUT", "15")),
        )
