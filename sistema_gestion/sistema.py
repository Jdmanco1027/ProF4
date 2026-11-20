from typing import Any, Mapping
from uuid import uuid4

from sistema_gestion.cliente import Cliente
from sistema_gestion.excepciones import (
    ClienteInvalidoError,
    OperacionNoPermitidaError,
    ParametroServicioError,
)
from sistema_gestion.reserva import Reserva
from sistema_gestion.servicio import Servicio


class SistemaGestion:
    def __init__(self) -> None:
        self._clientes: list[Cliente] = []
        self._servicios: list[Servicio] = []
        self._reservas: list[Reserva] = []

    @property
    def clientes(self) -> tuple[Cliente, ...]:
        return tuple(self._clientes)

    @property
    def servicios(self) -> tuple[Servicio, ...]:
        return tuple(self._servicios)

    @property
    def reservas(self) -> tuple[Reserva, ...]:
        return tuple(self._reservas)

    def registrar_cliente(self, cliente: Cliente) -> Cliente:
        if not isinstance(cliente, Cliente):
            raise ClienteInvalidoError("Solo se pueden registrar objetos Cliente.")
        cliente.validar()
        if any(actual.correo == cliente.correo for actual in self._clientes):
            raise OperacionNoPermitidaError(
                f"Ya existe un cliente con el correo {cliente.correo}."
            )
        self._clientes.append(cliente)
        return cliente

    def registrar_servicio(self, servicio: Servicio) -> Servicio:
        if not isinstance(servicio, Servicio):
            raise ParametroServicioError(
                "Solo se pueden registrar objetos Servicio."
            )
        servicio.validar()
        self._servicios.append(servicio)
        return servicio

    def crear_reserva(
        self,
        cliente: Cliente,
        servicio: Servicio,
        duracion: float,
        parametros_servicio: Mapping[str, Any] | None = None,
    ) -> Reserva:
        if not any(actual is cliente for actual in self._clientes):
            raise OperacionNoPermitidaError(
                "El cliente no está registrado en el sistema."
            )
        if not any(actual is servicio for actual in self._servicios):
            raise OperacionNoPermitidaError(
                "El servicio no está registrado en el sistema."
            )
        if not cliente.activo:
            raise OperacionNoPermitidaError(
                "Un cliente inactivo no puede crear reservas."
            )
        reserva = Reserva(
            f"RES-{uuid4().hex}",
            cliente,
            servicio,
            duracion,
            parametros_servicio,
        )
        self._reservas.append(reserva)
        cliente.agregar_reserva(reserva)
        return reserva
