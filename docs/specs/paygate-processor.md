# Paygate processor for openedx-zeitlabs-payments

## Problem Statement

Open edX operators who charge learners through Paygate relied on a Paygate payment processor for the Open edX ecommerce service. That service is deprecated, and its replacement, `openedx-zeitlabs-payments`, has no Paygate processor. Operators who move to `openedx-zeitlabs-payments` cannot offer Paygate's payment types (cards, PayPal, MB WAY, Multibanco references, DUC) to their learners.

## Solution

`eox-paygate` is a pip-installable plugin that adds a Paygate processor to `openedx-zeitlabs-payments` without changing that plugin or `openedx-platform`. It has functional parity with the existing ecommerce Paygate plugin (`fccn/ecommerce-plugin-paygate`), adapted to the zeitlabs processor contract `v1`. It also avoids that plugin's known bugs.

An operator installs the package and configures Paygate per site. Learners on that site can then choose Paygate at checkout and pay on Paygate's hosted payment page. When the payment completes, the cart is settled: the invoice is created and the learner is enrolled. This happens when the learner returns from Paygate, or later through Paygate's server callback for deferred payment types. Support staff can check a cart's payment against Paygate from the Django admin and recover payments whose server callback was lost. Sites without Paygate configuration see no trace of it.

The Paygate API reference is its published swagger (`/paygateWS/swagger/v3/swagger.json` on the Paygate host). The ecommerce plugin is a functional reference only.

## User Stories

1. As a learner, I want to see a "Pay with Paygate" option at checkout, so that I can pay with the payment types my site offers through Paygate.
2. As a learner, I want to be sent to Paygate's hosted payment page with my cart's amount and description already set, so that I don't have to type payment details twice.
3. As a learner, I want the hosted payment page in my language when Paygate supports it, so that I understand what I am paying for.
4. As a learner, I want to pay by card (VISA, MASTERCARD, AMEX), so that I am enrolled immediately.
5. As a learner, I want to pay with PayPal, so that I can use my PayPal account.
6. As a learner, I want to pay with MB WAY, so that I can confirm the payment on my phone.
7. As a learner, I want to pay with a Multibanco reference (REFMB), so that I can pay later at an ATM or in home banking.
8. As a learner, I want to pay with a DUC, so that I can use that payment document.
9. As a learner, after paying on the hosted payment page, I want to come back to the site and see that my payment succeeded, so that I know I am enrolled.
10. As a learner who chose a deferred payment type, I want to see that my payment is pending instead of an error, so that I know I still have to complete it.
11. As a learner who pays a Multibanco reference or DUC days later, I want to be enrolled without doing anything else on the site, so that paying is all I need to do.
12. As a learner who cancels on the hosted payment page, I want to come back to the site and see that the payment was cancelled, so that I can try again.
13. As a learner whose payment is declined, I want to come back to the site and see that it failed, so that I can try another payment type.
14. As a learner, I want never to be charged twice or enrolled twice for one cart because Paygate notified the site more than once, so that duplicate notices cause no harm.
15. As a learner who paid but was not enrolled, I want support staff to be able to verify my payment against Paygate and settle my cart, so that my problem is solved quickly.
16. As a site operator, I want to install `eox-paygate` next to `openedx-zeitlabs-payments` and have the processor registered automatically, so that I don't have to change zeitlabs or the platform.
17. As a site operator, I want to configure Paygate per site in `PAYGATE_SETTINGS`, through the site configuration or Django settings, so that each site in a multi-tenant instance can use its own Paygate merchant or none.
18. As a site operator, I want to set the Paygate API base URL myself, with no URL built into the code, so that I decide whether a site talks to Paygate's test or production environment.
19. As a site operator, I want to configure the access token, merchant code, Basic auth user and password, and callback key, so that the processor can authenticate against Paygate and verify Paygate's server callbacks.
20. As a site operator, I want to configure which payment types are offered, defaulting to VISA, MASTERCARD, AMEX, PAYPAL, MBWAY, REFMB and DUC, so that I only offer the types my merchant has enabled.
21. As a site operator, I want the processor hidden at checkout on any site without a usable Paygate configuration, so that learners never see a processor that cannot work.
22. As a site operator, I want a single server callback URL for Paygate to call, so that I can register it in my Paygate merchant set-up.
23. As a site operator, I want server callbacks with a wrong or missing callback key rejected without effect, so that nobody can settle carts by calling the URL.
24. As a site operator, I want every server callback verified against Paygate's API before a cart is settled, so that a forged or leaked callback cannot mark a cart as paid.
25. As a site operator, I want the amount and currency Paygate reports compared against the cart, so that an underpaid or wrong-currency payment is never settled as paid.
26. As a site operator, I want access tokens, passwords and the callback key kept out of logs and out of the transaction data the plugin stores, so that credentials do not leak through the database or log shipping.
27. As a site operator, I want a management command that finds payments completed in Paygate within a time window and settles carts that were not settled, so that I can recover after an outage in which server callbacks were lost.
28. As a site operator, I want that management command to accept a single payment reference, so that I can recover one learner's payment.
29. As a site operator, I want the management command to skip carts that are already settled and to report what it did, so that running it twice is safe.
30. As support staff, I want a "Check payment in Paygate" action on the cart admin of a site with Paygate configured, so that I can settle a paid cart from the admin.
31. As support staff, I want a "Mark test payment as paid" action on the cart admin of a site with Paygate configured, so that I can simulate a completed deferred payment in Paygate's test environment and exercise the server callback.
32. As support staff, I want a clear admin message for each selected cart: settled, still pending, not a Paygate cart, not found in Paygate, or Paygate error, so that I know what happened to each one.
33. As support staff on a site without Paygate configuration, I want the cart admin to look exactly like the standard zeitlabs one, so that Paygate actions don't appear where they cannot work.
34. As a developer, I want the processor to rely only on the zeitlabs processor contract `v1` and its public settlement logic, so that it keeps working as zeitlabs evolves.
35. As a developer, I want every behaviour written test-first (TDD), so that each piece of code exists because a failing test required it.
36. As a developer, I want 100% test coverage enforced in CI from the first commit, so that no untested code is merged.
37. As a developer, I want GitHub Actions to run the tests on Python 3.11 with Django 4.2 and Python 3.12 with Django 5.2, so that the plugin keeps working on the Open edX releases in use.
38. As a developer, I want the README to document installation, every setting, the server callback URL, the admin actions, the management command and a manual end-to-end test procedure against Paygate's test environment, all in English, so that operators and testers can use the plugin without reading the code.

