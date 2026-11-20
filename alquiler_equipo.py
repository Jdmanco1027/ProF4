"""Servicio especializado de alquiler de equipos de Software FJ.

Calcula el costo base del alquiler según duración, unidades y seguro. El total
de calcular_costo_total() es un float; por defecto incluye el descuento
automático del servicio y el IVA del 19 %. desglose_costo() devuelve el detalle
como dict.
"""

from Servicio import Servicio  # Clase abstracta de la que hereda


class AlquilerEquipo(Servicio):
    """Alquiler de equipos cobrado por día y por unidad.

    Opciones del cálculo:
        unidades: multiplica el costo base y no puede superar el stock.
        con_seguro: agrega un recargo del 5 % al costo base.

    El costo base no incluye descuentos ni impuestos. Desde los 7 días se
    aplica automáticamente un descuento del 10 % (15 % desde los 15 días).
    """

    # ------------------------------------------------------------------
    # Parámetros propios del alquiler
    # ------------------------------------------------------------------
    UNIDAD_DURACION = "días"
    DIAS_MIN = 1  # Duración mínima del alquiler
    DIAS_MAX = 30  # Duración máxima del alquiler
    RECARGO_SEGURO = 0.05  # Recargo del 5 % si se contrata seguro

    def __init__(
        self, nombre, tarifa_dia, tipo_equipo, stock, disponible=True, *, id_entidad=None
    ):
        # Inicializa y valida los atributos comunes definidos por Servicio.
        super().__init__(nombre, tarifa_dia, disponible, id_entidad=id_entidad)
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
        self, duracion, unidades=1, con_seguro=False, **otros
    ):
        """Valida la duración, la cantidad de unidades y el seguro."""
        self._rechazar_opciones_desconocidas(otros)
        # La duración se expresa en días completos.
        self._validar_duracion(duracion, self.DIAS_MIN, self.DIAS_MAX, paso=1)
        self._validar_entero(unidades, "unidades", minimo=1, maximo=self._stock)
        self._validar_booleano(con_seguro, "con_seguro")

    # ------------------------------------------------------------------
    # Cálculo de costos
    # ------------------------------------------------------------------
    def calcular_costo(
        self, duracion, unidades=1, con_seguro=False, **otros
    ) -> float:
        """Calcula el costo base según duración, unidades y seguro.

        Devuelve:
            float: Costo antes de aplicar descuentos e impuestos.
        """
        costo = self._tarifa_base * duracion * unidades
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
