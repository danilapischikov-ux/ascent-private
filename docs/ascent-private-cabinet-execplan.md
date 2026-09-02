# Ascent Private Cabinet: identity, calendar PDFs, and shared access

This ExecPlan is a living document. Maintain its `Progress`, `Surprises & Discoveries`, `Decision Log`, and `Outcomes & Retrospective` sections as work proceeds. Follow `PLANS.md` in the repository root when changing this plan.

## Purpose / Big Picture

After this work, a client can register with a name, email, and phone number, confirm the email, receive a temporary password, and sign in using either email or phone. A confirmed client receives one 30-day trial. The cabinet shows access status and a calendar of analytical PDF materials. A client with active access can open or download the selected date's PDF; an expired client can sign in and see the calendar preview, but cannot obtain a PDF URL or content. Telegram access and the cabinet use the same server-side entitlement, and a verified YooKassa webhook—not a browser return—restores paid access.

## Progress

- [x] 2026-08-27: Completed the read-only repository audit for Phase 1.
- [ ] Verify the production Nginx configuration and applied Alembic revision on the VPS without exposing secrets.
- [x] 2026-08-27: Implemented Phase 2 source changes: website identity, confirmation/reset tokens, PostgreSQL sessions, temporary-password flow, and auth routes. Database migration, SMTP delivery, and health validation remain environment-dependent manual checks.
- [x] 2026-08-27: Completed Phase 2.5/2.6 source hardening: registration rejects a supplied password field, duplicate-insert races return validation errors, and production CORS excludes localhost origins while credentials are enabled; focused contract tests were added.
- [x] 2026-09-02: Completed Phase 2 provisioned-environment validation: migration 008, PostgreSQL-backed auth flows, SMTP delivery, CORS preflight, `/health`, logout and password-reset session revocation all passed.
- [ ] Implement Phase 3: shared access entitlement and expiry state.
- [ ] Implement Phases 4–8 and record validation evidence.

## Surprises & Discoveries

- Observation: `src/static-main.tsx` is the only entry used by `vite.static.config.ts`; it renders the landing and policy pages only. The generated TanStack `/account` routes are not part of `build:static`.
  Evidence: `src/static-main.tsx` calls `createRoot` directly and has no `RouterProvider`; `vite.static.config.ts` has no alternate entry.
- Observation: existing subscriptions, payments, channel access, expiry, and YooKassa webhook all use Telegram `User` records.
  Evidence: `bot/app/services/subscriptions.py`, `bot/app/tasks/expire_access.py`, and `bot/app/api/routes/yookassa.py` accept or look up `User`.
- Observation: SMTP sending exists through `bot/app/services/email.py`; whether production credentials and delivery work cannot be determined safely from the repository.
- Observation: This workspace has neither Docker nor a Python environment with FastAPI/SQLAlchemy installed.
  Evidence: `docker` is not recognized, and the bundled Python can run dependency-free security tests but skips the FastAPI contract tests.

## Decision Log

- Decision: Create website-account tables additively and keep existing Telegram `users`, `subscriptions`, `payments`, and `channel_access` untouched in the first migration.
  Rationale: current production payment and channel logic references Telegram users directly; an additive bridge prevents historic access loss.
  Date/Author: 2026-08-27 / Codex.
- Decision: Use `access_entitlements` as the source of truth for cabinet/PDF/Telegram permission after the sync phase.
  Rationale: one entitlement can express website access independently of the historical Telegram-only subscription schema.
  Date/Author: 2026-08-27 / Codex.
- Decision: Use the existing static build with one client-side SPA entry for landing and `/account/*`, then configure a narrowly scoped Nginx fallback for `/account/` only.
  Rationale: it preserves the public landing and avoids a second frontend deployment pipeline. The exact Nginx change remains gated on VPS inspection.
  Date/Author: 2026-08-27 / Codex.
- Decision: In MVP each calendar date has at most one published PDF file; opening and downloading are separate protected backend endpoints.
  Rationale: this matches the product requirement and avoids exposing storage URLs to expired clients.
  Date/Author: 2026-08-27 / Codex.
- Decision: Phase 2 creates `access_entitlements` and only the trial-activation operation required after email confirmation; full shared access, expiry, payment, and Telegram behavior belongs to Phase 3.
  Rationale: email confirmation must safely create a trial, but changing the authority of legacy subscription flows before Telegram linking is validated would create unnecessary production risk.
  Date/Author: 2026-08-27 / Codex.
