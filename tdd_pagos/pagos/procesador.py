import uuid
from decimal import Decimal

from pagos.excepciones import (
    ErrorPasarela, PagoFallidoError, PagoNoEncontradoError, ReembolsoInvalidoError,
)
from pagos.modelos import EstadoPago, Pago
from pagos.puertos import PasarelaPago, RepositorioPagos


class ProcesadorPagos:
    """Orquesta el cobro de pagos. No conoce implementaciones concretas de
    pasarela ni de repositorio: recibe las abstracciones por constructor."""

    def __init__(self, pasarela: PasarelaPago, repositorio: RepositorioPagos,
                 generador_id=None, max_reintentos: int = 1):
        self._max_reintentos = max_reintentos
        self._pasarela = pasarela
        self._repositorio = repositorio
        self._generador_id = generador_id or (lambda: str(uuid.uuid4()))

    def procesar_pago(self, monto: Decimal, token_tarjeta: str) -> Pago:
        self._validar_monto(monto)
        try:
            respuesta = self._cobrar_con_reintentos(monto, token_tarjeta)
        except ErrorPasarela as causa:
            self._registrar(monto, token_tarjeta, EstadoPago.ERROR)
            raise PagoFallidoError("No se pudo contactar la pasarela") from causa
        if respuesta.aprobado:
            return self._registrar(monto, token_tarjeta, EstadoPago.APROBADO,
                                   respuesta.id_transaccion)
        return self._registrar(monto, token_tarjeta, EstadoPago.RECHAZADO)

    def consultar_pago(self, id_pago: str) -> Pago:
        return self._obtener_o_fallar(id_pago)

    def reembolsar_pago(self, id_pago: str) -> Pago:
        pago = self._obtener_o_fallar(id_pago)
        if pago.estado != EstadoPago.APROBADO:
            raise ReembolsoInvalidoError("Solo se reembolsan pagos aprobados")
        if not self._pasarela.reembolsar(pago.id_transaccion):
            raise ReembolsoInvalidoError("La pasarela rechazo el reembolso")
        pago.estado = EstadoPago.REEMBOLSADO
        self._repositorio.guardar(pago)
        return pago

    def _obtener_o_fallar(self, id_pago: str) -> Pago:
        pago = self._repositorio.obtener(id_pago)
        if pago is None:
            raise PagoNoEncontradoError(id_pago)
        return pago

    def _cobrar_con_reintentos(self, monto: Decimal, token_tarjeta: str):
        intentos_restantes = self._max_reintentos
        while True:
            try:
                return self._pasarela.cobrar(monto, token_tarjeta)
            except ErrorPasarela:
                if intentos_restantes == 0:
                    raise
                intentos_restantes -= 1

    @staticmethod
    def _validar_monto(monto: Decimal) -> None:
        if monto <= 0:
            raise ValueError("El monto debe ser mayor que cero")

    def _registrar(self, monto, token_tarjeta, estado, id_transaccion=None) -> Pago:
        pago = Pago(self._generador_id(), monto, token_tarjeta, estado, id_transaccion)
        self._repositorio.guardar(pago)
        return pago
