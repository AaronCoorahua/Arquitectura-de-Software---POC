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

Regla actual del mock:

- si `correlativo` termina en `99`, la factura se rechaza
- en cualquier otro caso, la factura se valida

El endpoint devuelve `source = "sunat_mock"`.

### Pasarela de pagos

No hay pasarela real.

La compra solo valida que el metodo de pago pertenezca a:

- `yape`
- `plin`
- `tarjeta`
- `transferencia`
- `wallet`

Si el metodo es valido, el POC considera el pago como exitoso.

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
