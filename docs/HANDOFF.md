# Ascent Private Handoff

## 1. Executive Summary

Ascent Private is a public landing page and Telegram-led subscription service for analytical support around the US market, options strategies, scenario modelling, and risk intelligence. The operating production flow is Telegram -> website payment form -> YooKassa -> verified server webhook -> paid Telegram-channel access.

YooKassa is now the active provider for new payments. The next main task is to make the client funnel reliable and visible in Google Sheets, then design and implement a real authenticated client cabinet with access control shared with Telegram.

Use legally careful public language: analytical support, professional consulting, information and analytical materials, scenario modelling, risk intelligence, and independent client decisions. Do not present the product as asset management, brokerage, trades on a client's behalf, individual investment recommendations, signals, guaranteed returns, or risk-free profit.

## 2. Current Project State

### Frontend

- Public landing is implemented with React, TypeScript, Vite, Tailwind, Radix primitives, and local image/font assets.
- The static production entry is `src/static-main.tsx`; `npm.cmd run build:static` creates `dist-static/`, which Nginx serves for `ascentprivate.com`.
- Landing sections are navigation, hero, problem, consulting, process, audience, value proposition, FAQ, CTA, payment footer, cookie banner, and policy pages.
- Footer accepts a payment token supplied by the bot, collects name/email/phone and consent flags, creates a provider payment, then redirects to the provider URL. It records a payment-form lead in Google Sheets as a non-blocking side effect.
- First-party tracking is in `src/lib/tracking.ts`; it stores attribution, sends browser events to the backend, and sends Metrika goals.

### Backend and Telegram bot

- `bot/` is a FastAPI and aiogram application with async SQLAlchemy, Alembic, PostgreSQL, Redis and APScheduler.
- It accepts Telegram updates, starts trial/payment/FAQ flows, creates payment tokens, manages subscriptions, issues one-use channel links, expires access, sends reminders, and reports to email, a support chat, and Google Sheets.
- Backend deployment uses Docker Compose at `/opt/ascent-private-bot`. The application port must stay bound to `127.0.0.1:8000:8000`.

### Payments

- YooKassa is the active provider when `PAYMENT_PROVIDER=YOOKASSA`.
- The website calls `POST /api/payments/yookassa/create`. The endpoint creates or reuses a YooKassa confirmation URL with Basic Auth and an idempotence key.
- `POST /yookassa/webhook` handles `payment.succeeded` and `payment.canceled`. It verifies a success event with a provider GET request and compares amount, currency and payment metadata before granting access.
- The browser return to the site is not payment proof; only a verified webhook activates access.
- Robokassa implementation and result routes are preserved for controlled rollback and historic callbacks. Creating a new Robokassa payment returns `503` while YooKassa is active.
- The server configuration defaults to 8,000 RUB and a 30-day duration. Production has been set to `SUBSCRIPTION_RUB_PRICE=8000` and `ALLOW_REPEAT_TRIAL_FOR_TESTING=false`. Old 1-RUB payment tokens have their historical amount and should not be reused.

### Analytics and reporting

- Site events are stored by `POST /api/events` in PostgreSQL. Attribution includes UTM fields, `yclid`, a first-party client ID, page context and payment token when available.
- Yandex Metrika counter `109523988` and goals are integrated in browser code. Backend contains Metrika and Direct API adapters; marketing automation remains read-only/dry-run.
- Google Sheets integrations cover payment leads, trial users, FAQ events and confirmed payments. Backend report clients follow Apps Script redirects to `script.googleusercontent.com`.

### Client cabinet

- Source includes TanStack routes `/account`, `/account/portfolio`, and `/account/cash`.
- They are static presentation pages without authentication, customer data, API integration, or access checks.
- The public deployment currently uses the separate static entry and therefore does not expose those TanStack routes as a production cabinet.

## 3. Repository Structure

- `src/components/site/` — landing sections, policy pages, payment footer and cookie UI.
- `src/components/ui/` — reusable Radix-style interface primitives.
- `src/lib/tracking.ts` — Metrika, attribution and first-party event delivery.
- `src/static-main.tsx` and `vite.static.config.ts` — static landing build.
- `src/routes/` — TanStack source routes, including the demonstration cabinet pages.
- `bot/app/api/routes/` — health, events, Telegram, payment, Robokassa and YooKassa routes.
- `bot/app/bot/handlers/` — start, trial, payment, FAQ, support, admin and channel-access interactions.
- `bot/app/db/` and `bot/migrations/` — models, repositories and Alembic migrations through `007_add_payment_provider_fields`.
- `bot/app/services/` — providers, subscriptions, channel access, reports, Sheets, email, Yandex and decision safety.
- `bot/app/tasks/` — expiry and reminder scheduler jobs.
- `docs/` — payment, Sheets and analytics operating documentation and implementation plans.
- `scripts/` — static preview, FAQ export and Yandex Direct documentation helper.

