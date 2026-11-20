import unittest

from sistema_gestion import (
    AlquilerEquipo,
    Asesoria,
    Cliente,
    EstadoReserva,
    ReservaSala,
    SistemaGestion,
)
from sistema_gestion.excepciones import (
    CostoInvalidoError,
    DatoInvalidoError,
    OperacionNoPermitidaError,
    ParametroFaltanteError,
    ValidacionError,
)


class SistemaGestionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sistema = SistemaGestion()
        self.cliente = self.sistema.registrar_cliente(
            Cliente(
                "CLI-001",
                "Ana Pérez",
                "1053849201",
                "ana@example.com",
                "3001234567",
            )
        )
        self.sala = self.sistema.registrar_servicio(
            ReservaSala("Sala Norte", 100000, capacidad=2)
        )

    def test_entidad_y_cliente_usan_contrato_de_ana(self) -> None:
        self.assertEqual(self.cliente.id_entidad, "CLI-001")
        self.assertTrue(self.cliente.validar())
        self.assertIn("1053849201", self.cliente.obtener_resumen())

    def test_cliente_requiere_id_y_documento_validos(self) -> None:
        with self.assertRaises(DatoInvalidoError) as contexto:
            Cliente("", "Ana Pérez", "1053849201", "ana@example.com", "3001234567")
        self.assertIsInstance(contexto.exception.__cause__, ParametroFaltanteError)

        with self.assertRaises(DatoInvalidoError):
            Cliente("CLI-002", "Ana Pérez", "123", "ana@example.com", "3001234567")

    def test_calcula_costo_con_impuesto_y_descuento_como_fracciones(self) -> None:
        total = self.sala.calcular_costo_total(
            2,
            descuento=0.10,
            impuesto=0.19,
            personas=2,
        )
        self.assertAlmostEqual(total, 214200)

    def test_reserva_confirma_y_procesa_con_api_de_servicio(self) -> None:
        reserva = self.sistema.crear_reserva(
            self.cliente, self.sala, 2, {"personas": 2}
        )
        monto = reserva.confirmar(descuento=0.10, impuesto=0.19)

        self.assertAlmostEqual(monto, 214200)
        self.assertIs(reserva.estado, EstadoReserva.CONFIRMADA)
        self.assertAlmostEqual(reserva.procesar(), 214200)
        self.assertIs(reserva.estado, EstadoReserva.PROCESADA)
        self.assertEqual(self.cliente.historial_reservas, [reserva])

    def test_reserva_rechaza_capacidad_excedida_al_crearla(self) -> None:
        with self.assertRaises(ValidacionError):
            self.sistema.crear_reserva(
                self.cliente, self.sala, 1, {"personas": 3}
            )

    def test_reserva_rechaza_operaciones_en_estado_incorrecto(self) -> None:
        reserva = self.sistema.crear_reserva(
            self.cliente, self.sala, 1, {"personas": 1}
        )
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.procesar()

        reserva.confirmar(impuesto=0)
        reserva.procesar()
        with self.assertRaises(OperacionNoPermitidaError):
            reserva.cancelar()

    def test_reserva_rechaza_servicio_no_disponible(self) -> None:
        self.sala.disponible = False
        reserva = self.sistema.crear_reserva(
            self.cliente, self.sala, 1, {"personas": 1}
        )
        with self.assertRaises(CostoInvalidoError) as contexto:
            reserva.confirmar()
        self.assertIsInstance(
            contexto.exception.__cause__, OperacionNoPermitidaError
        )
        self.assertIs(reserva.estado, EstadoReserva.PENDIENTE)

    def test_servicios_aplican_parametros_especificos(self) -> None:
        equipo = AlquilerEquipo("Proyector", 80000, "audiovisual", stock=3)
        self.assertAlmostEqual(
            equipo.calcular_costo_total(
                2, descuento=0, impuesto=0, unidades=2, con_seguro=True
            ),
            336000,
        )

        asesoria = Asesoria("Asesoría", 150000, "software")
        self.assertAlmostEqual(
            asesoria.calcular_costo_total(
                1, descuento=0, impuesto=0, nivel="senior", modalidad="virtual"
            ),
            225000,
        )

    def test_rechaza_duracion_fuera_de_rango(self) -> None:
        with self.assertRaises(ValidacionError):
            self.sistema.crear_reserva(
                self.cliente, self.sala, 13, {"personas": 1}
            )

    def test_no_crea_reserva_para_servicio_no_registrado(self) -> None:
        servicio = Asesoria("Asesoría", 90000, "consultoría")
        with self.assertRaises(OperacionNoPermitidaError):
            self.sistema.crear_reserva(self.cliente, servicio, 1)


if __name__ == "__main__":
    unittest.main()
