# POC de Factoring

## Objetivo

Construir un POC en FastAPI centrado en dos flujos:

- Happy path: compra de una factura.
- Critical path: `POST /facturas` con resultado exitoso y fallido.

## Alcance funcional

El POC implementa de forma minima:

- Registro de facturas por una empresa vendedora.
- Validacion interna de datos de la factura.
- Validacion mock de SUNAT.
- Publicacion de la factura si pasa validaciones.
- Compra total o parcial de una factura por un inversionista.
- Tracking basico del estado de la factura y de la compra.

## Integraciones externas del POC

Segun el README original, estas integraciones existen en la arquitectura pero para el POC se mockean:

- `SUNAT API`
- `Pasarela de pagos`
- `Servicio bancario`

Tambien `Redis` queda fuera de implementacion real en esta primera version.

## Reglas de mock definidas para empezar a implementar

### Mock SUNAT

El POC no se conecta a SUNAT real.

Se fija esta regla minima:

- si `correlativo` termina en `99`, la validacion responde rechazada
- en cualquier otro caso, la validacion responde aceptada

Salida esperada del mock:

- `source = "sunat_mock"`
- `is_valid = true/false`
- `observations = []` o mensajes de observacion
- `rejection_reason = null` o `"SUNAT validation failed"`

Esto cubre el camino exitoso y el camino fallido exigidos por el README.

### Mock pasarela de pagos

El README menciona pagos por `Yape`, `Plin`, `Tarjeta`, `transferencia`, y en observaciones tambien aparece wallet como posibilidad.

Para este POC se fija:

- no hay integracion real con una pasarela externa
- el backend solo valida que el metodo de pago este soportado
- si el metodo es soportado, el pago se considera exitoso
- si el metodo no es soportado, la compra se rechaza

Metodos soportados en esta iteracion:

- `yape`
- `plin`
- `tarjeta`
- `transferencia`
- `wallet`

### Mock servicio bancario

El README indica que hay servicio bancario y pago a la empresa vendedora, pero tambien deja abierto en que momento ocurre.

Para alinear el POC con ese alcance:

- no se implementa integracion real con banco
- no se realiza desembolso a empresa vendedora
- no se realiza recaudacion ni payout al vencimiento
- el banco queda representado solo como dependencia futura

## Supuestos cerrados para este POC

Estos supuestos ya no quedan abiertos para el equipo:

- La implementacion sera sincronica dentro de un monolito modular.
- `Auth` no se implementa completo; `seller_id` e `investor_id` se tratan como datos mock de aplicacion.
- `Tracking` se guarda de forma minima en memoria para esta primera base.
- No hay `Redis` real en esta iteracion.
- No hay integracion real con `SUNAT API`, pasarela ni banco.
- El pago a la empresa vendedora queda fuera del alcance del `POST /facturas`.
- La evaluacion de empresa compradora/deudora no se desarrolla como servicio separado; en esta base solo se deja contemplada como extension futura.

## Contratos minimos del POC

### `POST /facturas`

Registra una factura, ejecuta validacion interna y validacion SUNAT mock, y termina en:

- `published` si pasa validaciones
- `rejected` si falla validacion

Campos minimos:

- `ruc_emisor`
- `ruc_pagador`
- `serie`
- `correlativo`
- `monto`
- `fecha_emision`
- `fecha_vencimiento`
- `tasa_interes`
- `archivo_xml`

### `POST /validate_invoice`

Ejecuta la validacion mock de SUNAT para una factura.

### `POST /facturas/{id}/comprar`

Registra la compra de una factura publicada.

Validaciones minimas:

- la factura debe existir
- la factura debe estar `published` o `partially_funded`
- el metodo de pago debe estar soportado
- el monto no puede superar el saldo disponible

## Estados minimos

### Factura

- `draft`
- `validating`
- `rejected`
- `published`
- `partially_funded`
- `funded`
- `paid`

### Compra

- `pending_payment`
- `confirmed`
- `cancelled`

### Tracking

- `invoice_uploaded`
- `sunat_validated`
- `invoice_published`
- `purchase_registered`

## Reparticion sugerida para equipo de 4

### Integrante 1: Facturas

- `POST /facturas`
- reglas de validacion
- estados de factura

### Integrante 2: Validacion

- `POST /validate_invoice`
- mock SUNAT
- criterios de rechazo

### Integrante 3: Marketplace

- `POST /facturas/{id}/comprar`
- compra parcial
- validacion de medio de pago mock
- calculo de retorno esperado

### Integrante 4: Tracking y soporte

- tracking por factura y compra
- listados y consultas
- soporte transversal de configuracion y pruebas

## Estructura base acordada

El backend se organiza por modulos simples:

- `facturas`
- `validation`
- `marketplace`
- `tracking`
- `shared`

Cada modulo tiene:

- `routes.py`
- `schemas.py`
- `services.py`

## Que si implementa esta primera base

- contrato base de facturas
- contrato base de compra
- validacion SUNAT mock
- validacion de medio de pago mock
- tracking minimo
- almacenamiento temporal en memoria

## Que no implementa aun esta primera base

- autenticacion real
- base de datos real
- redis real
- pasarela real
- banco real
- payout a empresa vendedora
- dashboard
- wallet real
- cancelacion con penalidad

## Resultado esperado

Dejar una base suficientemente clara y alineada al README para que el equipo empiece a implementar de inmediato, sabiendo exactamente que partes del sistema son reales en el POC y cuales quedan simuladas.