## 4. Implemented Pages And Routes

### Static public deployment

- `/` — landing page and payment footer.
- `/cookies-policy` — cookie policy.
- `/private-policy` — personal-data policy.
- Footer uses fragment `#payment` and query parameters `payment_token` and `payment`.

### TanStack source routes, not released as an authenticated cabinet

- `/` — TanStack landing composition.
- `/account` — cabinet landing with portfolio and cash navigation.
- `/account/portfolio` — placeholder portfolio page.
- `/account/cash` — placeholder cash page.

### Backend routes

- `GET /health`
- `POST /telegram/webhook`
- `POST /api/events`
- `POST /api/payments/yookassa/create`
- `POST /api/payments/robokassa/create` — disabled unless the provider setting is Robokassa.
- `GET|POST /robokassa/result`, `/robokassa/success`, `/robokassa/fail`
- `POST /yookassa/webhook`

## 5. Implemented Components

- `Nav`, `Hero`, `Solve`, `Consulting`, `Process`, `Audience`, `Why`, `Faq`, `Cta`, `Footer`, and `CookieBanner` make up the landing.
- `Footer` contains provider-neutral payment creation and the form-lead side effect.
- `CookiePolicyPage` and `PersonalDataPolicyPage` render static policy content.
- Account route components use shared `Nav` and `Footer`, but are intentionally placeholder UI.

## 6. Backend / Bot State

- Users are keyed by unique Telegram ID and record whether the trial has been used.
- Trial starts from `trial_site`, lasts 30 days and is limited to once per Telegram ID when `ALLOW_REPEAT_TRIAL_FOR_TESTING=false`.
- Payment starts from `pay_site`; the bot creates a short-lived internal payment token and sends the site URL.
- Paid subscriptions start immediately after a trial, or extend from the end of an active paid period.
- `channel_access` stores issued links. The expiry job marks subscriptions expired and bans the member from the private channel when no later active subscription exists.
- FAQ searches local data; unmatched questions are forwarded to the support chat and FAQ events are reported to the funnel.
- The scheduler runs expiry and reminder jobs. The app may continue running when Telegram webhook setup times out on startup; investigate recurring network failures rather than treating this as a successful webhook registration.

## 7. Payment Flow State

1. The user enters through a Telegram deep link or the payment CTA.
2. The bot creates a pending payment with an internal token and current configured amount.
3. The landing submits customer details and tracking context to the active provider endpoint.
4. YooKassa returns a confirmation URL; the browser redirects there.
5. YooKassa posts a webhook to `/yookassa/webhook`.
6. Backend fetches the payment from YooKassa and validates the local payment ID, token, Telegram ID, amount, currency and succeeded status.
7. Only then the backend marks payment paid, creates/extends subscription, issues Telegram access, records analytics and sends reports.

Never activate paid access from a browser success return. Register `payment.succeeded` and `payment.canceled` in the YooKassa dashboard for `https://bot.ascentprivate.com/yookassa/webhook`.

## 8. Analytics State

- Browser goals: `page_view_landing`, `cta_click_profile`, `telegram_click`, `form_start`, `form_submit`, `payment_click`, `payment_return_success`, and `scroll_depth_50_75`.
- First-party events remain authoritative when browser Metrika is blocked by tracking protection.
- Attribution preserves UTM source/medium/campaign/content/term, `utm_id`, `yclid`, first/landing URL and referrer.
- Yandex Direct API credentials may be used only for read-only work unless an explicit later approval enables dry run or writes.
- Payment lead rows are written directly to the `Payment Leads` sheet. The master `Client Funnel` sheet combines risk, trial, payment-form, FAQ and paid-payment events by Telegram ID.

## 9. Access Model: Current And Target

### Current

The effective access model is Telegram-only. A user is identified through Telegram, can receive one trial, then receives or loses private-channel access based on subscription expiry. The database has subscription and channel-access records; there is no website account identity, login session, cabinet authorization layer, or single `access_status` field.

