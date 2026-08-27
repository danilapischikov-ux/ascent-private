# Ascent Private Telegram Bot

Production backend for the Ascent Private Telegram bot, Robokassa payments, channel access automation, and admin reporting.

## What Is Implemented

- One Telegram bot for trial and payment flows.
- `/start trial_site`: creates or updates a Telegram user, activates one 30-day trial, creates a one-use channel invite.
- `/start pay_site` and `/pay`: creates a `payment_token` and sends the bot button `Оплатить`.
- `POST /api/payments/robokassa/create`: accepts `payment_token`, name, email, phone and returns Robokassa payload plus payment URL.
- `GET|POST /robokassa/result`: verifies Robokassa signature with Password2, validates amount, token and Telegram ID, then activates paid access idempotently.
- Paid access starts immediately if the user only has trial access. If the user already has an active paid subscription, the next paid period starts when the current paid period ends.
- Channel access service unbans previously banned users and issues a one-use invite link.
- Admin email and support-chat reports after successful payment.
- APScheduler jobs for access expiration and reminders.
- PostgreSQL models, Alembic migrations, Docker Compose, Nginx config.

## Local Layout

This folder is intended to be copied to `/opt/ascent-private-bot` on the VPS.

```bash
cd /opt/ascent-private-bot
cp .env.example .env
nano .env
chmod 600 .env
```

## Required `.env` Values

Fill these before launch:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_USERNAME`
- `BOT_ADMIN_IDS`
- `ROBOKASSA_MERCHANT_LOGIN`
- `ROBOKASSA_PASSWORD1`
- `ROBOKASSA_PASSWORD2`
- `ROBOKASSA_TEST_PASSWORD1`
- `ROBOKASSA_TEST_PASSWORD2`
- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `SMTP_PASSWORD`
- `TELEGRAM_WEBHOOK_SECRET`
- `SECRET_KEY`

Generate secrets:

```bash
openssl rand -hex 32
openssl rand -hex 32
```

## VPS Install

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin nginx certbot python3-certbot-nginx
sudo systemctl enable docker
sudo systemctl start docker
sudo mkdir -p /opt/ascent-private-bot
sudo chown -R $USER:$USER /opt/ascent-private-bot
```

Copy this `bot/` directory contents into `/opt/ascent-private-bot`.

## Run

```bash
cd /opt/ascent-private-bot
docker compose up -d --build
docker compose exec app alembic upgrade head
docker compose logs -f app
```

## Health Check

```bash
curl https://bot.ascentprivate.com/health
```

Expected:

```json
{"status":"ok"}
```

## Nginx

```bash
sudo cp nginx/bot.ascentprivate.com.conf /etc/nginx/sites-available/bot.ascentprivate.com
sudo ln -s /etc/nginx/sites-available/bot.ascentprivate.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d bot.ascentprivate.com
```

DNS:

```text
Type: A
Name: bot
Value: <VPS IP>
TTL: Auto / 300
```

## Telegram Webhook

The app sets webhook automatically on startup when `TELEGRAM_WEBHOOK_URL` is set. Manual command:

```bash
curl -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
  -d "url=https://bot.ascentprivate.com/telegram/webhook" \
  -d "secret_token=${TELEGRAM_WEBHOOK_SECRET}"
```

Check:

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

## Robokassa Settings

Set in Robokassa account:

```text
Result URL: https://bot.ascentprivate.com/robokassa/result
Success URL: https://bot.ascentprivate.com/robokassa/success
Fail URL: https://bot.ascentprivate.com/robokassa/fail
Method: POST
Signature algorithm: MD5
```

`/robokassa/success` and `/robokassa/fail` accept both GET and POST, then redirect the user to
`PAYMENT_SUCCESS_URL` or `PAYMENT_FAIL_URL` on the main site.

Start with:

```env
ROBOKASSA_IS_TEST=1
```

After successful tests:

```env
ROBOKASSA_IS_TEST=0
```

## Site Integration

The site footer must call:

```http
POST https://bot.ascentprivate.com/api/payments/robokassa/create
```

Payload:

```json
{
  "payment_token": "...",
  "customer_name": "Client Name",
  "customer_email": "client@example.com",
  "customer_phone": "+79990000000"
}
```

If there is no `payment_token` in the page URL, the site button `Платежная ссылка` sends the user to:

```text
https://t.me/AscentPrivate_bot?start=pay_site
```

## Trial Test Checklist

1. On the site click `Получить доступ`.
2. Telegram opens `/start trial_site`.
3. Bot stores Telegram ID.
4. Bot activates one 30-day trial.
5. Bot creates an individual invite link.
6. User joins the private channel.
7. `users.trial_used = true`.
8. Support chat receives a notification.
9. Repeating trial does not issue a second free period and offers payment.

## Payment Test Checklist

1. On the site click `Платежная ссылка` without `payment_token`.
2. Telegram opens `/start pay_site`.
3. Bot creates `payment_token`.
4. Bot sends a site URL `https://ascentprivate.com/?payment_token=...#payment` with button `Оплатить`.
5. User fills name, email, phone in the footer.
6. Site calls `/api/payments/robokassa/create`.
7. Robokassa opens.
8. Robokassa sends `ResultURL`.
9. Backend verifies signature, amount, token, Telegram ID.
10. Backend returns `OK{InvId}`.
11. Paid subscription activates for 30 days.
12. Bot sends a one-use invite link.
13. Admin email goes to `admin@ascentprivate.com`.
14. Support Telegram chat receives a notification.
15. Repeated `ResultURL` returns `OK{InvId}` and does not extend access or resend reports.

## Useful Logs

```bash
docker compose logs -f app
docker compose logs -f postgres
docker compose logs -f redis
```
