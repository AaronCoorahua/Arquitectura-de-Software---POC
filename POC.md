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

## Reglas de mock a implementar

### Mock SUNAT

El POC no se conecta a SUNAT real. Esta simulacion queda como `TODO` del equipo.

La implementacion del mock debe devolver como minimo:

- `source = "sunat_mock"`
- `is_valid = true/false`
- `observations = []` o mensajes de observacion
- `rejection_reason = null` o `"SUNAT validation failed"`

Debe cubrir al menos:

- un caso exitoso
- un caso fallido

La regla exacta del mock queda abierta para implementacion del equipo.

### Mock pasarela de pagos

El README menciona pagos por `Yape`, `Plin`, `Tarjeta`, `transferencia`, y en observaciones tambien aparece wallet como posibilidad.

Para este POC se deja como `TODO`:

- no hay integracion real con una pasarela externa
- se debe crear una simulacion de respuesta de pago
- la compra debe reaccionar a exito o falla del mock

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
- no se realiza desembolso a empresa vendedora en esta base
- no se realiza recaudacion ni payout al vencimiento en esta base
- el banco queda representado solo como dependencia futura

## Supuestos cerrados para este POC

Estos supuestos ya no quedan abiertos para el equipo:

- La implementacion sera sincronica dentro de un monolito modular.
- `Auth` no se implementa completo; `seller_id` e `investor_id` se tratan como datos mock de aplicacion.
- `Tracking` se guarda de forma minima en memoria para esta primera base.
- No hay `Redis` real en esta iteracion.
- No hay integracion real con `SUNAT API`, pasarela ni banco.
- Los mocks de SUNAT y pagos quedan intencionalmente como `TODO`.
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

## Manejo de fallos por flujo

Esta seccion fija que debe pasar si falla un servicio o una validacion dentro de los dos paths principales del POC.

## Critical Path: `POST /facturas`

### Caso exitoso

Secuencia esperada:

1. validacion interna exitosa
2. validacion SUNAT mock exitosa
3. validacion de negocio exitosa
4. factura publicada

Resultado:

- `status` de factura: `published`
- response sugerido: `201`
- tracking esperado:
  - `invoice_uploaded`
  - `sunat_validated`
  - `invoice_published`

### Fallo en validacion interna

Ejemplos:

- monto menor o igual a cero
- fecha de vencimiento invalida
- factura duplicada
- campos obligatorios incompletos

Resultado esperado:

- no se llama a SUNAT mock
- la factura no debe quedar publicada
- response sugerido: `400`
- response body con mensaje claro de validacion
- tracking minimo esperado:
  - opcional registrar `invoice_uploaded` solo si ya se persistio antes de validar
  - no registrar `sunat_validated`
  - no registrar `invoice_published`

Decision recomendada para el equipo:

- validar primero y persistir despues para evitar facturas invalidas guardadas

### Fallo en `Validation & SUNAT Service`

Esto cubre cuando el mock de SUNAT responde rechazo funcional.

Resultado esperado:

- la factura queda `rejected`
- response sugerido: `400`
- `rejection_reason` obligatorio
- tracking esperado:
  - `invoice_uploaded`
  - no registrar `sunat_validated`
  - no registrar `invoice_published`

### Falla tecnica del mock SUNAT

Esto cubre timeout, excepcion interna o indisponibilidad del mock.

Resultado esperado:

- la factura no debe quedar `published`
- response sugerido: `503`
- mensaje tipo `SUNAT service unavailable`
- tracking esperado:
  - `invoice_uploaded` si ya se registro entrada
  - no registrar `sunat_validated`
  - no registrar `invoice_published`

Decision recomendada para el equipo:

- dejar la factura en `validating` o no persistirla si prefieren una version mas simple
- documentar una sola politica y mantenerla consistente

### Fallo en validacion de negocio

Esto cubre rechazo posterior a SUNAT, por ejemplo evaluacion de empresa compradora/deudora.

Resultado esperado:

- la factura queda `rejected`
- response sugerido: `400`
- `rejection_reason` de negocio obligatorio
- tracking esperado:
  - `invoice_uploaded`
  - `sunat_validated`
  - no registrar `invoice_published`

## Happy Path: `POST /facturas/{id}/comprar`

### Caso exitoso

Secuencia esperada:

1. factura encontrada
2. factura disponible para compra
3. monto valido
4. metodo de pago soportado
5. mock de pasarela/pago responde exito
6. se registra la compra
7. se actualiza saldo disponible

Resultado:

- compra `confirmed`
- response sugerido: `200`
- tracking esperado:
  - `purchase_registered`

### Fallo porque la factura no existe

Resultado esperado:

- no se crea compra
- no se modifica saldo
- response sugerido: `404`
- no registrar `purchase_registered`

### Fallo porque la factura no esta disponible

Ejemplos:

- factura `rejected`
- factura `funded`
- factura `paid`

Resultado esperado:

- no se crea compra
- no se modifica saldo
- response sugerido: `400`
- no registrar `purchase_registered`

### Fallo por monto invalido

Ejemplos:

- monto mayor al saldo disponible
- monto menor o igual a cero

Resultado esperado:

- no se crea compra
- no se modifica saldo
- response sugerido: `400`
- no registrar `purchase_registered`

### Fallo por metodo de pago no soportado

Resultado esperado:

- no se llama al mock de pago
- no se crea compra
- no se modifica saldo
- response sugerido: `400`
- no registrar `purchase_registered`

### Fallo funcional del mock de pasarela

Esto cubre cuando el mock responde pago rechazado.

Resultado esperado:

- la compra no se confirma
- la factura conserva su saldo disponible
- response sugerido: `402` o `400`
- no registrar `purchase_registered`

Decision recomendada para el equipo:

- usar `400` si quieren simplicidad
- usar `402` si quieren expresar fallo de pago de forma mas semantica

### Falla tecnica del mock de pasarela o banco

Esto cubre timeout, excepcion interna o indisponibilidad tecnica del mock.

Resultado esperado:

- la compra no se registra
- la factura conserva su saldo disponible
- response sugerido: `503`
- mensaje tipo `payment service unavailable`
- no registrar `purchase_registered`

## Politica de tracking frente a fallos

Para mantener el POC simple y consistente:

- nunca registrar eventos de exito si el paso no se completo realmente
- si un flujo falla antes del paso final, el tracking debe quedarse en el ultimo evento exitoso
- no inventar estados de tracking extra salvo que el equipo decida agregarlos formalmente

## Politica de consistencia del POC

Para ambos paths:

- si falla una validacion o mock externo, no se debe avanzar el estado de negocio
- si falla la compra, no se descuenta saldo de la factura
- si falla la publicacion, la factura no debe quedar visible como publicada
- si el equipo decide persistir estados intermedios, debe documentarlo en el modulo correspondiente

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
- estructura para implementar mock SUNAT
- estructura para implementar mock de medio de pago
- tracking minimo
- almacenamiento temporal en memoria

## Que no implementa aun esta primera base

- autenticacion real
- base de datos real
- redis real
- pasarela real
- banco real
- mock SUNAT implementado
- mock de pagos implementado
- payout a empresa vendedora
- dashboard
- wallet real
- cancelacion con penalidad

## Resultado esperado

Dejar una base suficientemente clara y alineada al README para que el equipo empiece a implementar de inmediato, sabiendo exactamente que partes del sistema son reales en el POC y cuales quedan simuladas.
