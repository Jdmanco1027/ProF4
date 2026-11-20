from abc import ABC, abstractmethod
from datetime import datetime
from excepciones import ParametroFaltanteError, DatoInvalidoError

class Entidad(ABC):
    """Clase abstracta base para entidades generales de Software FJ."""

    def __init__(self, id_entidad: str):
        self.id_entidad = id_entidad
        self._fecha_registro = datetime.now()
        self._activo = True

    @property
    def id_entidad(self) -> str:
        return self._id_entidad

    @id_entidad.setter
    def id_entidad(self, valor: str):
        if not valor or not isinstance(valor, str) or not valor.strip():
            raise ParametroFaltanteError("El ID de la entidad es obligatorio y no puede estar vacío.")
        if len(valor.strip()) < 3:
            raise DatoInvalidoError("El ID de la entidad debe tener al menos 3 caracteres.")
        self._id_entidad = valor.strip()

    @property
    def fecha_registro(self) -> datetime:
        return self._fecha_registro

    @property
    def activo(self) -> bool:
        return self._activo

    def desactivar(self):
        self._activo = False

    def activar(self):
        self._activo = True

    @abstractmethod
    def validar(self) -> bool:
        """Valida la integridad de los datos de la entidad."""
        pass

    @abstractmethod
    def obtener_resumen(self) -> str:
        """Devuelve una descripción legible de la entidad."""
        pass