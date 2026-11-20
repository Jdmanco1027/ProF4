import logging
from enum import Enum
from typing import Any, Mapping

from sistema_gestion.cliente import Cliente
from sistema_gestion.entidad import Entidad
from sistema_gestion.excepciones import (
    CostoInvalidoError,
    OperacionNoPermitidaError,
    ReservaError,
    SistemaSoftwareFJError,
)
from sistema_gestion.servicio import Servicio


class EstadoReserva(Enum):
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"
    PROCESADA = "procesada"


class Reserva(Entidad):
    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        parametros_servicio: Mapping[str, Any] | None = None,
    ) -> None:
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise ReservaError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise ReservaError("La reserva requiere un servicio válido.")
        if parametros_servicio is not None and not isinstance(
            parametros_servicio, Mapping
        ):
            raise ReservaError(
                "Los parámetros del servicio deben ser un diccionario."
            )
        self._cliente = cliente
        self._servicio = servicio
        self._duracion = duracion
        self._parametros_servicio = dict(parametros_servicio or {})
        self._estado = EstadoReserva.PENDIENTE
        self._monto: float | None = None
        self.validar()

    @property
    def cliente(self) -> Cliente:
        return self._cliente

    @property
    def servicio(self) -> Servicio:
        return self._servicio

    @property
    def duracion(self) -> float:
        return self._duracion

    @property
    def estado(self) -> EstadoReserva:
        return self._estado

    @property
    def monto(self) -> float | None:
        return self._monto

    def validar(self) -> bool:
        self._cliente.validar()
        self._servicio.validar()
        self._servicio.validar_parametros(
            self._duracion, **self._parametros_servicio
        )
        return True

    def obtener_resumen(self) -> str:
        monto = "pendiente de cálculo" if self.monto is None else f"${self.monto:.2f}"
        return (
            f"Reserva [{self.id_entidad}] - {self.cliente.nombre} | "
            f"{self.servicio.nombre} | Duración: {self.duracion} "
            f"{self.servicio.UNIDAD_DURACION} | Estado: {self.estado.value} | "
            f"Monto: {monto}"
        )

    def confirmar(
        self,
        descuento: str | float | None = None,
        impuesto: float | None = None,
    ) -> float:
        if self.estado is not EstadoReserva.PENDIENTE:
            raise OperacionNoPermitidaError(
                f"No se puede confirmar una reserva {self.estado.value}."
            )
        try:
            monto = self.servicio.calcular_costo_total(
                self.duracion,
                descuento=descuento,
                impuesto=impuesto,
                **self._parametros_servicio,
            )
            if (
                isinstance(monto, bool)
                or not isinstance(monto, (int, float))
                or monto < 0
            ):
                raise CostoInvalidoError(
                    "El servicio devolvió un costo inconsistente."
                )
        except SistemaSoftwareFJError as exc:
            raise CostoInvalidoError(
                f"No fue posible confirmar la reserva: {exc}"
            ) from exc
        except (TypeError, ArithmeticError, ValueError) as exc:
            raise CostoInvalidoError(
                f"No fue posible confirmar la reserva: {exc}"
            ) from exc
        self._monto = float(monto)
        self._estado = EstadoReserva.CONFIRMADA
        logging.getLogger("sistema_software_fj").info(
            "Reserva %s confirmada por $%.2f.", self.id_entidad, self.monto
        )
        return self._monto

    def cancelar(self) -> None:
        if self.estado not in (EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA):
            raise OperacionNoPermitidaError(
                f"No se puede cancelar una reserva {self.estado.value}."
            )
        self._estado = EstadoReserva.CANCELADA
        logging.getLogger("sistema_software_fj").info(
            "Reserva %s cancelada.", self.id_entidad
        )

    def procesar(self) -> float:
        if self.estado is not EstadoReserva.CONFIRMADA or self.monto is None:
            raise OperacionNoPermitidaError(
                "Solo se puede procesar una reserva confirmada."
            )
        self._estado = EstadoReserva.PROCESADA
        logging.getLogger("sistema_software_fj").info(
            "Reserva %s procesada.", self.id_entidad
        )
        return self.monto
