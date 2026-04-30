# POC de Factoring - Analisis de Arquitectura para Happy Path y Critical Path

## Objetivo

Este documento analiza unicamente los dos paths pedidos para el POC en FastAPI:

- Happy path: `compra de una factura`
- Critical path: `POST /facturas` con resultado exitoso y fallido

La fuente de verdad para este analisis es solo lo visible en los diagramas compartidos. No se asume comportamiento adicional fuera de lo que la arquitectura muestra.

## Veredicto Ejecutivo

La arquitectura es suficiente para disenar el POC y delimitar modulos, actores, endpoints y secuencia general de interaccion.

No es suficiente para implementar estos paths sin completar contratos minimos, estados y algunas reglas de negocio clave. En particular, faltan definiciones sobre pagos, tracking, validaciones de negocio y manejo de compras parciales.

## Alcance del POC Analizado

### Actores relevantes

- `Empresa vendedora`: sube la factura para venderla en la plataforma.
- `Inversionista`: compra una factura o parte de ella en la plataforma.
- `Empresa deudora`: actor externo de negocio; es quien finalmente debe pagar la factura.

### Estilo arquitectonico

- Monolito modular con frontend web.
- Backend orientado a servicios internos implementables como modulos en FastAPI.
- Persistencia central en base de datos relacional.
- Integraciones externas visibles en la arquitectura:
  - `SUNAT API`
  - `Pasarela de pagos`
  - `Servicio bancario`
  - `Redis` para cache/sesion/validacion rapida

### Modulos involucrados directamente

- `Modulo de Facturas`
- `Modulo de Marketplace` o compra/venta de facturas
- `Modulo de Pagos`

### Dependencias minimas implicitas

- `Modulo de Usuarios y Autenticacion`
- `Modulo de Tracking`
- `Modulo de Wallet` para el caso del inversionista

## Lo explicito en la arquitectura

## Modulos y servicios identificados

Desde los diagramas se pueden extraer estos servicios o capacidades:

- `Auth & User Service`
- `Factoring Service`
- `Validation & SUNAT Service`
- `Tracking & Dashboard Service`
- `Payment Service`
- `Scheduler Service`
- `API Gateway`

En el diagrama funcional tambien aparecen servicios intermedios o subflujos:

- `Invoice upload service`
- `Validacion de facturas service`
- `Encolamiento en SUNAT service`
- `Factura rechazada service`
- `Evaluacion de empresa compradora service`
- `Publicacion de la factura service`
- `Registro de compra service`
- `Recaudacion service`
- `Cobro de inversion service`
- `Validacion de pago service`
- `Publicacion de pago service`
- `Pago a la empresa vendedora service`

## Endpoints sugeridos por la arquitectura

Los diagramas muestran explicitamente o implican estos endpoints:

- `POST /login`
- `GET /users/me`
- `POST /facturas`
- `GET /facturas`
- `POST /facturas/{id}/comprar`
- `POST /facturas/{id}/cancelar`
- `POST /validate_invoice`
- `POST /wallet/deposit`
- `POST /wallet/withdraw`
- `POST /insurance/buy`
- `GET /dashboard/portfolio`
- `GET /facturas/{id}/tracking`
- `GET /ranking/companies`

## Happy Path: compra de una factura

## Objetivo del flujo

Permitir que un inversionista autenticado compre una factura publicada o parte de ella y que la operacion quede registrada con tracking.

## Precondiciones minimas derivadas de la arquitectura

- El inversionista ya existe y esta autenticado.
- La factura ya fue cargada, validada y publicada previamente.
- La factura esta disponible para compra.
- El inversionista conoce el porcentaje de interes y el monto total esperado a cobrar.
- Existe un mecanismo para pagar la compra:
  - wallet
  - pasarela
  - o una combinacion, aunque eso no queda definido en la arquitectura

## Secuencia que si sugiere la arquitectura

