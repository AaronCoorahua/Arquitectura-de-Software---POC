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

La base actual usa almacenamiento en memoria para avanzar rapido:

- `invoices`
- `purchases`
- `tracking_events`

Esto permite probar los flujos sin meter base de datos todavia.

## Ejecutar

```bash
uvicorn main:app --reload
```

## Notas para implementacion

- `seller_id` e `investor_id` hoy se manejan como mock
- `tracking` se guarda de forma minima
- `Auth`, `Redis`, banco y pasarela real quedan para una siguiente etapa
- mock de `SUNAT` y mock de pagos quedan marcados como `TODO`
