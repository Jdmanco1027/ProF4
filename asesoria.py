"""Servicio especializado de asesoría de Software FJ.

Calcula el costo de asesorías por hora según el nivel y la modalidad.
"""

from Servicio import Servicio  # Clase abstracta de la que hereda


class Asesoria(Servicio):
    """Asesoría por hora cuyo costo depende del nivel y la modalidad.

    Opciones del cálculo:
        nivel: "junior", "senior" o "experto"; modifica la tarifa por hora.
        modalidad: "virtual" o "presencial"; la modalidad presencial tiene
        un costo adicional.
    """

    # ------------------------------------------------------------------
    # Parámetros propios de la asesoría
    # ------------------------------------------------------------------
    UNIDAD_DURACION = "horas"
    HORAS_MIN = 0.5  # Duración mínima de una asesoría
    HORAS_MAX = 8  # Duración máxima de una asesoría
    PASO_HORAS = 0.5  # La duración se ofrece en bloques de media hora
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}
    MODALIDADES = {"virtual": 1.0, "presencial": 1.2}

    def __init__(self, nombre, tarifa_hora, especialidad, disponible=True):
        # Inicializa y valida los atributos comunes definidos por Servicio.
        super().__init__(nombre, tarifa_hora, disponible)
        self._especialidad = self._validar_texto(especialidad, "especialidad")

    # ------------------------------------------------------------------
    # Propiedades (Encapsulación de atributos)
    # ------------------------------------------------------------------
    @property
    def especialidad(self):
        """Obtiene el área de especialidad de la asesoría."""
        return self._especialidad

    # ------------------------------------------------------------------
    # Validación de parámetros propios
    # ------------------------------------------------------------------
    def validar_parametros(self, duracion, nivel="junior", modalidad="virtual", **otros):
        """Valida la duración, el nivel y la modalidad de la asesoría."""
        self._rechazar_opciones_desconocidas(otros)
        self._validar_duracion(
            duracion, self.HORAS_MIN, self.HORAS_MAX, self.PASO_HORAS
        )
        self._validar_opcion(nivel, "nivel", self.NIVELES)
        self._validar_opcion(modalidad, "modalidad", self.MODALIDADES)

    # ------------------------------------------------------------------
    # Cálculo de costos
    # ------------------------------------------------------------------
    def calcular_costo(
        self, duracion, nivel="junior", modalidad="virtual", **otros
    ) -> float:
        """Calcula el costo base según duración, nivel y modalidad.

        Devuelve:
            float: Costo base antes de aplicar descuentos e impuestos.
        """
        factor_nivel = self.NIVELES[nivel.strip().lower()]
        factor_modalidad = self.MODALIDADES[modalidad.strip().lower()]
        return self._tarifa_base * duracion * factor_nivel * factor_modalidad

    def descuento_por_defecto(self, duracion):
        """Devuelve un descuento del 5 % para asesorías de 5 horas o más."""
        return 0.05 if duracion >= 5 else 0.0

    def describir(self) -> str:
        """Devuelve una descripción legible de la asesoría."""
        estado = "disponible" if self._disponible else "no disponible"
        return (
            f"Asesoría en {self._especialidad} '{self._nombre}', "
            f"${self._tarifa_base:,.0f} por hora (nivel junior), {estado}."
        )
