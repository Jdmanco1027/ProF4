from sistema_gestion.servicio import Servicio


class ReservaSala(Servicio):
    UNIDAD_DURACION = "horas"
    HORAS_MIN = 1
    HORAS_MAX = 12
    RECARGO_PROYECTOR_HORA = 15000
    HORAS_DESCUENTO = 8
    DESCUENTO_JORNADA = 0.10

    def __init__(
        self,
        nombre: str,
        tarifa_hora: int | float,
        capacidad: int,
        disponible: bool = True,
        *,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(
            nombre, tarifa_hora, disponible, id_entidad=id_entidad
        )
        self._capacidad = self._validar_entero(capacidad, "capacidad", minimo=1)

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_parametros(
        self,
        duracion: float,
        personas: int = 1,
        con_proyector: bool = False,
        **otros: object,
    ) -> None:
        self._rechazar_opciones_desconocidas(otros)
        self._validar_duracion(duracion, self.HORAS_MIN, self.HORAS_MAX, paso=1)
        self._validar_entero(
            personas, "personas", minimo=1, maximo=self.capacidad
        )
        self._validar_booleano(con_proyector, "con_proyector")

    def calcular_costo(
        self,
        duracion: float,
        personas: int = 1,
        con_proyector: bool = False,
        **otros: object,
    ) -> float:
        self.validar_parametros(
            duracion,
            personas=personas,
            con_proyector=con_proyector,
            **otros,
        )
        costo = self.tarifa_base * duracion
        if con_proyector:
            costo += self.RECARGO_PROYECTOR_HORA * duracion
        return costo

    def descuento_por_defecto(self, duracion: float) -> float:
        if duracion >= self.HORAS_DESCUENTO:
            return self.DESCUENTO_JORNADA
        return 0.0

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "no disponible"
        return (
            f"Sala '{self.nombre}' (capacidad {self.capacidad} personas), "
            f"${self.tarifa_base:,.0f} por hora, {estado}."
        )
