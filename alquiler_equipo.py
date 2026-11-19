"""Servicio especializado de alquiler de equipos de Software FJ.

Calcula el costo del alquiler según la duración, la cantidad y el seguro.
"""

from Servicio import Servicio  # Clase abstracta de la que hereda


class AlquilerEquipo(Servicio):
    """Alquiler de equipos cobrado por día y por unidad.

    Opciones del cálculo:
        cantidad: unidades a alquilar; no puede superar el stock disponible.
        con_seguro: agrega un recargo al costo del alquiler.
    """

    # ------------------------------------------------------------------
    # Parámetros propios del alquiler
    # ------------------------------------------------------------------
    UNIDAD_DURACION = "días"
    DIAS_MIN = 1  # Duración mínima del alquiler
    DIAS_MAX = 30  # Duración máxima del alquiler
    RECARGO_SEGURO = 0.05  # Recargo del 5 % si se contrata seguro

    def __init__(self, nombre, tarifa_dia, tipo_equipo, stock, disponible=True):
        # Inicializa y valida los atributos comunes definidos por Servicio.
        super().__init__(nombre, tarifa_dia, disponible)
        self._tipo_equipo = self._validar_texto(tipo_equipo, "tipo_equipo")
        self._stock = self._validar_entero(stock, "stock", minimo=1)

    # ------------------------------------------------------------------
    # Propiedades (Encapsulación de atributos)
    # ------------------------------------------------------------------
    @property
    def tipo_equipo(self):
        """Obtiene el tipo de equipo alquilado."""
        return self._tipo_equipo

    @property
    def stock(self):
        """Obtiene las unidades disponibles para alquilar."""
        return self._stock

    # ------------------------------------------------------------------
    # Validación de parámetros propios
    # ------------------------------------------------------------------
    def validar_parametros(
        self, duracion, cantidad=1, con_seguro=False, **otros
    ):
        """Valida la duración, la cantidad de equipos y el seguro."""
        self._rechazar_opciones_desconocidas(otros)
        # La duración se expresa en días completos.
        self._validar_duracion(duracion, self.DIAS_MIN, self.DIAS_MAX, paso=1)
        self._validar_entero(cantidad, "cantidad", minimo=1, maximo=self._stock)
        self._validar_booleano(con_seguro, "con_seguro")

    # ------------------------------------------------------------------
    # Cálculo de costos
    # ------------------------------------------------------------------
    def calcular_costo(
        self, duracion, cantidad=1, con_seguro=False, **otros
    ) -> float:
        """Calcula el costo del alquiler según duración, cantidad y seguro.

        Devuelve:
            float: Costo del alquiler antes de aplicar descuentos e impuestos.
        """
        costo = self._tarifa_base * duracion * cantidad
        if con_seguro:
            costo += costo * self.RECARGO_SEGURO
        return costo

    # ------------------------------------------------------------------
    # Descuentos por duración
    # ------------------------------------------------------------------
    def descuento_por_defecto(self, duracion):
        """Devuelve un descuento según la duración del alquiler."""
        if duracion >= 15:
            return 0.15
        if duracion >= 7:
            return 0.10
        return 0.0

    def describir(self) -> str:
        """Devuelve una descripción legible del alquiler."""
        estado = "disponible" if self._disponible else "no disponible"
        return (
            f"Alquiler de {self._tipo_equipo} '{self._nombre}' "
            f"({self._stock} unidades), ${self._tarifa_base:,.0f} por día, {estado}."
        )
