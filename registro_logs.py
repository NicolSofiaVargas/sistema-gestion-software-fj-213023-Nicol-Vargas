# registro_logs.py
"""Manejo de archivo de logs para eventos y errores en Software FJ."""

import logging
from pathlib import Path


def obtener_logger(nombre_archivo: str = "eventos_software_fj.log") -> logging.Logger:
    """Configura y devuelve un logger que escribe en archivo .log y en consola."""
    ruta_log = Path(__file__).resolve().parent / nombre_archivo
    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita que se dupliquen los mensajes si se llama más de una vez
    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler_archivo = logging.FileHandler(ruta_log, mode="a", encoding="utf-8")
        handler_archivo.setLevel(logging.INFO)
        handler_archivo.setFormatter(formato)

        handler_consola = logging.StreamHandler()
        handler_consola.setLevel(logging.INFO)
        handler_consola.setFormatter(formato)

        logger.addHandler(handler_archivo)
        logger.addHandler(handler_consola)

    return logger