### Target

Implement a server-side access state as the single source of truth, for example `trial_active`, `paid_active`, `expired`, and `revoked`. The requested flow is:

```text
Website registration
  -> User account created
  -> 30-day trial access activated
  -> Cabinet access enabled
  -> Telegram account linked through a bot deep link
  -> Private Telegram invite issued
  -> Shared access_status controls cabinet and Telegram
  -> Trial/payment expiry disables both
  -> Verified payment restores both
```

The password should remain stable. Expiry must block access to materials, not mutate a password or delete an account.

## 10. Known Gaps

- The cabinet is demonstration UI only. No registration, authentication, client data store, API authorization or shared access status exists.
- Static deployment does not contain the TanStack account pages.
- `Client Funnel` currently needs the Apps Script function `refreshClientFunnel` after new payment-form leads; automate this refresh or make the event processor record payment-form events directly.
- YooKassa provider and provider payment ID are available in paid-event payloads/raw data but are not yet shown as dedicated visible Client Funnel columns.
- Historical reporting events that failed before redirect following was enabled may require a controlled backfill.
- A complete live `payment.succeeded` test for the final YooKassa production configuration, including subscription, invite, Sheets and reports, should be recorded. Opening a checkout without paying is not that test.
- The bot can experience outbound Telegram webhook setup/support-message network timeouts. The app health endpoint can remain healthy, but delivery should be monitored.
- `bot/.env.example` still contains the prior 1-RUB testing price and duplicate provider comments/lines; align it with the 8,000-RUB production baseline in a separate documentation-only cleanup.

## 11. Priority TODO

1. Run and document one full YooKassa paid-payment test with webhook verification, access issue, Sheets row and admin/support reports.
2. Automate Client Funnel updates after payment-form submission and expose provider/provider payment ID as normal columns.
3. Backfill only confirmed historical reporting events if the audit identifies gaps.
4. Design the account identity, authentication and shared access-status model before implementing a client cabinet.
5. Implement the authenticated cabinet and integrate it with the existing subscription/channel-access services.
6. Resolve persistent outbound Telegram network/webhook timeout behaviour and add focused health/delivery monitoring.

## 12. Validation

This handoff was prepared after source inspection on 2026-08-27. Results from this documentation pass:

- `npm.cmd exec tsc -- --noEmit` — passed.
- `npm.cmd run build:static` — passed.
- Backend syntax compilation with the bundled Python runtime — passed.
- `npm.cmd run lint` — did not finish within the 30-second command window and printed no diagnostics. Treat it as not run to completion; run it separately before a code release.
- No automated test suite was found in the repository during this pass.

Run these checks after code changes:

```powershell
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build:static
```

```powershell
python -m compileall -q bot\app
```

When local Python is unavailable, use the bundled Codex runtime instead.

VPS verification:

```bash
cd /opt/ascent-private-bot
docker compose up -d --build app
docker compose exec app alembic upgrade head
docker compose ps
docker compose logs --tail=80 app
docker compose exec app curl -i http://127.0.0.1:8000/health
curl -i https://bot.ascentprivate.com/health
ss -tulpn | grep 8000
```

Expected port binding: `127.0.0.1:8000->8000/tcp`.

## 13. Notes For Next Agent

- Preserve the dirty worktree. `bot/` and several documentation/static files may be untracked or user-owned; do not reset, clean or bulk-replace them.
- Work in small diffs. Run static build after frontend changes and add an Alembic migration for data-model changes.
- Never expose the backend port publicly, print secrets, or treat a browser payment return as confirmation.
- Keep marketing automation read-only unless the user explicitly authorizes a safer later phase.
- For the live deployment, distinguish source state from what has actually been copied to `/opt/ascent-private-bot`; verify the container code and logs after every manual upload.
- Read this file together with `AGENTS.md`, `docs/yookassa-implementation-execplan.md`, and the applicable Google Sheets document before touching payments or reporting.

## 14. Cabinet Phase 1 Audit (2026-08-27)

