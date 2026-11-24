import unittest
from decimal import Decimal
from unittest.mock import Mock

from pagos.excepciones import ErrorPasarela, PagoFallidoError
from pagos.modelos import EstadoPago
from pagos.procesador import ProcesadorPagos
from pagos.puertos import PasarelaPago, RepositorioPagos, RespuestaPasarela


class PruebasReintentoPasarela(unittest.TestCase):
    """Requisito modificado: ante ErrorPasarela se reintenta UNA vez
    antes de marcar el pago como ERROR."""

    def setUp(self):
        self.pasarela = Mock(spec=PasarelaPago)
        self.repositorio = Mock(spec=RepositorioPagos)
        self.procesador = ProcesadorPagos(
            self.pasarela, self.repositorio, generador_id=lambda: "P-001"
        )

    def test_reintenta_una_vez_y_aprueba_si_el_segundo_intento_funciona(self):
        self.pasarela.cobrar.side_effect = [
            ErrorPasarela("timeout"),
            RespuestaPasarela(True, "TX-2"),
        ]
        pago = self.procesador.procesar_pago(Decimal("60.00"), "tok_abc")
        self.assertEqual(pago.estado, EstadoPago.APROBADO)
        self.assertEqual(self.pasarela.cobrar.call_count, 2)
        self.repositorio.guardar.assert_called_once()

    def test_si_el_reintento_tambien_falla_marca_error_tras_dos_intentos(self):
        self.pasarela.cobrar.side_effect = ErrorPasarela("caida")
        with self.assertRaises(PagoFallidoError):
            self.procesador.procesar_pago(Decimal("60.00"), "tok_abc")
        self.assertEqual(self.pasarela.cobrar.call_count, 2)
        self.repositorio.guardar.assert_called_once()
        self.assertEqual(
            self.repositorio.guardar.call_args.args[0].estado, EstadoPago.ERROR
        )

    def test_un_rechazo_no_se_reintenta(self):
        self.pasarela.cobrar.return_value = RespuestaPasarela(False)
        self.procesador.procesar_pago(Decimal("60.00"), "tok_abc")
        self.pasarela.cobrar.assert_called_once()


if __name__ == "__main__":
    unittest.main()
