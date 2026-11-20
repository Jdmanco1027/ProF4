from abc import ABC, abstractmethod
from datetime import datetime

from sistema_gestion.excepciones import DatoInvalidoError, ParametroFaltanteError


class Entidad(ABC):
    def __init__(self, id_entidad: str) -> None:
        self.id_entidad = id_entidad
        self._fecha_registro = datetime.now()
        self._activo = True

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @id_entidad.setter
    def id_entidad(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError(
                "El ID de la entidad es obligatorio y no puede estar vacío."
            )
        valor = valor.strip()
        if len(valor) < 3:
            raise DatoInvalidoError(
                "El ID de la entidad debe tener al menos 3 caracteres."
            )
        self._id_entidad = valor

    @property
    def fecha_registro(self) -> datetime:
        return self._fecha_registro

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self) -> None:
        self._activo = False

    def activar(self) -> None:
        self._activo = True

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de los datos de la entidad."""

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Devuelve una descripción legible de la entidad."""
