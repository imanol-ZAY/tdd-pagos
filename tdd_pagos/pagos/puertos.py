"""Contratos (interfaces) de las dependencias externas.

El procesador depende de estas abstracciones y no de implementaciones
concretas (principio de inversion de dependencias). En las pruebas se
reemplazan por dobles creados con unittest.mock.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from pagos.modelos import Pago


@dataclass(frozen=True)
class RespuestaPasarela:
    aprobado: bool
    id_transaccion: Optional[str] = None


class PasarelaPago(ABC):
    @abstractmethod
    def cobrar(self, monto: Decimal, token_tarjeta: str) -> RespuestaPasarela:
        """Solicita el cobro a la pasarela. Puede lanzar ErrorPasarela."""

    @abstractmethod
    def reembolsar(self, id_transaccion: str) -> bool:
        """Solicita el reembolso. Devuelve True si fue aceptado."""


class RepositorioPagos(ABC):
    @abstractmethod
    def guardar(self, pago: Pago) -> None:
        """Persiste el pago (crea o actualiza)."""

    @abstractmethod
    def obtener(self, id_pago: str) -> Optional[Pago]:
        """Devuelve el pago o None si no existe."""