## Implementation Decisions

**Packaging and registration**
- The existing scaffold stays: the processor is registered through the `zeitlabs_payments.v1` entry point under the slug `paygate`, and the package installs as an LMS Django app through `lms.djangoapp`.
- `openedx-zeitlabs-payments` and `openedx-platform` are not modified. Everything lives in `eox-paygate`.

**Configuration**
- All configuration lives in `PAYGATE_SETTINGS`. It is read through the zeitlabs settings service, which reads the current site's configuration first and Django settings otherwise. Configuration from other sites is never consulted.
- Keys: API base URL, access token, merchant code, Basic auth user, Basic auth password, callback key, payment types (with the default list above), and request timeouts with sensible defaults.
- The code contains no Paygate URL, neither test nor production.
- The processor exposes a single "is enabled" check: true when the required keys are present for the current site. It drives both the checkout visibility (`is_hidden_for`) and the admin actions' visibility.
- `eox-paygate` stores no credentials. How the operator's site configuration or settings store them is outside this plugin's responsibility.

**Paygate API client**
- A small client module wraps the Paygate REST operations used: `CheckOut`, a single-payment status lookup by Payment ID, a search of completed payments by time window or payment reference, and `MarkTestPaymentAsPaid`.
- All calls are JSON POSTs with HTTP Basic auth, plus `ACCESS_TOKEN` and `MERCHANT_CODE` in the body.
- Amounts are sent as JSON numbers in `XXXXX.XX` format. Serialization must not depend on `simplejson` being installed.
- Network errors, timeouts, non-200 responses, non-JSON bodies and `Success: false` answers become a gateway error.
- Credentials are scrubbed from anything logged or stored.

**Identifiers**
- **Payment reference** (`PAYMENT_REF`) is the zeitlabs order reference `<site_id>-<cart_id>`. It fits Paygate's 32-character SIBS limit.
- **Payment ID** is the transaction id recorded in zeitlabs. Paygate guarantees it is unique per payment, which zeitlabs needs for duplicate detection.
- Return and server callback URLs are built by `eox-paygate` with the payment reference in their query string, so nothing depends on Paygate's undocumented appended parameters.

**Payment initiation**
- `get_transaction_parameters` calls `CheckOut` with:
  - the cart's payment reference, description, amount and currency;
  - the learner's name, email and language;
  - the configured payment types;
  - success, cancel and failure return URLs, and the server callback URL, all absolute.
- The learner is sent to the hosted payment page with the returned session token.
- Billing address and REFMB/DUC validity dates are not sent, for parity.

**Return and status (zeitlabs contract `v1`)**
- The return view accepts GET and POST, because the method Paygate uses to return the learner is undocumented. Which one stays is decided during manual testing against Paygate's test environment.
- The status view looks up the payment in Paygate and maps Paygate status codes to zeitlabs payment statuses:
  - `C` → success;
  - `P` → pending;
  - `E` → declined;
  - `X` → cancelled.
- `D` (refunded) and `A` (pre-authorized) are never settled.
- `verify_success_response` checks that the answer belongs to this merchant and this cart.
- `reconcile_payment` compares the paid amount and currency with the cart.
- `get_transaction_details` returns the Payment ID, the payment type, the amount, the currency and a reason.
- Deferred payment types leave the cart pending, and the learner sees a pending outcome, not an error.

**Server callback**
- `eox-paygate` mounts its own server callback URL through its Django plugin URL configuration. zeitlabs contract `v1` has no callback route, and zeitlabs is not modified.
- Verification:
  1. Reject the callback (4xx, no effect) unless the callback key in the body matches the configured callback key.
  2. Ignore every other field in the body except the Payment ID.
  3. Look the payment up in Paygate's API by Payment ID.
  4. Settle only through zeitlabs' public settlement logic (`process_payment_and_update_records`), applying the same status mapping, verification and reconciliation as the status view.
