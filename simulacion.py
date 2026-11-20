from collections.abc import Callable
from typing import Any

from sistema_gestion import (
    AlquilerEquipo,
    Asesoria,
    Cliente,
    ReservaSala,
    SistemaGestion,
)
from sistema_gestion.excepciones import SistemaSoftwareFJError
from sistema_gestion.logger import Logger


def ejecutar_operacion(
    numero: int,
    descripcion: str,
    accion: Callable[[], Any],
    logger: Any,
) -> Any:
    print(f"\n{numero}. {descripcion}")
    try:
        resultado = accion()
    except SistemaSoftwareFJError as exc:
        logger.exception("Operación %s fallida: %s", numero, descripcion)
        print(f"Error controlado: {exc}")
        return None
    except Exception as exc:
        logger.exception("Error inesperado en operación %s: %s", numero, descripcion)
        print(f"Error inesperado registrado: {exc}")
        return None
    else:
        logger.info("Operación %s completada: %s", numero, descripcion)
        print(f"Correcto: {resultado}")
        return resultado
    finally:
        logger.info("Fin de operación %s.", numero)


def ejecutar_demostracion() -> None:
    logger = Logger.configurar()
    sistema = SistemaGestion()

    cliente = Cliente(
        "CLI-001", "Ana Pérez", "1053849201", "ana@example.com", "3001234567"
    )
    sala = ReservaSala("Sala Norte", 120000, capacidad=10)
    equipo = AlquilerEquipo("Proyector", 80000, "audiovisual", stock=4)
    asesoria = Asesoria(
        "Asesoría técnica", 150000, "desarrollo de software"
    )

    ejecutar_operacion(
        1, "Registrar un cliente válido.", lambda: sistema.registrar_cliente(cliente), logger
    )
    ejecutar_operacion(
        2,
        "Intentar crear un cliente con datos inválidos.",
        lambda: Cliente("CLI-002", "Luis123", "123", "correo-invalido", "3001234567"),
        logger,
    )
    ejecutar_operacion(
        3,
        "Registrar un servicio de reserva de sala.",
        lambda: sistema.registrar_servicio(sala).describir(),
        logger,
    )
    ejecutar_operacion(
        4,
        "Intentar crear un servicio con tarifa inválida.",
        lambda: AlquilerEquipo("Portátil", 0, "computación", stock=2),
        logger,
    )
    ejecutar_operacion(
        5,
        "Registrar un servicio de alquiler de equipos.",
        lambda: sistema.registrar_servicio(equipo).describir(),
        logger,
    )
    ejecutar_operacion(
        6,
        "Registrar un servicio de asesoría especializada.",
        lambda: sistema.registrar_servicio(asesoria).describir(),
        logger,
    )

    def reserva_exitosa() -> str:
        reserva = sistema.crear_reserva(
            cliente, sala, 2, {"personas": 4}
        )
        reserva.confirmar(descuento=0.10, impuesto=0.19)
        monto = reserva.procesar()
        return f"{reserva.estado.value}, total ${monto:,.2f}"

    ejecutar_operacion(
        7, "Confirmar y procesar una reserva válida.", reserva_exitosa, logger
    )

    def reserva_fuera_de_capacidad() -> None:
        sistema.crear_reserva(
            cliente, sala, 1, {"personas": 12}
        )

    ejecutar_operacion(
        8,
        "Intentar reservar una sala para más personas de las permitidas.",
        reserva_fuera_de_capacidad,
        logger,
    )

    def cancelar_reserva() -> str:
        reserva = sistema.crear_reserva(cliente, asesoria, 1)
        reserva.cancelar()
        return reserva.estado.value

    ejecutar_operacion(
        9, "Crear y cancelar una reserva pendiente.", cancelar_reserva, logger
    )

    def procesar_reserva_pendiente() -> None:
        reserva = sistema.crear_reserva(
            cliente, equipo, 1, {"unidades": 2}
        )
        reserva.procesar()

    ejecutar_operacion(
        10,
        "Intentar procesar una reserva que aún no ha sido confirmada.",
        procesar_reserva_pendiente,
        logger,
    )

    def reservar_servicio_inexistente() -> None:
        servicio = Asesoria("Servicio no registrado", 90000, "consultoría")
        sistema.crear_reserva(cliente, servicio, 1)

    ejecutar_operacion(
        11,
        "Intentar reservar un servicio que no está registrado.",
        reservar_servicio_inexistente,
        logger,
    )

    def continuar_despues_de_errores() -> str:
        reserva = sistema.crear_reserva(
            cliente, equipo, 2, {"unidades": 2}
        )
        reserva.confirmar(impuesto=0)
        monto = reserva.procesar()
        return f"{reserva.estado.value}, total ${monto:,.2f}"

    ejecutar_operacion(
        12,
        "Procesar otra reserva para comprobar que el sistema sigue activo.",
        continuar_despues_de_errores,
        logger,
    )

    print(f"\nReservas registradas en memoria: {len(sistema.reservas)}")
    print("Los eventos y errores quedaron registrados en logs/sistema.log.")
