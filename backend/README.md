# Backend FastAPI

## Objetivo

Implementar solo los flujos minimos del POC:

- `POST /facturas`
- `POST /validate_invoice`
- `POST /facturas/{id}/comprar`
- `GET /facturas`
- `GET /facturas/{id}/tracking`

## Estructura

- `main.py`
- `modules/facturas`
- `modules/validation`
- `modules/marketplace`
- `modules/tracking`
- `modules/shared`

Cada modulo tiene:

- `routes.py`
- `schemas.py`
- `services.py`

## Que se mockea en este backend

### SUNAT

No hay integracion real con SUNAT.

La simulacion queda como `TODO` del equipo.

El endpoint y el servicio ya existen, pero la logica mock no esta implementada todavia.

### Pasarela de pagos

No hay pasarela real.

La simulacion queda como `TODO` del equipo.

La compra hoy solo deja visible la lista base de metodos pensados para el POC:

- `yape`
- `plin`
- `tarjeta`
- `transferencia`
- `wallet`

Falta implementar la respuesta mock de exito o falla.

### Servicio bancario

No hay banco real ni transferencias reales.

En esta iteracion:

- no se paga a la empresa vendedora
- no se hace recaudacion
- no se liquida al vencimiento

## Persistencia del POC

La base ahora usa `SQLite` local para mantener el POC simple pero persistente:

- `backend/factoring_poc.sqlite3`
- tabla `invoices`
- tabla `purchases`
- tabla `tracking_events`
- tabla `investors`

La base se inicializa automaticamente al levantar FastAPI y agrega seeds minimos para probar la UI.

## Ejecutar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Notas para implementacion

- `seller_id` e `investor_id` hoy se manejan como mock
- `tracking` se guarda de forma minima
- `Auth`, `Redis`, banco y pasarela real quedan para una siguiente etapa
- `SUNAT` y pagos se simulan con reglas mock para el POC
- existe un endpoint extra `GET /investors/{investor_id}` para leer saldo mock del inversionista desde la UI

## Manejo de fallos esperado

Resumen alineado al `POC.md`:

- si falla validacion interna de factura: responder `400` y no publicar
- si SUNAT mock rechaza: factura `rejected`
- si SUNAT mock falla tecnicamente: responder `503`
- si falla validacion de compra: responder `400` o `404` segun el caso
- si pago mock rechaza: no registrar compra ni descontar saldo
- si pago mock falla tecnicamente: responder `503`

La matriz detallada de fallos esta en [POC.md].
