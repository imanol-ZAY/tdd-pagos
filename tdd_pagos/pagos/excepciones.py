class ErrorPasarela(Exception):
    """La pasarela de pago externa fallo (red, timeout, servicio caido)."""


class PagoFallidoError(Exception):
    """El pago no pudo procesarse por un error de infraestructura."""


class PagoNoEncontradoError(Exception):
    """No existe un pago con el identificador indicado."""


class ReembolsoInvalidoError(Exception):
    """El pago no cumple las condiciones para ser reembolsado."""
