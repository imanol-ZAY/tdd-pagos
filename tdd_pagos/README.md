# Modulo de procesamiento de pagos (TDD)

Actividad de Pruebas de Software: ciclo Red-Green-Refactor, dobles de prueba
(mocks y stubs) y pruebas de regresion.

Autor: Imanol Paulino Reinoso, UTECO.

## Estructura

    pagos/
      modelos.py       Pago y EstadoPago
      puertos.py       Interfaces PasarelaPago y RepositorioPagos
      excepciones.py   Excepciones del dominio
      procesador.py    ProcesadorPagos (logica de negocio)
    tests/
      test_procesar_pago.py          Ciclo 1
      test_consultar_reembolsar.py   Ciclo 2
      test_reintentos.py             Requisito modificado (regresion)
    evidencias/        Logs de cada fase (rojo, verde, refactor, regresion)

## Ejecutar las pruebas

Requiere Python 3.9 o superior. No usa librerias externas.

    python -m unittest discover -v

## Historial TDD

Cada fase tiene su propio commit: `git log --oneline`.
