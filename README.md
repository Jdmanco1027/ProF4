# ProF4

#Sistema integral de gestión de clientes, servicios y reservas para la fase 4
#del componente práctico.

## Requisitos

- Python 3.10 o superior
- No requiere paquetes externos ni base de datos

## Ejecutar la demostración

Desde la carpeta del proyecto:

```powershell
python main.py
```

La demostración ejecuta doce operaciones con resultados válidos e inválidos.
Los clientes, servicios y reservas se conservan en listas en memoria durante
la ejecución. Los eventos y errores se escriben en `logs/sistema.log`.

## Ejecutar las pruebas

```powershell
python -m unittest discover -s tests -v
```

## Organización

- `sistema_gestion/entidad.py`: clase abstracta `Entidad` con identificador y resumen.
- `sistema_gestion/cliente.py`: cliente con documento, validaciones e historial.
- `sistema_gestion/servicio.py`: servicio abstracto, IVA, descuentos y cálculos.
- `sistema_gestion/reserva_sala.py`: servicio de reserva de salas.
- `sistema_gestion/alquiler_equipo.py`: servicio de alquiler de equipos.
- `sistema_gestion/asesoria.py`: servicio de asesoría especializada.
- `sistema_gestion/reserva.py`: estados y operaciones de una reserva.
- `sistema_gestion/sistema.py`: listas en memoria y registro de objetos.
- `sistema_gestion/excepciones.py`: excepciones propias.
- `sistema_gestion/logger.py`: registro de eventos y errores.
- `main.py` y `simulacion.py`: entrada y demostración ejecutable.
- `tests/`: pruebas automatizadas.

Los descuentos e impuestos se expresan como fracciones entre 0 y 1
(por ejemplo, `0.19` representa el 19 % de IVA). Cada servicio valida sus
parámetros específicos (`personas` para salas, `unidades` para equipos) y
calcula su costo total mediante la misma interfaz.
