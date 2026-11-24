import unittest
from decimal import Decimal
from unittest.mock import Mock

from pagos.excepciones import PagoNoEncontradoError, ReembolsoInvalidoError
from pagos.modelos import EstadoPago, Pago
from pagos.procesador import ProcesadorPagos
from pagos.puertos import PasarelaPago, RepositorioPagos


def un_pago(estado=EstadoPago.APROBADO, id_transaccion="TX-9"):
    return Pago("P-009", Decimal("200.00"), "tok_xyz", estado, id_transaccion)


class PruebasConsultarPago(unittest.TestCase):
    """Ciclo 2a: consultar un pago. El repositorio es un STUB (solo devuelve)."""

    def setUp(self):
        self.repositorio = Mock(spec=RepositorioPagos)
        self.procesador = ProcesadorPagos(Mock(spec=PasarelaPago), self.repositorio)

    def test_devuelve_el_pago_existente(self):
        pago = un_pago()
        self.repositorio.obtener.return_value = pago
        self.assertIs(self.procesador.consultar_pago("P-009"), pago)
        self.repositorio.obtener.assert_called_once_with("P-009")

    def test_pago_inexistente_lanza_no_encontrado(self):
        self.repositorio.obtener.return_value = None
        with self.assertRaises(PagoNoEncontradoError):
            self.procesador.consultar_pago("P-404")


class PruebasReembolsarPago(unittest.TestCase):
    """Ciclo 2b: reembolsar. Pasarela y repositorio actuan como stub y mock
    segun lo que se quiera controlar o verificar en cada prueba."""

    def setUp(self):
        self.pasarela = Mock(spec=PasarelaPago)
        self.repositorio = Mock(spec=RepositorioPagos)
        self.procesador = ProcesadorPagos(self.pasarela, self.repositorio)

    def test_reembolsa_pago_aprobado_y_lo_guarda(self):
        self.repositorio.obtener.return_value = un_pago()
        self.pasarela.reembolsar.return_value = True
        pago = self.procesador.reembolsar_pago("P-009")
        self.assertEqual(pago.estado, EstadoPago.REEMBOLSADO)
        self.pasarela.reembolsar.assert_called_once_with("TX-9")
        self.repositorio.guardar.assert_called_once_with(pago)

    def test_no_reembolsa_pago_que_no_esta_aprobado(self):
        self.repositorio.obtener.return_value = un_pago(EstadoPago.RECHAZADO, None)
        with self.assertRaises(ReembolsoInvalidoError):
            self.procesador.reembolsar_pago("P-009")
        self.pasarela.reembolsar.assert_not_called()
        self.repositorio.guardar.assert_not_called()

    def test_no_reembolsa_dos_veces(self):
        self.repositorio.obtener.return_value = un_pago(EstadoPago.REEMBOLSADO)
        with self.assertRaises(ReembolsoInvalidoError):
            self.procesador.reembolsar_pago("P-009")
        self.pasarela.reembolsar.assert_not_called()

    def test_si_la_pasarela_rechaza_el_reembolso_no_cambia_el_estado(self):
        pago = un_pago()
        self.repositorio.obtener.return_value = pago
        self.pasarela.reembolsar.return_value = False
        with self.assertRaises(ReembolsoInvalidoError):
            self.procesador.reembolsar_pago("P-009")
        self.assertEqual(pago.estado, EstadoPago.APROBADO)
        self.repositorio.guardar.assert_not_called()

    def test_reembolsar_pago_inexistente_lanza_no_encontrado(self):
        self.repositorio.obtener.return_value = None
        with self.assertRaises(PagoNoEncontradoError):
            self.procesador.reembolsar_pago("P-404")
        self.pasarela.reembolsar.assert_not_called()


if __name__ == "__main__":
    unittest.main()