1. El inversionista interactua con el frontend.
2. El request entra por el `API Gateway`.
3. El gateway enruta y autentica hacia `Factoring Service`.
4. `Factoring Service` coordina la compra de la factura.
5. Se invoca `Payment Service` para procesar el medio de pago.
6. Se registra la compra en el flujo de `Registro de compra service`.
7. Se actualiza `Tracking & Dashboard Service`.
8. La compra queda confirmada y asociada al inversionista.

## Resultado minimo esperado para el POC

- La compra queda registrada.
- La factura reduce su saldo disponible o reserva una participacion.
- Se calcula el retorno esperado del inversionista.
- El tracking refleja que la compra fue registrada.

## Critical Path: POST /facturas

## Objetivo del flujo

Permitir que una empresa vendedora suba una factura y que el sistema la publique si supera todas las validaciones; si no, debe rechazarla con motivo.

## Rama exitosa derivada del diagrama

1. La empresa vendedora envia la factura por frontend.
2. El request entra por `API Gateway`.
3. El gateway autentica y enruta a `Factoring Service`.
4. `Factoring Service` guarda o inicia el registro de la factura.
5. Se ejecuta la validacion interna de datos.
6. Se ejecuta `POST /validate_invoice` en `Validation & SUNAT Service`.
7. El servicio consulta o contrasta la factura con `SUNAT API`.
8. Si SUNAT responde aceptado, continua la validacion de negocio.
9. Se evalua la empresa compradora o deudora.
10. Si la evaluacion es aceptada, la factura se publica.
11. El tracking registra que la factura fue subida, validada y publicada.

## Rama fallida derivada del diagrama

1. La empresa vendedora envia la factura.
2. La factura entra a validacion interna y/o validacion SUNAT.
3. Si falla la validacion documental, SUNAT o la evaluacion de negocio:
   - la factura queda `rejected`
   - se registra un `rejection_reason`
   - el tracking debe mostrar el rechazo

## Observacion importante del diagrama

`Pago a la empresa vendedora service` aparece conectado al flujo de validacion/publicacion, pero la arquitectura no deja claro si ese pago:

- ocurre al publicar la factura
- ocurre al ser comprada
- o ocurre al completarse el fondeo de la factura

Para este POC, conviene dejarlo fuera del `POST /facturas` y tratarlo como una fase posterior al fondeo.

## Propuesta minima de contratos para poder implementar el POC

## 1. POST /facturas

### Request minimo propuesto

```json
{
  "ruc_emisor": "20123456789",
  "ruc_pagador": "20987654321",
  "serie": "F001",
  "correlativo": "12345",
  "monto": 15000.50,
  "fecha_emision": "2026-04-29",
  "fecha_vencimiento": "2026-06-15",
  "tasa_interes": 0.12,
  "archivo_xml": "base64-o-referencia"
}
```

### Reglas minimas propuestas

- `seller_id` se toma del token y no del body.
- `monto` debe ser mayor a cero.
- `fecha_vencimiento` debe ser posterior a `fecha_emision`.
- `serie + correlativo + ruc_emisor` deben identificar de forma unica la factura.

### Response minimo propuesto

```json
{
  "invoice_id": "inv_001",
  "status": "published",
  "message": "Factura validada y publicada",
  "rejection_reason": null
}
```

### Response fallido propuesto

```json
{
  "invoice_id": "inv_001",
  "status": "rejected",
  "message": "Factura rechazada",
  "rejection_reason": "SUNAT validation failed"
}
```

## 2. POST /validate_invoice

### Request minimo propuesto

```json
{
  "ruc_emisor": "20123456789",
  "ruc_pagador": "20987654321",
  "serie": "F001",
  "correlativo": "12345",
  "monto": 15000.50
}
```

### Response minimo propuesto

```json
{
  "is_valid": true,
  "source": "sunat_mock",
  "observations": [],
  "rejection_reason": null
}
```

## 3. POST /facturas/{id}/comprar

### Request minimo propuesto

```json
{
  "amount": 5000.00,
  "payment_method": "yape",
  "use_wallet_balance": false,
  "insurance_opt_in": false
}
```

### Response minimo propuesto

