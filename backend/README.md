# Backend FastAPI

## Que hace

Backend del POC de factoring con:

- registro de facturas
- validacion mock de `SUNAT`
- compra de facturas
- tracking
- persistencia en `SQLite`

## Endpoints

- `GET /health`
- `GET /investors/{investor_id}`
- `GET /facturas`
- `POST /facturas`
- `POST /validate_invoice`
- `POST /facturas/{id}/comprar`
- `GET /facturas/{id}/tracking`

## Estructura

- `main.py`
- `database.py`
- `modules/facturas`
- `modules/validation`
- `modules/marketplace`
- `modules/tracking`
- `modules/shared`

## Persistencia

Base local:

- `backend/factoring_poc.sqlite3`

Tablas:

- `invoices`
- `purchases`
- `tracking_events`
- `investors`

La base se crea sola al iniciar y agrega datos seed para pruebas.

## Mocks implementados

### SUNAT

- exito
- rechazo funcional
- falla tecnica `503`

Reglas actuales:

- `serie` que empieza con `ERR`: falla tecnica
- `correlativo` que termina en `999`: rechazo
- `ruc_emisor == ruc_pagador`: rechazo

### Pagos

Metodos soportados:

- `yape`
- `plin`
- `tarjeta`
- `transferencia`
- `wallet`

Reglas actuales:

- `tarjeta` con monto mayor a `3000`: rechazo `402`
- `transferencia` con monto mayor o igual a `4500`: falla tecnica `503`
- saldo insuficiente: rechazo `400`

## Ejecutar

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

## Notas

- `seller_id` e `investor_id` son mock
- hay `CORS` abierto para probar `index.html`
- no hay auth real, banco real ni pasarela real

