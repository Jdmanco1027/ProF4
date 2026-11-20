"""Servicio especializado de reserva de salas de Software FJ.

Calcula el costo base de reservar una sala según la duración y el uso de
proyector. El total de calcular_costo_total() es un float; por defecto incluye
el descuento automático del servicio y el IVA del 19 %. desglose_costo()
devuelve el detalle como dict.
"""

from Servicio import Servicio  # Clase abstracta de la que hereda


class ReservaSala(Servicio):
    """Reserva de una sala de reuniones cobrada por hora.

    Opciones del cálculo:
        personas: valida el aforo; no modifica la tarifa.
        con_proyector: agrega un recargo por hora de uso.

    El costo base no incluye descuentos ni impuestos. Desde las 8 horas se
    aplica automáticamente un descuento del 10 % al calcular el total.
    """

    # ------------------------------------------------------------------
    # Parámetros propios de la reserva
    # ------------------------------------------------------------------
    UNIDAD_DURACION = "horas"
    HORAS_MIN = 1  # Duración mínima de una reserva
    HORAS_MAX = 12  # Duración máxima de una reserva
    RECARGO_PROYECTOR_HORA = 15000  # Recargo por hora si se usa proyector
    HORAS_DESCUENTO = 8  # Desde estas horas aplica descuento automático
    DESCUENTO_JORNADA = 0.10  # 10 % por reservar una jornada larga

    def __init__(
        self, nombre, tarifa_hora, capacidad, disponible=True, *, id_entidad=None
    ):
        # Inicializa y valida los atributos comunes definidos por Servicio.
        super().__init__(nombre, tarifa_hora, disponible, id_entidad=id_entidad)
        # La capacidad debe ser un entero positivo.
        self._capacidad = self._validar_entero(capacidad, "capacidad", minimo=1)

    # ------------------------------------------------------------------
    # Propiedades (Encapsulación de atributos)
    # ------------------------------------------------------------------
    @property
    def capacidad(self):
        """Obtiene el número máximo de asistentes."""
        return self._capacidad

    # ------------------------------------------------------------------
    # Validación de parámetros propios
    # ------------------------------------------------------------------
    def validar_parametros(
        self, duracion, personas=1, con_proyector=False, **otros
    ):
        """Valida la duración, la cantidad de personas y el proyector."""
        self._rechazar_opciones_desconocidas(otros)
        # La duración se expresa en horas completas.
        self._validar_duracion(duracion, self.HORAS_MIN, self.HORAS_MAX, paso=1)
        # La cantidad de personas no debe superar la capacidad de la sala.
        self._validar_entero(
            personas, "personas", minimo=1, maximo=self._capacidad
        )
        self._validar_booleano(con_proyector, "con_proyector")

    # ------------------------------------------------------------------
    # Cálculo de costos
    # ------------------------------------------------------------------
    def calcular_costo(
        self, duracion, personas=1, con_proyector=False, **otros
    ) -> float:
        """Calcula el costo base según la duración y el uso del proyector.

        Devuelve:
            float: Costo antes de aplicar descuentos e impuestos.
        """
        costo = self._tarifa_base * duracion
        if con_proyector:
            costo += self.RECARGO_PROYECTOR_HORA * duracion
        return costo

    # ------------------------------------------------------------------
    # Descuentos por duración
    # ------------------------------------------------------------------
    def descuento_por_defecto(self, duracion):
        """Devuelve el descuento automático para jornadas largas."""
        return self.DESCUENTO_JORNADA if duracion >= self.HORAS_DESCUENTO else 0.0

    def describir(self) -> str:
        """Devuelve una descripción legible de la reserva."""
        estado = "disponible" if self._disponible else "no disponible"
        return (
            f"Sala '{self._nombre}' (capacidad {self._capacidad} personas), "
            f"${self._tarifa_base:,.0f} por hora, {estado}."
        )
