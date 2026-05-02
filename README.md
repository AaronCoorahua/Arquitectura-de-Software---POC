# POC de Factoring

POC en `FastAPI` para probar dos flujos principales del sistema:

- `Critical Path`: `POST /facturas`
- `Happy Path`: `POST /facturas/{id}/comprar`

## Alcance

- registro de facturas
- validacion de datos
- validacion mock de `SUNAT`
- publicacion de factura
- compra parcial o total
- tracking por factura
- persistencia simple con `SQLite`

## Arquitectura

- monolito modular
- frontend estatico en `index.html`
- backend en `backend/`
- base local `SQLite`

## Endpoints principales

- `GET /health`
- `GET /investors/{investor_id}`
- `GET /facturas`
- `POST /facturas`
- `POST /validate_invoice`
- `POST /facturas/{id}/comprar`
- `GET /facturas/{id}/tracking`

## Implementado

### Facturas

- registro de factura
- validacion de campos con `Pydantic`
- deteccion de duplicados por `ruc_emisor + serie + correlativo`
- publicacion si pasa validaciones
- rechazo con `rejection_reason` si falla

### Mock SUNAT

- `source = "sunat_mock"`
- exito
- rechazo funcional
- falla tecnica `503`

Reglas actuales:

- `serie` que empieza con `ERR`: falla tecnica
- `correlativo` que termina en `999`: rechazo funcional
- `ruc_emisor == ruc_pagador`: rechazo funcional

### Compras

- compra parcial o total
- validacion de estado de factura
- validacion de saldo disponible
- validacion de metodo de pago
- descuento de saldo del inversionista mock
- actualizacion de `monto_disponible`
- cambio de estado a `partially_funded` o `funded`
- calculo de `owned_fraction`
- calculo de `expected_return`

### Mock pagos

Metodos soportados:

- `yape`
- `plin`
- `tarjeta`
- `transferencia`
- `wallet`

Reglas actuales:

- `tarjeta` con monto mayor a `3000`: rechazo funcional `402`
- `transferencia` con monto mayor o igual a `4500`: falla tecnica `503`
- saldo insuficiente del inversionista: rechazo `400`

### Tracking

Eventos implementados:

- `invoice_uploaded`
- `sunat_validated`
- `invoice_published`
- `purchase_registered`

## Persistencia

Se usa `SQLite` en:

- `backend/factoring_poc.sqlite3`

Tablas:

- `invoices`
- `purchases`
- `tracking_events`
- `investors`

Ademas se cargan seeds minimos para probar la UI.

## Estados usados

### Factura

- `validating`
- `rejected`
- `published`
- `partially_funded`
- `funded`

### Compra

- `confirmed`

## Fuera de alcance

- autenticacion real
- `SUNAT` real
- pasarela real
- banco real
- redis
- payout a empresa vendedora
- cancelacion con penalidad

## Ejecucion

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Luego abre `index.html` para probar los dos paths.
