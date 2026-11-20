from sistema_gestion.servicio import Servicio


class Asesoria(Servicio):
    UNIDAD_DURACION = "horas"
    HORAS_MIN = 0.5
    HORAS_MAX = 8
    PASO_HORAS = 0.5
    NIVELES = {"junior": 1.0, "senior": 1.5, "experto": 2.0}
    MODALIDADES = {"virtual": 1.0, "presencial": 1.2}

    def __init__(
        self,
        nombre: str,
        tarifa_hora: int | float,
        especialidad: str,
        disponible: bool = True,
        *,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(
            nombre, tarifa_hora, disponible, id_entidad=id_entidad
        )
        self._especialidad = self._validar_texto(especialidad, "especialidad")

    @property
    def especialidad(self) -> str:
        return self._especialidad

    def validar_parametros(
        self,
        duracion: float,
        nivel: str = "junior",
        modalidad: str = "virtual",
        **otros: object,
    ) -> None:
        self._rechazar_opciones_desconocidas(otros)
        self._validar_duracion(
            duracion, self.HORAS_MIN, self.HORAS_MAX, self.PASO_HORAS
        )
        self._validar_opcion(nivel, "nivel", self.NIVELES)
        self._validar_opcion(modalidad, "modalidad", self.MODALIDADES)

    def calcular_costo(
        self,
        duracion: float,
        nivel: str = "junior",
        modalidad: str = "virtual",
        **otros: object,
    ) -> float:
        self.validar_parametros(
            duracion, nivel=nivel, modalidad=modalidad, **otros
        )
        nivel_normalizado = self._validar_opcion(nivel, "nivel", self.NIVELES)
        modalidad_normalizada = self._validar_opcion(
            modalidad, "modalidad", self.MODALIDADES
        )
        return (
            self.tarifa_base
            * duracion
            * self.NIVELES[nivel_normalizado]
            * self.MODALIDADES[modalidad_normalizada]
        )

    def descuento_por_defecto(self, duracion: float) -> float:
        return 0.05 if duracion >= 5 else 0.0

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "no disponible"
        return (
            f"Asesoría en {self.especialidad} '{self.nombre}', "
            f"${self.tarifa_base:,.0f} por hora (nivel junior), {estado}."
        )


AsesoriaEspecializada = Asesoria
