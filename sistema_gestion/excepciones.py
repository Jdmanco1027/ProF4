import logging


class SistemaSoftwareFJError(Exception):
    """Excepción base para el sistema de Software FJ."""


ErrorSistema = SistemaSoftwareFJError
SoftwareFJError = SistemaSoftwareFJError


class DatoInvalidoError(SistemaSoftwareFJError):
    """Un dato no cumple el formato o las reglas de validación."""


class ValidacionError(DatoInvalidoError):
    """Un dato o parámetro no cumple una regla de validación."""


class ClienteInvalidoError(DatoInvalidoError):
    """Los datos del cliente no son válidos."""


class CorreoInvalidoError(ClienteInvalidoError):
    """El correo del cliente no es válido."""


class TelefonoInvalidoError(ClienteInvalidoError):
    """El teléfono del cliente no es válido."""


class ParametroFaltanteError(SistemaSoftwareFJError):
    """Falta un parámetro obligatorio."""


class OperacionNoPermitidaError(SistemaSoftwareFJError):
    """La operación solicitada no está permitida."""


class ServicioNoDisponibleError(OperacionNoPermitidaError):
    """El servicio no está disponible para la operación."""


class TarifaInvalidaError(DatoInvalidoError):
    """La tarifa del servicio no es válida."""


class ParametroServicioError(ValidacionError):
    """Un parámetro específico del servicio no es válido."""


class ReservaError(SistemaSoftwareFJError):
    """Error relacionado con una reserva."""


class DuracionInvalidaError(ValidacionError, ReservaError):
    """La duración de la reserva no es válida."""


class CostoInvalidoError(ReservaError):
    """El costo calculado para una reserva no es válido."""


class CalculoInconsistenteError(CostoInvalidoError):
    """El resultado de un cálculo no es coherente."""


ErrorValidacion = ValidacionError
ErrorOperacion = OperacionNoPermitidaError
ErrorServicioNoDisponible = ServicioNoDisponibleError
ErrorEstadoReserva = OperacionNoPermitidaError
ErrorProcesamientoReserva = CostoInvalidoError


def _logger() -> logging.Logger:
    return logging.getLogger("sistema_software_fj")


def registrar_evento(mensaje: str) -> None:
    _logger().info(mensaje)


def registrar_error(mensaje: str, error: Exception | None = None) -> None:
    if error is None:
        _logger().error(mensaje)
    else:
        _logger().error(
            "%s | Detalle: %s: %s",
            mensaje,
            type(error).__name__,
            error,
            exc_info=error.__traceback__ is not None,
        )
