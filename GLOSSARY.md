# eox-paygate

Paygate payment processor for `openedx-zeitlabs-payments`: lets any Open edX site that uses that plugin charge learners through the Paygate payment gateway.

## Language

### Gateway

**Paygate**:
The PPAP PayGate payment gateway by Optimistic Blue, reached through its REST API and its hosted payment page.
_Avoid_: PayGate widget (when meaning the whole gateway)

**Hosted payment page**:
The Paygate page the learner is sent to with a session token to choose a payment type and pay.
_Avoid_: Widget, checkout page

**Payment type**:
A way of paying offered on the hosted payment page, such as VISA, MB WAY or a Multibanco reference.
_Avoid_: Payment method, card type

**Deferred payment type**:
A payment type whose payment is completed after the learner leaves the hosted payment page, such as a Multibanco reference (REFMB) or a DUC.
_Avoid_: Async method, offline payment

### Identifiers

**Payment reference**:
The merchant's reference for a payment, sent to Paygate as `PAYMENT_REF`; it identifies the cart and may match several Paygate payments.
_Avoid_: Order number, order reference

**Payment ID**:
Paygate's own unique identifier for a single payment.
_Avoid_: Transaction ID, gateway order id

### Settlement

**Server callback**:
The server-to-server notice Paygate sends to the merchant when a payment changes state.
_Avoid_: Webhook, IPN, server notification

**Callback key**:
The merchant-level secret Paygate includes in every server callback.
_Avoid_: Signature, API key
