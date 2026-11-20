import re

from sistema_gestion.entidad import Entidad
from sistema_gestion.excepciones import (
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    registrar_error,
    registrar_evento,
)


class Cliente(Entidad):
    def __init__(
        self,
        id_cliente: str,
        nombre: str,
        documento: str,
        correo: str,
        telefono: str,
    ) -> None:
        try:
            super().__init__(id_cliente)
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
            self._historial_reservas: list[object] = []
            self.validar()
            registrar_evento(
                f"Cliente registrado correctamente: {self.nombre} "
                f"(ID: {self.id_entidad})"
            )
        except (DatoInvalidoError, ParametroFaltanteError) as exc:
            registrar_error(f"Fallo al crear cliente '{nombre}'", exc)
            raise DatoInvalidoError(
                f"No se pudo registrar el cliente '{nombre}'."
            ) from exc

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if len(valor.strip()) < 3 or any(char.isdigit() for char in valor):
            raise DatoInvalidoError(
                f"Nombre inválido '{valor}': debe tener al menos 3 letras y sin números."
            )
        self._nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError(
                "El documento de identidad es obligatorio."
            )
        limpio = valor.strip()
        if not limpio.isdigit() or not 6 <= len(limpio) <= 12:
            raise DatoInvalidoError(
                f"Documento inválido '{valor}': debe contener entre 6 y 12 dígitos."
            )
        self._documento = limpio

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError(
                "El correo electrónico es obligatorio."
            )
        limpio = valor.strip()
        if not re.fullmatch(r"[\w.-]+@[\w.-]+\.\w{2,}", limpio):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = limpio.lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El teléfono es obligatorio.")
        limpio = valor.strip()
        if not limpio.isdigit() or not 7 <= len(limpio) <= 15:
            raise DatoInvalidoError(
                f"Teléfono inválido '{valor}': debe tener entre 7 y 15 dígitos."
            )
        self._telefono = limpio

    @property
    def historial_reservas(self) -> list[object]:
        return list(self._historial_reservas)

    def agregar_reserva(self, reserva: object) -> None:
        if not self.activo:
            error = OperacionNoPermitidaError(
                f"El cliente {self.nombre} está inactivo y no puede reservar."
            )
            registrar_error("Intento de reserva con cliente inactivo", error)
            raise error
        if reserva is None:
            raise ParametroFaltanteError(
                "La reserva a asociar no puede ser None."
            )
        self._historial_reservas.append(reserva)
        registrar_evento(
            f"Reserva asociada al cliente {self.nombre} "
            f"(ID: {self.id_entidad})"
        )

    def validar(self) -> bool:
        if not all(
            (
                self.id_entidad,
                self.nombre,
                self.documento,
                self.correo,
                self.telefono,
            )
        ):
            raise ParametroFaltanteError(
                "Faltan datos obligatorios en el cliente."
            )
        return True

    def obtener_resumen(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (
            f"Cliente [{self.id_entidad}] - {self.nombre} | "
            f"Doc: {self.documento} | Correo: {self.correo} | "
            f"Tel: {self.telefono} | Estado: {estado}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()
