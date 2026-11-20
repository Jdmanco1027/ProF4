import logging
from pathlib import Path


class Logger:
    @staticmethod
    def configurar(archivo: str | Path | None = None) -> logging.Logger:
        if archivo is None:
            archivo = Path(__file__).resolve().parent.parent / "logs" / "sistema.log"
        ruta = Path(archivo).resolve()
        ruta.parent.mkdir(parents=True, exist_ok=True)

        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        ya_configurado = any(
            isinstance(handler, logging.FileHandler)
            and Path(handler.baseFilename).resolve() == ruta
            for handler in root_logger.handlers
        )
        if not ya_configurado:
            manejador = logging.FileHandler(ruta, encoding="utf-8")
            manejador.setFormatter(
                logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
            )
            root_logger.addHandler(manejador)

        logger = logging.getLogger("sistema_software_fj")
        logger.setLevel(logging.INFO)
        logger.propagate = True
        return logger
