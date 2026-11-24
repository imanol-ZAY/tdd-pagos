import unittest
from decimal import Decimal
from unittest.mock import Mock

from pagos.excepciones import ErrorPasarela, PagoFallidoError
from pagos.modelos import EstadoPago
from pagos.procesador import ProcesadorPagos
from pagos.puertos import PasarelaPago, RepositorioPagos, RespuestaPasarela


class PruebasProcesarPago(unittest.TestCase):
    """Ciclo 1: procesar un pago.

    Convencion de dobles:
    - STUB: la pasarela. Solo se configura lo que devuelve (cobrar.return_value).
    - MOCK: el repositorio. Se verifica con que datos fue llamado (guardar).
    """

    def setUp(self):
        self.pasarela = Mock(spec=PasarelaPago)
        self.repositorio = Mock(spec=RepositorioPagos)
        self.procesador = ProcesadorPagos(
            self.pasarela, self.repositorio, generador_id=lambda: "P-001"
        )

    def _pago_guardado(self):
        self.repositorio.guardar.assert_called_once()
        return self.repositorio.guardar.call_args.args[0]

    def test_monto_cero_lanza_error_y_no_toca_dependencias(self):
        with self.assertRaises(ValueError):
            self.procesador.procesar_pago(Decimal("0"), "tok_abc")
        self.pasarela.cobrar.assert_not_called()
        self.repositorio.guardar.assert_not_called()

    def test_monto_negativo_lanza_error(self):
        with self.assertRaises(ValueError):
            self.procesador.procesar_pago(Decimal("-5.00"), "tok_abc")
        self.pasarela.cobrar.assert_not_called()

    def test_cobra_el_monto_y_el_token_recibidos(self):
        self.pasarela.cobrar.return_value = RespuestaPasarela(True, "TX-1")
        self.procesador.procesar_pago(Decimal("150.00"), "tok_abc")
        self.pasarela.cobrar.assert_called_once_with(Decimal("150.00"), "tok_abc")

    def test_pago_aprobado_se_guarda_como_aprobado(self):
        self.pasarela.cobrar.return_value = RespuestaPasarela(True, "TX-1")
        pago = self.procesador.procesar_pago(Decimal("150.00"), "tok_abc")
        self.assertEqual(pago.estado, EstadoPago.APROBADO)
        self.assertEqual(pago.id_transaccion, "TX-1")
        self.assertEqual(pago.id, "P-001")
        self.assertIs(self._pago_guardado(), pago)

    def test_pago_rechazado_se_guarda_como_rechazado(self):
        self.pasarela.cobrar.return_value = RespuestaPasarela(False)
        pago = self.procesador.procesar_pago(Decimal("80.00"), "tok_abc")
        self.assertEqual(pago.estado, EstadoPago.RECHAZADO)
        self.assertIsNone(pago.id_transaccion)
        self.assertEqual(self._pago_guardado().estado, EstadoPago.RECHAZADO)

    def test_error_de_pasarela_guarda_estado_error_y_lanza_pago_fallido(self):
        self.pasarela.cobrar.side_effect = ErrorPasarela("timeout")
        with self.assertRaises(PagoFallidoError):
            self.procesador.procesar_pago(Decimal("40.00"), "tok_abc")
        self.assertEqual(self._pago_guardado().estado, EstadoPago.ERROR)


if __name__ == "__main__":
    unittest.main()
