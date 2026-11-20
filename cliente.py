import re
from Entidad import Entidad
from excepciones import (
    DatoInvalidoError,
    ParametroFaltanteError,
    OperacionNoPermitidaError,
    registrar_evento,
    registrar_error,
)

class Cliente(Entidad):
    """Representa a un cliente de Software FJ con encapsulación y validaciones estrictas."""

    def __init__(self, id_cliente: str, nombre: str, documento: str, correo: str, telefono: str):
        try:
            super().__init__(id_cliente)
            self.nombre = nombre
            self.documento = documento
            self.correo = correo
            self.telefono = telefono
            self._historial_reservas = []
            self.validar()
            registrar_evento(f"Cliente registrado correctamente: {self.nombre} (ID: {self.id_entidad})")
        except (DatoInvalidoError, ParametroFaltanteError) as e:
            registrar_error(f"Fallo al crear cliente '{nombre}'", e)
            raise DatoInvalidoError(f"No se pudo registrar el cliente '{nombre}'.") from e

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El nombre del cliente es obligatorio.")
        if len(valor.strip()) < 3 or any(char.isdigit() for char in valor):
            raise DatoInvalidoError(f"Nombre inválido '{valor}': debe tener al menos 3 letras y sin números.")
        self._nombre = valor.strip()

    @property
    def documento(self) -> str:
        return self._documento

    @documento.setter
    def documento(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El documento de identidad es obligatorio.")
        limpio = valor.strip()
        if not limpio.isdigit() or not (6 <= len(limpio) <= 12):
            raise DatoInvalidoError(f"Documento inválido '{valor}': debe contener entre 6 y 12 dígitos.")
        self._documento = limpio

    @property
    def correo(self) -> str:
        return self._correo

    @correo.setter
    def correo(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El correo electrónico es obligatorio.")
        patron = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        if not re.match(patron, valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El teléfono es obligatorio.")
        limpio = valor.strip()
        if not limpio.isdigit() or not (7 <= len(limpio) <= 15):
            raise DatoInvalidoError(f"Teléfono inválido '{valor}': debe tener entre 7 y 15 dígitos.")
        self._telefono = limpio

    @property
    def historial_reservas(self) -> list:
        return list(self._historial_reservas)

    def agregar_reserva(self, reserva):
        if not self.activo:
            error = OperacionNoPermitidaError(f"El cliente {self.nombre} está inactivo y no puede reservar.")
            registrar_error("Intento de reserva con cliente inactivo", error)
            raise error
        if reserva is None:
            raise ParametroFaltanteError("La reserva a asociar no puede ser None.")
        self._historial_reservas.append(reserva)
        registrar_evento(f"Reserva asociada al cliente {self.nombre} (ID: {self.id_entidad})")

    def validar(self) -> bool:
        if not all([self._id_entidad, self._nombre, self._documento, self._correo, self._telefono]):
            raise ParametroFaltanteError("Faltan datos obligatorios en el cliente.")
        return True

    def obtener_resumen(self) -> str:
        estado = "Activo" if self.activo else "Inactivo"
        return (
            f"Cliente [{self.id_entidad}] - {self.nombre} | Doc: {self.documento} | "
            f"Correo: {self.correo} | Tel: {self.telefono} | Estado: {estado}"
        )

    def __str__(self) -> str:
        return self.obtener_resumen()


# Pruebas rápidas del módulo Rol 1 (se ejecutan solo si corres este archivo directamente)
if __name__ == "__main__":
    clientes = []
    datos_prueba = [
        ("CLI-001", "Laura Gómez", "1053849201", "laura@correo.com", "3104567890"),  # Válido
        ("CLI-002", "Carlos123", "123", "correo-malo", "3001112233"),               # Inválido (nombre y doc)
        ("", "Andrés Pérez", "98765432", "andres@empresa.co", "3159876543"),        # Inválido (ID vacío)
    ]

    for id_c, nom, doc, mail, tel in datos_prueba:
        try:
            nuevo = Cliente(id_c, nom, doc, mail, tel)
        except DatoInvalidoError as err:
            print(f"[ERROR CONTROLADO] {err} -> Causa: {err.__cause__}")
        else:
            clientes.append(nuevo)
            print(f"[OK] {nuevo}")
        finally:
            print("--- Fin de validación de registro ---")