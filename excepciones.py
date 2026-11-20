import logging

# Configuración del archivo de logs
logging.basicConfig(
    filename="sistema.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

def registrar_evento(mensaje: str):
    logging.info(mensaje)

def registrar_error(mensaje: str, error: Exception = None):
    if error:
        logging.error(f"{mensaje} | Detalle: {type(error).__name__}: {error}")
    else:
        logging.error(mensaje)

class SistemaSoftwareFJError(Exception):
    """Excepción base para todo el sistema de Software FJ."""
    pass

class DatoInvalidoError(SistemaSoftwareFJError):
    """Se lanza cuando un dato no cumple el formato o las reglas de validación."""
    pass

class ParametroFaltanteError(SistemaSoftwareFJError):
    """Se lanza cuando falta un parámetro obligatorio o está vacío."""
    pass

class OperacionNoPermitidaError(SistemaSoftwareFJError):
    """Se lanza cuando se intenta ejecutar una acción inválida sobre una entidad."""
    pass