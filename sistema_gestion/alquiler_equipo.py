from sistema_gestion.servicio import Servicio


class AlquilerEquipo(Servicio):
    UNIDAD_DURACION = "días"
    DIAS_MIN = 1
    DIAS_MAX = 30
    RECARGO_SEGURO = 0.05

    def __init__(
        self,
        nombre: str,
        tarifa_dia: int | float,
        tipo_equipo: str,
        stock: int,
        disponible: bool = True,
        *,
        id_entidad: str | None = None,
    ) -> None:
        super().__init__(
            nombre, tarifa_dia, disponible, id_entidad=id_entidad
        )
        self._tipo_equipo = self._validar_texto(tipo_equipo, "tipo_equipo")
        self._stock = self._validar_entero(stock, "stock", minimo=1)

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def stock(self) -> int:
        return self._stock

    def validar_parametros(
        self,
        duracion: float,
        unidades: int = 1,
        con_seguro: bool = False,
        **otros: object,
    ) -> None:
        self._rechazar_opciones_desconocidas(otros)
        self._validar_duracion(duracion, self.DIAS_MIN, self.DIAS_MAX, paso=1)
        self._validar_entero(unidades, "unidades", minimo=1, maximo=self.stock)
        self._validar_booleano(con_seguro, "con_seguro")

    def calcular_costo(
        self,
        duracion: float,
        unidades: int = 1,
        con_seguro: bool = False,
        **otros: object,
    ) -> float:
        self.validar_parametros(
            duracion, unidades=unidades, con_seguro=con_seguro, **otros
        )
        costo = self.tarifa_base * duracion * unidades
        if con_seguro:
            costo += costo * self.RECARGO_SEGURO
        return costo

    def descuento_por_defecto(self, duracion: float) -> float:
        if duracion >= 15:
            return 0.15
        if duracion >= 7:
            return 0.10
        return 0.0

    def describir(self) -> str:
        estado = "disponible" if self.disponible else "no disponible"
        return (
            f"Alquiler de {self.tipo_equipo} '{self.nombre}' "
            f"({self.stock} unidades), ${self.tarifa_base:,.0f} por día, {estado}."
        )