- The active cabinet specification is `docs/ascent_private_cabinet_tz_codex.md`; the implementation plan is `docs/ascent-private-cabinet-execplan.md`.
- `build:static` uses `src/static-main.tsx`, which renders the public landing and policy pages only. Existing TanStack `/account`, `/account/portfolio`, and `/account/cash` source routes are demonstration UI and are not included in the static production entry.
- Existing backend access is Telegram-centric: `User` requires a Telegram ID; trial/paid subscriptions, channel access, expiry, and the verified YooKassa webhook operate through that model. Phase 2 must add website identity additively and preserve this flow.
- SMTP send code and the latest local Alembic revision (`007_add_payment_provider_fields`) exist, but production SMTP delivery, applied VPS revision, and the `ascentprivate.com` Nginx server block were not available from this workspace. Verify them manually before cabinet deployment; do not print environment values or secrets.
- No migrations, API routes, frontend routes, auth logic, static build, or Nginx configuration were changed during Phase 1.

## 15. Cabinet Phase 2 Source State (2026-08-27)

- Added additive migration `008_add_web_account_auth` for website accounts, website-only trial entitlements, PostgreSQL-backed sessions, and account audit events.
- Added `/api/auth` endpoints for registration, email confirmation, login by email or normalized Russian phone, session lookup/logout, password change, confirmation resend, and password reset.
- Email confirmation creates a 30-day website `trial_active` entitlement. It does not alter the legacy Telegram subscription, payment, channel-access, YooKassa webhook, or scheduler flows; shared access remains Phase 3 work.
- The temporary password is generated once after email confirmation and is never resent. Lost credentials use the password-reset flow.
- New VPS variables are documented in `bot/.env.example`: auth token/session lifetimes, cookie name, public backend URL and development CORS origins. Add them to `/opt/ascent-private-bot/.env` before deploying.
- Local unit tests for phone normalization and password hashing passed. A local Python executable with FastAPI/SQLAlchemy and Docker are not available in this workspace, so Alembic upgrade, full API import, SMTP delivery, container build, and health check must be performed on a provisioned environment.

## 16. Cabinet Phase 6 UX Requirement (2026-08-27)

- Do not implement this requirement in Phase 2. It does not authorize frontend, static-routing, Nginx, header, or form changes now.
- All future cabinet pages must reuse the visual language of the existing AscentPrivate.com landing: dark graphite background, muted gold accents, ivory/soft-white primary text, warm-grey secondary text, and premium private-banking plus AI styling. Avoid generic dashboard and light SaaS admin-panel styling.
- Phase 6 adds `Регистрация` and `Вход` to the public header using the existing site button system: matching radius, gold/dark treatment, hover behavior, typography, and spacing.
- Phase 6 registration and login forms must visually match the existing payment form card, fields, spacing, dark premium background, gold accents, consent/link styling, and structured calm presentation.

## 17. Cabinet Phase 2.5 Validation And Hardening (2026-08-27)

- Registration now rejects unknown JSON fields, including `password`; the flow accepts only its declared name, email, phone, consent and optional attribution fields.
- A concurrent unique-email or unique-phone database insert is translated to HTTP 422 instead of a server error. Existing normalization and pre-insert duplicate checks remain in place.
- Added `bot/tests/test_auth_contract.py` for the no-password registration contract, safe `/me` summary shape, production session-cookie flags and CORS origin configuration. These tests run when FastAPI/SQLAlchemy dependencies are present.
- Production CORS no longer includes development localhost origins when credentials are enabled; configured dev origins are used only outside `APP_ENV=production`.
- The bundled local Python passed `compileall` and the dependency-free security tests. It skipped five FastAPI contract tests because this workspace has no installed backend dependencies; Docker is also unavailable, so PostgreSQL migration/API, SMTP delivery, CORS preflight and `/health` remain mandatory VPS checks.
- Phase 2.5 did not modify Telegram start parameters, payment routers/webhooks, channel access, scheduler, or legacy subscription behavior.

## 18. Cabinet Phase 2 Acceptance And Password Policy (2026-09-02)

- Phase 2 infrastructure and end-to-end auth validation passed on the VPS: migration 008, PostgreSQL tables, container compile check, health check, production-only port binding, SMTP delivery, confirmation, login by email and phone, safe `/api/auth/me`, password reset, logout, session revocation and credentialed production CORS preflight.
- MVP password policy is a product decision: user-selected change-password and reset-password values must be 8–256 characters and include at least one letter and one digit. Do not increase this minimum without a new explicit product decision.
- The generated one-time temporary password remains 16 random characters. It is not the minimum-policy value and must not be resent.
- Password and reset-token fields are secret values. Validation responses must never reflect their submitted contents.