```json
{
  "purchase_id": "pur_001",
  "invoice_id": "inv_001",
  "status": "confirmed",
  "owned_fraction": 0.3333,
  "expected_return": 5600.00,
  "tracking_status": "purchase_registered"
}
```

## Estados minimos propuestos

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

## Lo que falta definir en la arquitectura

Estos puntos no quedan cerrados solo con los diagramas y deben tratarse como observaciones abiertas:

- No se define si la compra se paga desde `wallet`, directo por `pasarela`, o por una combinacion de ambos.
- Los requerimientos mencionan `efectivo`, `tarjeta`, `Yape`, `Plin` y `transferencia`, pero la pasarela del diagrama solo muestra `Yape`, `Plin` y `Tarjeta`.
- No esta definido como se maneja la compra parcial:
  - porcentaje minimo
  - monto minimo
  - redondeo
  - agotamiento del saldo disponible
- No esta definido en que momento se paga a la empresa vendedora.
- No esta definido el contrato exacto con `SUNAT API`.
- No esta definido que datos de validacion se cachean en `Redis`.
- No esta definido que informacion usa la evaluacion de la empresa compradora o deudora ni sus criterios de aceptacion.
- No esta definido si el tracking se implementa como eventos, tabla de estados o historial transaccional.
- La cancelacion con penalidad existe como requerimiento, pero no forma parte de estos dos paths.
- El retiro de dinero y el payout al vencimiento pertenecen al flujo completo, pero no al alcance inmediato de este README.

## Suficiencia de la arquitectura para codear el POC

## La arquitectura si resuelve

- Actores principales del negocio
- Modulos centrales del sistema
- Integraciones externas relevantes
- Endpoints base del POC
- Secuencia general de publicacion y compra

## La arquitectura no resuelve por si sola

- Contratos request/response completos
- Modelo de estados exacto
- Reglas de negocio de compra parcial
- Politica de medios de pago del POC
- Criterios de rechazo de negocio
- Modelo de tracking persistente

## Conclusion

La arquitectura ya es suficiente para empezar a codear el POC solo si antes se aceptan los contratos minimos y supuestos propuestos en este documento. Sin esas decisiones, el equipo tendria que improvisar detalles importantes durante la implementacion.

## Casos de prueba recomendados

## POST /facturas

- Caso exitoso: factura valida en datos, aceptada por SUNAT y publicada.
- Caso fallido por SUNAT: la factura se rechaza y se devuelve `rejection_reason`.
- Caso fallido por validacion de negocio: la factura se rechaza aunque SUNAT la valide.

## POST /facturas/{id}/comprar

- Caso exitoso: compra valida con metodo de pago soportado.
- Caso fallido por monto: el monto solicitado supera el saldo disponible de la factura.
- Caso fallido por metodo de pago: se intenta comprar con un metodo no soportado por el POC.

## Tracking

- El tracking muestra `invoice_uploaded`, `sunat_validated` e `invoice_published` despues de una publicacion exitosa.
- El tracking muestra `purchase_registered` despues de una compra exitosa.

## Supuestos y defaults para dejarlo implementable

- El POC sera sincronico dentro del monolito aunque el diagrama sugiera pasos tipo cola o encolamiento.
- `Auth` se trata como dependencia minima obligatoria, sin profundizar en su implementacion interna.
- `Tracking` se modela de forma minima en la misma base de datos del monolito.
- `SUNAT API`, `pasarela de pagos` y servicios bancarios pueden simularse o mockearse en el POC.
- `Pago a la empresa vendedora` queda fuera del `POST /facturas` y se considera una fase posterior al fondeo o compra efectiva.

## Recomendacion final para implementacion

Si el siguiente paso es codear, el equipo deberia tomar este README como contrato inicial del POC y fijar primero:

1. El modelo de estados.
2. Los contratos minimos de `POST /facturas`, `POST /validate_invoice` y `POST /facturas/{id}/comprar`.
3. La politica de medios de pago soportados en esta iteracion.
4. La forma minima de tracking persistente.

Con esas decisiones, el POC ya queda lo bastante especificado para implementar los dos paths sin inventar comportamiento critico sobre la marcha.
