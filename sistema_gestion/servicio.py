import logging
import math
from abc import ABC, abstractmethod
from uuid import uuid4

from sistema_gestion.entidad import Entidad
from sistema_gestion.excepciones import (
    CalculoInconsistenteError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    SistemaSoftwareFJError,
    ValidacionError,
)


logger = logging.getLogger(__name__)


class Servicio(Entidad, ABC):
    IVA = 0.19
    UNIDAD_DURACION = "horas"
    DESCUENTOS_NOMBRADOS = {
        "ESTUDIANTE": 0.15,
        "CORPORATIVO": 0.10,
        "COPORATIVO": 0.10,
        "FRECUENTE": 0.05,
    }

    def __init__(
        self,
        nombre: str,
        tarifa_base: int | float,
        disponible: bool = True,
        *,
        id_entidad: str | None = None,
    ) -> None:
        if id_entidad is None:
            id_entidad = f"SRV-{uuid4().hex.upper()}"
        super().__init__(id_entidad)
        self._nombre = self._validar_texto(nombre, "nombre")
        self.tarifa_base = tarifa_base
        self.disponible = disponible

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor: int | float) -> None:
        self._tarifa_base = self._validar_numero(
            valor, "tarifa_base", minimo=0, estricto=True
        )

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        self._disponible = self._validar_booleano(valor, "disponible")
        logger.info(
            "Servicio '%s' disponibilidad establecida a: %s",
            self.nombre,
            self._disponible,
        )

    @staticmethod
    def _validar_texto(valor: object, campo: str) -> str:
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, str) or not valor.strip():
            raise ValidacionError(f"'{campo}' debe ser un texto no vacío.")
        return valor.strip()

    @staticmethod
    def _validar_booleano(valor: object, campo: str) -> bool:
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, bool):
            raise ValidacionError(f"'{campo}' debe ser booleano (True/False).")
        return valor

    @staticmethod
    def _validar_numero(
        valor: object,
        campo: str,
        minimo: float | None = None,
        maximo: float | None = None,
        estricto: bool = False,
    ) -> float:
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValidacionError(
                f"'{campo}' debe ser numérico, no {type(valor).__name__}."
            )
        if not math.isfinite(valor):
            raise ValidacionError(f"'{campo}' no puede ser NaN ni infinito.")
        if minimo is not None:
            if estricto and valor <= minimo:
                raise ValidacionError(f"'{campo}' debe ser mayor que {minimo}.")
            if not estricto and valor < minimo:
                raise ValidacionError(f"'{campo}' debe ser al menos {minimo}.")
        if maximo is not None and valor > maximo:
            raise ValidacionError(f"'{campo}' no puede superar {maximo}.")
        return float(valor)

    @staticmethod
    def _validar_entero(
        valor: object,
        campo: str,
        minimo: int | None = None,
        maximo: int | None = None,
    ) -> int:
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise ValidacionError(f"'{campo}' debe ser un entero.")
        if minimo is not None and valor < minimo:
            raise ValidacionError(f"'{campo}' debe ser al menos {minimo}.")
        if maximo is not None and valor > maximo:
            raise ValidacionError(f"'{campo}' no puede superar {maximo}.")
        return valor

    @classmethod
    def _validar_duracion(
        cls,
        duracion: int | float,
        minimo: float,
        maximo: float,
        paso: float | None = None,
    ) -> float:
        duracion = cls._validar_numero(
            duracion, "duracion", minimo=minimo, maximo=maximo
        )
        if paso and abs(duracion / paso - round(duracion / paso)) > 1e-9:
            raise ValidacionError(
                f"'duracion' debe ser múltiplo de {paso} "
                f"{cls.UNIDAD_DURACION}."
            )
        return duracion

    @staticmethod
    def _rechazar_opciones_desconocidas(opciones: dict[str, object]) -> None:
        if opciones:
            raise ValidacionError(
                f"Opciones no reconocidas: {', '.join(sorted(opciones))}."
            )

    @staticmethod
    def _validar_opcion(
        valor: object, campo: str, permitidas: dict[str, float]
    ) -> str:
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, str) or valor.strip().lower() not in permitidas:
            raise ValidacionError(
                f"'{campo}' debe ser uno de: {', '.join(sorted(permitidas))}."
            )
        return valor.strip().lower()

    def validar(self) -> bool:
        self._validar_texto(self.nombre, "nombre")
        self._validar_numero(
            self.tarifa_base, "tarifa_base", minimo=0, estricto=True
        )
        self._validar_booleano(self.disponible, "disponible")
        return True

    @abstractmethod
    def validar_parametros(self, duracion: float, **opciones: object) -> None:
        """Valida la duración y las opciones propias del servicio."""

    @abstractmethod
    def calcular_costo(self, duracion: float, **opciones: object) -> float:
        """Calcula el costo base antes de descuentos e impuestos."""

    @abstractmethod
    def describir(self) -> str:
        """Devuelve una descripción legible del servicio."""

    def obtener_resumen(self) -> str:
        return self.describir()

    def descuento_por_defecto(self, duracion: float) -> float:
        del duracion
        return 0.0

    def _resolver_descuento(
        self, descuento: str | float | None, duracion: float
    ) -> float:
        if descuento is None:
            return self.descuento_por_defecto(duracion)
        if isinstance(descuento, str):
            codigo = descuento.strip().upper()
            if codigo not in self.DESCUENTOS_NOMBRADOS:
                raise ValidacionError(
                    f"Código de descuento desconocido: '{descuento}'."
                )
            return self.DESCUENTOS_NOMBRADOS[codigo]
        return self._validar_numero(
            descuento, "descuento", minimo=0, maximo=1
        )

    def _resolver_impuesto(self, impuesto: float | None) -> float:
        if impuesto is None:
            return self.IVA
        return self._validar_numero(impuesto, "impuesto", minimo=0, maximo=1)

    def desglose_costo(
        self,
        duracion: float,
        descuento: str | float | None = None,
        impuesto: float | None = None,
        **opciones: object,
    ) -> dict[str, float]:
        try:
            if not self.disponible:
                raise OperacionNoPermitidaError(
                    f"El servicio '{self.nombre}' no está disponible."
                )
            self.validar_parametros(duracion, **opciones)
            base = self.calcular_costo(duracion, **opciones)
            base = self._validar_numero(base, "costo_base", minimo=0)
            tasa_descuento = self._validar_numero(
                self._resolver_descuento(descuento, duracion),
                "descuento_resuelto",
                minimo=0,
                maximo=1,
            )
            tasa_impuesto = self._resolver_impuesto(impuesto)
            valor_descuento = base * tasa_descuento
            subtotal = base - valor_descuento
            valor_impuesto = subtotal * tasa_impuesto
            total = subtotal + valor_impuesto
            if not math.isfinite(total) or total < 0:
                raise CalculoInconsistenteError(
                    f"Total inconsistente: {total}."
                )
        except SistemaSoftwareFJError:
            logger.exception("Error calculando costo del servicio '%s'.", self.nombre)
            raise
        except (TypeError, ArithmeticError, ValueError) as exc:
            logger.exception("Fallo inesperado al calcular el servicio '%s'.", self.nombre)
            raise CalculoInconsistenteError(
                f"No fue posible calcular el costo de '{self.nombre}'."
            ) from exc
        else:
            detalle = {
                "base": round(base, 2),
                "tasa_descuento": tasa_descuento,
                "descuento": round(valor_descuento, 2),
                "subtotal": round(subtotal, 2),
                "tasa_impuesto": tasa_impuesto,
                "impuesto": round(valor_impuesto, 2),
                "total": round(total, 2),
            }
            logger.info(
                "Costo calculado para '%s': total=%.2f",
                self.nombre,
                detalle["total"],
            )
            return detalle
        finally:
            logger.debug("Fin del cálculo de costo para '%s'.", self.nombre)

    def calcular_costo_total(
        self,
        duracion: float,
        descuento: str | float | None = None,
        impuesto: float | None = None,
        **opciones: object,
    ) -> float:
        return self.desglose_costo(
            duracion, descuento, impuesto, **opciones
        )["total"]

    def costo_con_impuesto(
        self, duracion: float, impuesto: float | None = None, **opciones: object
    ) -> float:
        return self.calcular_costo_total(duracion, 0.0, impuesto, **opciones)

    def costo_con_descuento(
        self,
        duracion: float,
        descuento: str | float,
        **opciones: object,
    ) -> float:
        return self.calcular_costo_total(
            duracion, descuento, None, **opciones
        )

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id_entidad}, "
            f"nombre={self.nombre!r}, tarifa_base={self.tarifa_base}, "
            f"disponible={self.disponible})"
        )
