"""Configuracion general del sistema.

Los datos de red y credenciales se leen de variables de entorno; no se
guardan en el codigo fuente.
"""

import os

RUTA_BD = os.environ.get("VIGISALUD_BD", "vigisalud.db")

SERVIDOR_SMTP = os.environ.get("VIGISALUD_SMTP_HOST", "")
PUERTO_SMTP = int(os.environ.get("VIGISALUD_SMTP_PUERTO", "587"))
USUARIO_SMTP = os.environ.get("VIGISALUD_SMTP_USUARIO", "")
CLAVE_SMTP = os.environ.get("VIGISALUD_SMTP_CLAVE", "")
TIEMPO_ESPERA_SMTP = 10

ENFERMEDADES = frozenset({"DENGUE", "IRA", "EDA"})
SEXOS = frozenset({"M", "F"})
CONDICIONES = frozenset({"VIVO", "FALLECIDO"})
TIPOS_DX = frozenset({"CONFIRMADO", "PROBABLE"})

ANIO_ACTUAL = 2026
ANIOS_HISTORICOS = (2021, 2022, 2023, 2024, 2025)