- Decision: Canonical Russian phone normalization is digits-only `7XXXXXXXXXX`: remove spaces, punctuation, and an optional `+`; convert an 11-digit number beginning with `8` to the same number beginning with `7`; reject any other value. Apply this exact function at registration and login.
  Rationale: `+7`, `8`, and formatted Russian inputs must resolve to one unique account without ambiguous matching.
  Date/Author: 2026-08-27 / Codex.
- Decision: MVP does not add S3 or another external PDF storage provider. A server-side resolver maps `pdf_storage_key` to an approved local/private source.
  Rationale: protected delivery is required, but external storage introduces deployment and access-control scope that needs separate approval.
  Date/Author: 2026-08-27 / Codex.
- Decision: Reject unknown fields on the registration schema, specifically including `password`, and convert a database uniqueness race into the same client-visible validation class as ordinary duplicate detection.
  Rationale: silent acceptance of a password is misleading and unsafe for this temporary-password flow; application-level duplicate checks alone cannot prevent concurrent inserts.
  Date/Author: 2026-08-27 / Codex.
- Decision: Include configured development CORS origins only when `APP_ENV` is not production.
  Rationale: allowing localhost origins together with credentialed production requests would unnecessarily expose an authenticated browser session to a locally hosted origin.
  Date/Author: 2026-08-27 / Codex.
- Decision: MVP user-selected passwords for change and reset operations must be 8–256 characters with at least one letter and one digit. Do not increase the minimum without explicit product approval. The generated temporary password remains a separate 16-character random credential.
  Rationale: this is the accepted MVP product policy, while the longer generated temporary password retains additional initial-credential entropy.
  Date/Author: 2026-09-02 / Product decision recorded by Codex.

## Context and Orientation

The public site is a React/Vite static build. `src/static-main.tsx` is served from `dist-static/` and currently does not render the existing TanStack routes in `src/routes/`. The backend is FastAPI in `bot/app`, deployed by Docker Compose at `/opt/ascent-private-bot` and exposed only through Nginx. Its `users` table identifies people by a required Telegram ID; `subscriptions` tracks active/expired trial and paid periods; `channel_access` tracks issued Telegram invites.

The new website account is separate from a Telegram bot user. An entitlement is a database record that states whether that account currently has access. It must be consulted by every cabinet PDF endpoint and by Telegram synchronization. A payment is trusted only after the existing YooKassa webhook retrieves and validates it from YooKassa.

## Plan of Work

### Milestone 1 — production audit and deployment design

Read the VPS configuration before changing code. Run `nginx -T` with output restricted to the `ascentprivate.com` server block and record whether `/account/*` reaches the static `index.html`. Run `docker compose exec app alembic current` and `alembic heads` inside `/opt/ascent-private-bot`; compare the result to local revision `007_add_payment_provider_fields`. Confirm only the presence, not values, of SMTP variables in `/opt/ascent-private-bot/.env`.

If Nginx does not already handle the cabinet routes, Phase 6 will add a location rule equivalent to `location ^~ /account/ { try_files $uri $uri/ /index.html; }`. Do not apply this rule until the SPA renders protected cabinet pages. Keep the existing generic public-site behavior unchanged.

### Milestone 2 — website account and email authentication

Add an Alembic migration after revision 007 and SQLAlchemy models/repositories for `web_accounts`, `telegram_account_links`, `access_entitlements`, `idea_calendar_files`, and `idea_publications`. Phase 2 creates the entitlement plus the minimal `activate_trial_after_email_confirmation` operation; Phase 3 expands it into the shared AccessService. Add a compact server-side session record or Redis-backed opaque session identifier so logout can invalidate a session; the browser cookie contains only a random session identifier, is `HttpOnly`, `Secure` in production, `SameSite=Lax`, and is never stored in localStorage.

`web_accounts` stores normalized lowercase email, display phone, unique normalized phone, password hash, email-confirmation token hash and timestamps, activation status, `trial_used`, and `must_change_password`. Normalize a Russian phone by removing spaces, punctuation, and an optional `+`; convert 11 digits beginning with `8` to 11 digits beginning with `7`; require exactly 11 digits beginning with `7`; persist that `7XXXXXXXXXX` value and use the same function before every phone login lookup. Use Python `hashlib.scrypt` with a unique random salt and a versioned stored representation; never store a password or token in plaintext. Confirmation and Telegram-link tokens use `secrets.token_urlsafe`, hash before persistence, and have explicit expiry and one-time use.

