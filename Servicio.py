"""Clase abstracta servicio de Software FJ
Aqui definire el contrato común o poliformismo que cumpliran todos los
servicios especializados, como por ejemplo:
validar parametros, calcular costos y describirse
se centralizara las validaciones, descuentos e impuestos para evitar
la duplicidad logica en clases hijas.
"""

import logging #Registro de eventos y errores
import math #Detectamos resultados no finitos como NaN, Inf, -Inf
from abc import ABC, abstractmethod

from entidad import Entidad  # Clase abstracta general del sistema
from excepciones import (  # Excepciones personalizadas del sistema
    CalculoInconsistenteError,
    ParametroFaltanteError,
    ServicioNoDisponibleError,
    SoftwareFJError,
    ValidacionError,
)

logger = logging.getLogger(__name__)  # Configuración del logger para esta clase

class Servicio(Entidad, ABC):
    #Servicio generico de Software FJ, que implementa la
    #clase abstracta Entidad y define el contrato para todos los
    #servicios especializados.

    IVA = 0.19  # Tasa por defecto del IVA al 19%
    UNIDAD_DURACION = "horas"
    # Unidad de medida por defecto para la duración de los servicios

    # Descuentos con nombre que el cliente puede solicitar por código
    DESCUENTOS = {
        "ESTUDIANTE": 0.15,  # 15% de descuento para estudiantes
        "COPORATIVO": 0.10,  # 10% de descuento para corporativos
        "FRECUENTE": 0.05,  # 5% de descuento para clientes frecuentes
    }
    DESCUENTOS_NOMBRADOS = DESCUENTOS

    def __init__(self, nombre, tarifa_base, disponible=True):
        super().__init__()  # Asigna un ID unico a la instancia de Servicio
        self._nombre = self._validar_texto(nombre, "nombre")
        self.tarifa_base = self._validar_numero(
            tarifa_base, "tarifa_base", minimo=0, estricto=True
        )
        self.disponible = self._validar_booleano(disponible, "disponible")

    # -------------------------------------------
    # Propiedades (Encapsulación de atributos)
    # -------------------------------------------

    @property
    def nombre(self):
        """Obtiene el nombre del servicio."""
        return self._nombre

    @property
    def tarifa_base(self):
        """Obtiene la tarifa base del servicio."""
        return self._tarifa_base

    @tarifa_base.setter
    def tarifa_base(self, valor):
        self._tarifa_base = self._validar_numero(
            valor, "tarifa_base", minimo=0, estricto=True
        )

    @property
    def disponible(self):
        """Obtiene el estado de disponibilidad del servicio."""
        return self._disponible

    @disponible.setter
    def disponible(self, valor):
        self._disponible = self._validar_booleano(valor, "disponible")
        logger.info(
            "Servicio '%s' disponibilidad establecida a: %s",
            self.nombre,
            self._disponible,
        )


 # ------------------------------------------------------------------
 # Validaciones reutilizables (las usan las clases hijas)
 # ------------------------------------------------------------------
    @staticmethod
    def _validar_texto(valor, campo):
        # Valida que `valor` sea un texto no vacío. Devuelve el texto limpio (sin espacios al inicio o final).
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, str) or not valor.strip():
            raise ValidacionError(f"'{campo}' debe ser un texto no vacío.")
        return valor.strip()

    @staticmethod
    def _validar_booleano(valor, campo):
        # Valida que `valor` sea estrictamente True o False.
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, bool):
            raise ValidacionError(f"'{campo}' debe ser booleano (True/False).")
        return valor

    @staticmethod
    def _validar_numero(valor, campo, minimo=None, maximo=None, estricto=False):
        #Valida un número real dentro de un rango. estricto=True hace que `minimo` sea excluyente (valor > minimo).

        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        # bool es subclase de int, por eso se excluye de forma explícita
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise ValidacionError(f"'{campo}' debe ser numérico, no {type(valor).__name__}.")
        if math.isnan(valor) or math.isinf(valor):
            raise ValidacionError(f"'{campo}' no puede ser NaN ni infinito.")
        if minimo is not None:
            if estricto and valor <= minimo:
                raise ValidacionError(f"'{campo}' debe ser mayor que {minimo}.")
            if not estricto and valor < minimo:
                raise ValidacionError(f"'{campo}' debe ser al menos {minimo}.")
        if maximo is not None and valor > maximo:
            raise ValidacionError(f"'{campo}' no puede superar {maximo}.")
        return valor

    @staticmethod
    def _validar_entero(valor, campo, minimo=None, maximo=None):
        """Valida un entero (no bool) dentro de un rango."""
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
    def _validar_duracion(cls, duracion, minimo, maximo, paso=None):
        """Valida la duración: rango permitido y, opcionalmente, múltiplo de `paso`."""
        cls._validar_numero(duracion, "duracion", minimo=minimo, maximo=maximo)
        if paso:
            # Se compara con tolerancia para evitar errores de coma flotante
            if abs(duracion / paso - round(duracion / paso)) > 1e-9:
                raise ValidacionError(
                    f"'duracion' debe ser múltiplo de {paso} {cls.UNIDAD_DURACION}."
                )
        return duracion

    @staticmethod
    def _rechazar_opciones_desconocidas(otros):
        """Falla si llegan opciones que el servicio no reconoce."""
        if otros:
            raise ValidacionError(
                f"Opciones no reconocidas: {', '.join(sorted(otros))}."
            )

    @staticmethod
    def _validar_opcion(valor, campo, permitidas):
        """Valida que `valor` esté dentro de un conjunto de textos permitidos."""
        if valor is None:
            raise ParametroFaltanteError(f"Falta el parámetro '{campo}'.")
        if not isinstance(valor, str) or valor.strip().lower() not in permitidas:
            raise ValidacionError(
                f"'{campo}' debe ser uno de: {', '.join(sorted(permitidas))}."
            )
        return valor.strip().lower()

    # ------------------------------------------------------------------
    # Contrato abstracto (cada servicio lo implementa a su manera)
    # ------------------------------------------------------------------
    @abstractmethod
    def validar_parametros(self, duracion, **opciones):
        """Valida duración y opciones propias. Lanza ValidacionError si falla."""

    @abstractmethod
    def calcular_costo(self, duracion, **opciones) -> float:
        """
        Calcula el costo base del servicio para la duración dada.

        Parámetros:
            duracion (float): Duración del servicio en la unidad definida por UNIDAD_DURACION.
            **opciones: Opciones adicionales específicas del servicio.

        Devuelve:
            float: Costo base (sin aplicar descuentos ni impuestos).

        Lanza:
            ValidacionError: Si los parámetros no son válidos.
        """
        """Costo base (sin descuento ni impuesto) para la duración dada."""

    @abstractmethod
    def describir(self) -> str:
        """Descripción legible del servicio."""

    def descuento_por_defecto(self, duracion) -> float:
        """Descuento automático según la duración (las hijas pueden sobrescribirlo)."""
        return 0.0

    # ------------------------------------------------------------------
    # Descuentos e impuestos (resolución polimórfica por tipo de dato)
    # ------------------------------------------------------------------
    def _resolver_descuento(self, descuento, duracion) -> float:
        """Convierte el descuento recibido en una tasa entre 0 y 1.

        Admite tres variantes (sobrecarga por tipo de argumento):
          - None          -> descuento automático del servicio
          - float/int     -> fracción entre 0 y 1 (0.10 = 10 %)
          - str           -> código de descuento con nombre (p. ej. "ESTUDIANTE")
        """
        if descuento is None:
            return self.descuento_por_defecto(duracion)
        if isinstance(descuento, str):
            codigo = descuento.strip().upper()
            if codigo not in self.DESCUENTOS_NOMBRADOS:
                raise ValidacionError(f"Código de descuento desconocido: '{descuento}'.")
            return self.DESCUENTOS_NOMBRADOS[codigo]
        return self._validar_numero(descuento, "descuento", minimo=0, maximo=1)

    def _resolver_impuesto(self, impuesto):
        """Devuelve la tasa de impuesto: IVA por defecto o una tasa válida 0-1."""
        if impuesto is None:
            return self.IVA
        return self._validar_numero(impuesto, "impuesto", minimo=0, maximo=1)

    # ------------------------------------------------------------------
    # Cálculo de costos (métodos sobrecargados mediante parámetros opcionales)
    # ------------------------------------------------------------------
    def desglose_costo(self, duracion, descuento=None, impuesto=None, **opciones):
        """Devuelve el detalle completo del cálculo como diccionario.

        Usa try/except/else/finally y encadenamiento de excepciones:
        cualquier error inesperado se convierte en CalculoInconsistenteError
        conservando la causa original (`raise ... from`).
        """
        try:
            # 1) El servicio debe estar disponible
            if not self._disponible:
                raise ServicioNoDisponibleError(
                    f"El servicio '{self._nombre}' no está disponible."
                )
            # 2) Validar parámetros propios del servicio
            self.validar_parametros(duracion, **opciones)
            # 3) Calcular costo base, descuento e impuesto
            base = self.calcular_costo(duracion, **opciones)
            tasa_descuento = self._resolver_descuento(descuento, duracion)
            tasa_impuesto = self._resolver_impuesto(impuesto)
            valor_descuento = base * tasa_descuento
            subtotal = base - valor_descuento
            valor_impuesto = subtotal * tasa_impuesto
            total = subtotal + valor_impuesto
            # 4) Verificar que el resultado sea coherente
            if math.isnan(total) or math.isinf(total) or total < 0:
                raise CalculoInconsistenteError(f"Total inconsistente: {total}.")
        except SoftwareFJError as exc:
            # Errores propios: se registran y se propagan sin alterarlos
            logger.error("Error calculando costo de '%s': %s", self._nombre, exc)
            raise
        except (TypeError, ArithmeticError) as exc:
            # Errores inesperados: se encadenan a una excepción del dominio
            logger.error("Fallo inesperado en '%s': %r", self._nombre, exc)
            raise CalculoInconsistenteError(
                f"No fue posible calcular el costo de '{self._nombre}'."
            ) from exc
        else:
            # Solo se ejecuta si no hubo ninguna excepción
            logger.info("Costo calculado para '%s': total=%.2f", self._nombre, total)
            return {
                "base": round(base, 2),
                "tasa_descuento": tasa_descuento,
                "descuento": round(valor_descuento, 2),
                "subtotal": round(subtotal, 2),
                "tasa_impuesto": tasa_impuesto,
                "impuesto": round(valor_impuesto, 2),
                "total": round(total, 2),
            }
        finally:
            # Se ejecuta siempre, haya o no error
            logger.debug("Fin del cálculo de costo para '%s'.", self._nombre)

    def calcular_costo_total(self, duracion, descuento=None, impuesto=None, **opciones):
        """Costo final con descuento e impuesto (ambos opcionales)."""
        return self.desglose_costo(duracion, descuento, impuesto, **opciones)["total"]

    def costo_con_impuesto(self, duracion, impuesto=None, **opciones):
        """Variante: solo impuesto, sin descuento alguno."""
        return self.calcular_costo_total(duracion, 0.0, impuesto, **opciones)

    def costo_con_descuento(self, duracion, descuento, **opciones):
        """Variante: descuento explícito (fracción o código) más IVA por defecto."""
        return self.calcular_costo_total(duracion, descuento, None, **opciones)

    def __repr__(self):
        # Representación técnica útil para depurar
        return (
            f"{type(self).__name__}(id={self.id}, nombre={self._nombre!r}, "
            f"tarifa_base={self._tarifa_base}, disponible={self._disponible})"
        )
