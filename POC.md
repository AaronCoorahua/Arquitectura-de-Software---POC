# POC de Factoring

## Objetivo

Construir un POC en FastAPI centrado en dos flujos:

- Happy path: compra de una factura.
- Critical path: `POST /facturas` con resultado exitoso y fallido.

## Alcance funcional

El POC implementa de forma mínima:

- Registro de facturas por una empresa vendedora.
- Validación interna de la factura.
- Validación mock de SUNAT.
- Publicación de la factura si pasa validaciones.
- Compra total o parcial de una factura por un inversionista.
- Tracking básico del estado de la factura y de la compra.

## Supuestos del POC

- La implementación será síncrona dentro de un monolito modular.
- SUNAT, pasarela de pagos y servicios bancarios se simulan.
- El tracking se persistirá de forma mínima.
- El pago a la empresa vendedora queda fuera de este alcance.
- `seller_id` e `investor_id` se tratan como datos de aplicación o mock.

## Contratos mínimos considerados

### `POST /facturas`

Permite registrar una factura, validarla y publicarla o rechazarla.

### `POST /validate_invoice`

Permite validar una factura contra una fuente mock de SUNAT.

### `POST /facturas/{id}/comprar`

Permite registrar la compra total o parcial de una factura publicada.

## Estados mínimos

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

## Repartición sugerida para equipo de 4

### Integrante 1: Facturas

- `POST /facturas`
- reglas de validación
- estados de factura

### Integrante 2: Validación

- `POST /validate_invoice`
- integración mock SUNAT
- criterios de rechazo

### Integrante 3: Marketplace

- `POST /facturas/{id}/comprar`
- compra parcial
- cálculo de retorno esperado

### Integrante 4: Tracking y soporte

- tracking por factura y compra
- listados y consultas
- soporte transversal de configuración y pruebas

## Estructura base elegida

El backend se organiza por módulos para evitar cruces entre integrantes:

- `facturas`
- `marketplace`
- `tracking`
- `validation`
- `shared`

## Resultado esperado de esta primera base

Dejar una estructura lista para que el equipo continúe con implementación, pruebas y persistencia real sin redefinir contratos ni modelos principales.