Create `/api/auth/register`, `/api/auth/confirm-email`, `/api/auth/login`, `/api/auth/change-password`, `/api/auth/logout`, `/api/auth/me`, and `/api/auth/resend-confirmation`. Registration accepts only name, email, phone, required consents, and optional safe attribution. Login accepts `identifier` and password; normalize email or phone before lookup. Confirmation activates the account, generates a temporary password once, sends a second email containing only that password, creates the trial entitlement, and redirects to `/account/login?email_confirmed=1`. If that password is lost, the user must use password reset; neither confirmation nor resend may reveal or regenerate the earlier temporary password. A failed email send must leave a recoverable account state.

### Milestone 3 — shared access service

Add `bot/app/services/access.py` in Phase 3. Its access summary derives `can_view_materials` only when account status is active, entitlement status is `trial_active` or `paid_active`, and `current_period_end` is in the future. It owns expiry, paid activation/extension, revoke, restore, and Telegram synchronization; it takes over the minimal Phase 2 trial operation. Until Telegram linking and synchronization have been implemented and validated, legacy Telegram subscriptions remain authoritative for the existing Telegram-led trial/payment/channel flow. The service then maps a linked account to the effective access result without changing historical subscription records.

Expired and blocked accounts may authenticate when appropriate, but receive no material URL. The expiry job calls the access service for website entitlements and retains the existing Telegram expiry behavior until the linked-account path is proven. Audit records must capture auth/access/payment events without passwords, tokens, or secrets.

### Milestone 4 — cabinet API and protected calendar files

Add authenticated cabinet routes for dashboard, calendar month, selected date, protected PDF open/download, billing, cabinet payment creation, and Telegram link-token creation. The dashboard has access, payment, and Telegram status only; it has no latest-ideas list.

`GET /api/cabinet/calendar?month=&year=&search=` returns date, company count, and tickers. `GET /api/cabinet/calendar/{date}` returns selected-date metadata; for expired access it returns only locked metadata and paywall text. `GET /api/cabinet/files/{id}/open` streams or redirects through a protected backend response for active access. `GET /api/cabinet/files/{id}/download` sends the same file with an attachment response. Neither endpoint may return a raw storage URL to a client without active access. MVP validates one published file per calendar date with a unique database constraint.

Cabinet payment creation attaches `account_id` and `payment_source=cabinet` to a local payment. Extend the existing payment schema in a later additive migration so a payment can relate to either the legacy Telegram user or website account safely. The existing Telegram `payment_token` route and Robokassa fallback remain unchanged. Update webhook validation to restore the corresponding account entitlement only after the existing provider GET verification succeeds.

### Milestone 5 — Telegram linking and synchronization

The cabinet creates a one-time `link_<token>` deep link. The Telegram start handler validates it, links the Telegram ID to only one active website account, and checks the legacy `users.trial_used` record to prevent duplicate trials. If entitlement access is active, reuse `issue_channel_access`; otherwise report that Telegram access resumes after payment. Expiry and paid restoration call the same entitlement result before revoking or issuing an invite.

### Milestone 6 — static frontend cabinet

Replace the demonstration account experience with routes for register, login, change password, dashboard, calendar, billing, Telegram, and profile. Reuse the existing visual system but make the cabinet a quiet private-banking interface. The dashboard displays status, days remaining, Telegram state, billing CTA, and disclaimer—not latest idea cards.

The calendar has previous/next month controls, optional ticker/company search, clickable days with ideas, a selected-date PDF block, title-as-open action, and a separate download button. Expired views show metadata and paywall only. The frontend always calls protected APIs; it never treats a hidden element as access control. Add account events through the resilient `src/lib/tracking.ts` path so failures never block user actions.

All cabinet pages must visually match the existing AscentPrivate.com landing page: dark graphite background, muted gold accents, ivory/soft-white primary text, warm-grey secondary text, and the existing premium private-banking plus AI visual language. Do not introduce a generic dashboard, light SaaS admin-panel look, or visually foreign component system. Add `Регистрация` and `Вход` buttons to the public header only in this phase. They must reuse the current site button system's border radius, gold/dark styling, hover behavior, typography rhythm, and spacing. Registration and login forms must inherit the current payment form's card treatment, fields, spacing, dark background, gold accents, consent/link styling, and calm structured appearance.

