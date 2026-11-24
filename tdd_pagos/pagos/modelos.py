from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


class EstadoPago(Enum):
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    ERROR = "ERROR"
    REEMBOLSADO = "REEMBOLSADO"


@dataclass
class Pago:
    id: str
    monto: Decimal
    token_tarjeta: str
    estado: EstadoPago
    id_transaccion: Optional[str] = None