- There is no IP allow-list.
- The view answers 200 once the callback has been handled, including when the cart was already settled. It answers non-2xx only when Paygate should retry.
- Duplicate and concurrent callbacks are safe. zeitlabs' conditional cart transitions and unique `(gateway, transaction id)` constraint already guarantee this; the processor must not bypass them.

**Recovery management command**
- The command searches Paygate for completed payments in a time window, or for one payment reference, and settles every matching cart that is not settled yet. It goes through the same verification and settlement path as the server callback, calling it directly, not by HTTP to itself.
- The command reports, per payment, one of: settled, already settled, not found, or error.
- It is run manually by the operator. No scheduling, cron or Celery task is shipped.

**Admin actions**
- `eox-paygate` re-registers zeitlabs' cart admin with a subclass that adds two actions:
  - "Check payment in Paygate": looks up and settles, through the same path as the server callback.
  - "Mark test payment as paid": calls `MarkTestPaymentAsPaid`, which Paygate only allows in its test environments.
- The actions appear only when Paygate is enabled for the site of the current request (`get_actions`). On other sites the admin is unchanged.
- Each selected cart gets its own result message. A failure on one cart does not stop the others.
- Known limitation, to document: if another plugin also re-registers the cart admin, the last registration wins.

## Testing Decisions

- **Test-first:** every behaviour is driven by a test that is written and seen failing before the production code that makes it pass.
- **What makes a good test:** it exercises external behaviour through public entry points and asserts observable outcomes:
  - HTTP requests sent to Paygate;
  - HTTP responses and redirects;
  - cart status, transactions and invoices recorded by zeitlabs;
  - admin messages;
  - command output.

  It does not assert on private methods or call order.
- **Unit tests only:** the component under test is `eox-paygate`. There are no integration tests against Paygate.
- **Isolation:**
  - Outbound HTTP to Paygate is always simulated at the transport level, for example with `responses` over `requests`. The ecommerce plugin mocked its client's internal request method, so its HTTP and auth layer was never covered; that is not repeated.
  - `openedx-platform` is replaced by zeitlabs' `edx-platform` mocks.
  - `openedx-zeitlabs-payments` is installed in the test environment, as zeitlabs' own processor tests do.
- **Entry points under test:**
  1. zeitlabs' payment initiation for the `paygate` processor, checking the `CheckOut` payload and the redirect to the hosted payment page;
  2. the return view, with GET and POST;
  3. the status view, for each Paygate status code;
  4. the server callback: valid, invalid and missing callback key, unknown payment, amount mismatch, duplicate and already-settled carts;
  5. the admin actions: visibility per site and per-cart results;
  6. the management command: window, single reference, already settled, errors;
  7. processor visibility with complete, partial and missing configuration;
  8. the absence of credentials in logs and stored transaction data.
- **Prior art:**
  - zeitlabs' test utilities: the `edx-platform` mocks, the fixture pattern that registers a processor in the processor registry, and the dummy processor;
  - zeitlabs' tests of the return and status view mixins against the mounted routes;
  - tox installing `openedx-zeitlabs-payments` as a dependency.
- **CI:**
  - A GitHub Actions workflow (none exists today) runs tox on Python 3.11 + Django 4.2 and Python 3.12 + Django 5.2, plus quality checks.
  - Coverage must be 100%, with `fail_under = 100`, from the first commit.
- **Manual end-to-end:** the developer runs it in a staging environment against Paygate's test environment, following the procedure in the README. It covers each payment type, the return HTTP method, and the server callback via "Mark test payment as paid". It is not automated.

## Out of Scope

- Refunds through Paygate's `DoRefund`. This is a follow-up once zeitlabs supports refunds.
- Migrating orders, transactions or references from the deprecated ecommerce service.
- REFMB/DUC validity dates, and any expiry handling beyond zeitlabs' own cart session expiry.
- Scheduled or automatic recovery (cron, Celery beat).
- Payment types or Paygate features beyond the ecommerce plugin's: wallets, pre-authorization, recurring payments, QR codes, Google Pay or Apple Pay as defaults.
- An IP allow-list for the server callback.
- Proposing a generic server callback route to zeitlabs upstream.
- Any change to `openedx-zeitlabs-payments` or `openedx-platform`.
- Automated tests against Paygate's test or production environment.

## Further Notes

- The Paygate swagger leaves several points undocumented:
  - the HTTP method and parameters used to return the learner;
  - the server callback retry policy;
  - whether a callback fires when a pending reference expires.

  The design avoids depending on any of them, and the manual end-to-end test settles the return method.
- The swagger contradicts itself on `success` for status `A`. Settlement relies only on the status code looked up through the API.
- Known zeitlabs limitations that also affect this processor:
  - A second success with a different Payment ID on an already-paid cart is not recorded.
  - Concurrent status polls may answer `not_fulfilled` while another settles.
- Domain vocabulary is in `GLOSSARY.md`.