### Milestone 7 — completion, deployment, and rollout

Update scheduler/payment integration, reports, env examples, AGENTS/HANDOFF documentation, and the VPS deployment notes. Apply the database migration, rebuild the backend, then deploy the static build and the explicitly reviewed Nginx `/account/` fallback. Keep the public main CTA directed to Telegram until the complete registration, payment, and Telegram-linking scenario passes in production.

## Interfaces and Dependencies

Auth endpoints accept/return JSON except confirmation, which redirects the browser. Authentication uses an `HttpOnly` cookie sent with `credentials: "include"`; FastAPI CORS remains restricted to the configured site origins with credentials allowed. New settings include confirmation-token TTL, Telegram-link-token TTL, cookie name and lifetime, and cabinet public URL. Add them to `bot/.env.example`; production values belong only in `/opt/ascent-private-bot/.env`.

No new external SaaS is required. Existing SMTP sends confirmation and temporary-password mail. PDF storage is deliberately abstracted as `pdf_storage_key` plus a server-side resolver. MVP must use an approved private/local source and must not add S3 or other external storage without explicit approval. Do not expose direct private PDF storage URLs.

## Concrete Steps

From the repository root, before implementation, run:

    npm.cmd exec tsc -- --noEmit
    npm.cmd run lint
    python -m compileall -q bot\app

On the VPS, only during the audit:

    cd /opt/ascent-private-bot
    docker compose exec app alembic current
    docker compose exec app alembic heads
    sudo nginx -T

Expected local migration head is `007_add_payment_provider_fields`. Record any VPS mismatch in this plan before applying a migration. Do not display `.env` values or secrets.

After implementation, run the TypeScript check, lint, static build, backend compile, Docker build, Alembic upgrade, `/health` check, and the manual scenarios below. The static deployment is `rsync -av --delete dist-static/ /var/www/ascent-private/dist-static/`; it does not copy `bot/.env`.

## Validation and Acceptance

Prove registration has no password field. Confirm a new email receives a confirmation link; before opening it, login and trial access fail. After confirming it, the second mail contains only a temporary password, login works by either email or normalized phone, and password change is required before materials.

Create a published calendar file and verify an active user can select its date, open its PDF by title, and download it. Expire the entitlement and verify the same user can sign in and see metadata/paywall but receives 403 or a locked response from both file endpoints. Verify an expired entitlement revokes linked Telegram access and a verified YooKassa payment restores both access paths exactly once. Repeat the webhook and confirm no extra paid period, invite, or report is created.

## Idempotence and Recovery

All migrations are additive and must have an Alembic downgrade where safe. Registration and resend must not create duplicate accounts for a normalized email/phone. Confirmation, webhook, Telegram linking, expiry, and invite issuance must be idempotent. If deployment fails, keep the legacy Telegram flow active, roll back only the static/Nginx release if necessary, and do not delete website accounts or historic payments. Restore a database backup before any destructive recovery; this plan does not authorize destructive actions.

## Artifacts and Notes

The exact production Nginx source is not in the repository. Before Phase 6, collect the active server block and insert the reviewed `/account/` fallback snippet into the deployment notes. The repository has no automated test suite discovered during Phase 1; add focused backend and frontend tests as each feature phase introduces behavior.

## Outcomes & Retrospective

Phase 1 produced this implementation plan. Phase 2 added website-only account/auth source code without changing legacy Telegram subscriptions, payments, channel access, scheduler, YooKassa webhook, frontend routing, or Nginx. Phase 2.5/2.6 hardened registration input handling, duplicate handling, CORS and secret validation responses. VPS validation passed: migration, health, SMTP and the auth/session flow are verified. Remaining work is Phases 3–8.

Revision note (2026-08-27): Created from `docs/ascent_private_cabinet_tz_codex.md` after repository inspection. The plan uses calendar PDF files, login by email or normalized phone, and a temporary-password-only second email.

Revision note (2026-08-27): Recorded Phase 2 implementation and its environment-dependent validation gaps.

Revision note (2026-08-27): Added Phase 6 UX requirement to visually match the existing landing, including public-header registration/login buttons and payment-form-aligned auth forms.

Revision note (2026-08-27): Recorded Phase 2.5/2.6 source hardening and the unavailable local Docker/FastAPI runtime; VPS validation remains required.

Revision note (2026-09-02): Recorded completed Phase 2 VPS validation and the accepted MVP 8-character minimum password policy.
