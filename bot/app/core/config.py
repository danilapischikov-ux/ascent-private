from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_bot_username: str = Field(default="AscentPrivate_bot", alias="TELEGRAM_BOT_USERNAME")
    telegram_channel_id: int = Field(default=-1003869201155, alias="TELEGRAM_CHANNEL_ID")
    telegram_support_chat_id: int = Field(default=-1004441348826, alias="TELEGRAM_SUPPORT_CHAT_ID")
    bot_admin_ids: list[int] = Field(default_factory=list, alias="BOT_ADMIN_IDS")

    subscription_rub_price: int = Field(default=8000, alias="SUBSCRIPTION_RUB_PRICE")
    subscription_days: int = Field(default=30, alias="SUBSCRIPTION_DAYS")
    trial_days: int = Field(default=30, alias="TRIAL_DAYS")
    allow_repeat_trial_for_testing: bool = Field(default=False, alias="ALLOW_REPEAT_TRIAL_FOR_TESTING")
    currency_code: str = Field(default="RUB", alias="CURRENCY_CODE")

    site_url: str = Field(default="https://ascentprivate.com", alias="SITE_URL")
    payment_form_anchor: str = Field(default="#payment", alias="PAYMENT_FORM_ANCHOR")
    payment_page_url: str = Field(default="https://ascentprivate.com/#payment", alias="PAYMENT_PAGE_URL")
    payment_success_url: str = Field(
        default="https://ascentprivate.com/?payment=success#payment",
        alias="PAYMENT_SUCCESS_URL",
    )
    payment_fail_url: str = Field(
        default="https://ascentprivate.com/?payment=fail#payment",
        alias="PAYMENT_FAIL_URL",
    )
    bot_trial_start_param: str = Field(default="trial_site", alias="BOT_TRIAL_START_PARAM")
    bot_payment_start_param: str = Field(default="pay_site", alias="BOT_PAYMENT_START_PARAM")
    bot_faq_start_param: str = Field(default="faq_site", alias="BOT_FAQ_START_PARAM")

    robokassa_merchant_login: str = Field(default="", alias="ROBOKASSA_MERCHANT_LOGIN")
    robokassa_password1: str = Field(default="", alias="ROBOKASSA_PASSWORD1")
    robokassa_password2: str = Field(default="", alias="ROBOKASSA_PASSWORD2")
    robokassa_test_password1: str = Field(default="", alias="ROBOKASSA_TEST_PASSWORD1")
    robokassa_test_password2: str = Field(default="", alias="ROBOKASSA_TEST_PASSWORD2")
    robokassa_is_test: bool = Field(default=True, alias="ROBOKASSA_IS_TEST")
    robokassa_hash_algorithm: Literal["MD5", "SHA256"] = Field(default="MD5", alias="ROBOKASSA_HASH_ALGORITHM")
    robokassa_payment_url: AnyHttpUrl = Field(
        default="https://auth.robokassa.ru/Merchant/Index.aspx",
        alias="ROBOKASSA_PAYMENT_URL",
    )
    robokassa_result_url: str = Field(
        default="https://bot.ascentprivate.com/robokassa/result",
        alias="ROBOKASSA_RESULT_URL",
    )
    robokassa_success_url: str = Field(
        default="https://bot.ascentprivate.com/robokassa/success",
        alias="ROBOKASSA_SUCCESS_URL",
    )
    robokassa_fail_url: str = Field(
        default="https://bot.ascentprivate.com/robokassa/fail",
        alias="ROBOKASSA_FAIL_URL",
    )
    robokassa_payment_description: str = Field(
        default="Подписка Ascent Private на 30 дней",
        alias="ROBOKASSA_PAYMENT_DESCRIPTION",
    )

    payment_provider: Literal["ROBOKASSA", "YOOKASSA"] = Field(
        default="ROBOKASSA",
        alias="PAYMENT_PROVIDER",
    )
    yookassa_shop_id: str = Field(default="", alias="YOOKASSA_SHOP_ID")
    yookassa_secret_key: str = Field(default="", alias="YOOKASSA_SECRET_KEY")
    yookassa_api_url: AnyHttpUrl = Field(
        default="https://api.yookassa.ru/v3",
        alias="YOOKASSA_API_URL",
    )
    yookassa_return_url: str = Field(
        default="https://ascentprivate.com/?payment=success#payment",
        alias="YOOKASSA_RETURN_URL",
    )
    yookassa_payment_description: str = Field(
        default="Подписка Ascent Private на 30 дней",
        alias="YOOKASSA_PAYMENT_DESCRIPTION",
    )
    yookassa_capture: bool = Field(default=True, alias="YOOKASSA_CAPTURE")
    yookassa_receipt_enabled: bool = Field(default=True, alias="YOOKASSA_RECEIPT_ENABLED")
    yookassa_vat_code: int = Field(default=1, alias="YOOKASSA_VAT_CODE")
    yookassa_payment_mode: str = Field(default="full_payment", alias="YOOKASSA_PAYMENT_MODE")
    yookassa_payment_subject: str = Field(default="service", alias="YOOKASSA_PAYMENT_SUBJECT")
    yookassa_webhook_url: str = Field(
        default="https://bot.ascentprivate.com/yookassa/webhook",
        alias="YOOKASSA_WEBHOOK_URL",
    )

    database_url: str = Field(
        default="postgresql+asyncpg://ascent_bot_user:CHANGE_ME@postgres:5432/ascent_private_bot",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="ascentprivate@gmail.com", alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="ascentprivate@gmail.com", alias="SMTP_FROM_EMAIL")
    smtp_from_name: str = Field(default="Ascent Private", alias="SMTP_FROM_NAME")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")
    auth_confirmation_token_ttl_hours: int = Field(default=24, alias="AUTH_CONFIRMATION_TOKEN_TTL_HOURS")
    auth_reset_token_ttl_hours: int = Field(default=24, alias="AUTH_RESET_TOKEN_TTL_HOURS")
    auth_session_ttl_days: int = Field(default=14, alias="AUTH_SESSION_TTL_DAYS")
    auth_session_cookie_name: str = Field(default="ascent_cabinet_session", alias="AUTH_SESSION_COOKIE_NAME")
    auth_public_api_url: str = Field(default="https://bot.ascentprivate.com", alias="AUTH_PUBLIC_API_URL")
    auth_dev_cors_origins: str = Field(
        default="http://127.0.0.1:5173,http://localhost:5173,http://127.0.0.1:5176,http://localhost:5176",
        alias="AUTH_DEV_CORS_ORIGINS",
    )
    payment_report_email_enabled: bool = Field(default=True, alias="PAYMENT_REPORT_EMAIL_ENABLED")
    payment_report_email_to: str = Field(default="admin@ascentprivate.com", alias="PAYMENT_REPORT_EMAIL_TO")
    payment_report_email_subject: str = Field(
        default="Новая оплата Ascent Private",
        alias="PAYMENT_REPORT_EMAIL_SUBJECT",
    )
    payment_report_sheets_endpoint: str = Field(default="", alias="PAYMENT_REPORT_SHEETS_ENDPOINT")
    trial_report_sheets_endpoint: str = Field(default="", alias="TRIAL_REPORT_SHEETS_ENDPOINT")

    yandex_metrika_counter_id: str = Field(default="", alias="YANDEX_METRIKA_COUNTER_ID")
    yandex_metrika_oauth_token: str = Field(default="", alias="YANDEX_METRIKA_OAUTH_TOKEN")
    yandex_metrika_offline_conversion_target: str = Field(
        default="payment_confirmed",
        alias="YANDEX_METRIKA_OFFLINE_CONVERSION_TARGET",
    )
    yandex_metrika_offline_conversion_id_type: Literal["CLIENT_ID", "YCLID"] = Field(
        default="CLIENT_ID",
        alias="YANDEX_METRIKA_OFFLINE_CONVERSION_ID_TYPE",
    )
    yandex_metrika_api_base_url: str = Field(
        default="https://api-metrika.yandex.net",
        alias="YANDEX_METRIKA_API_BASE_URL",
    )
    yandex_direct_oauth_token: str = Field(default="", alias="YANDEX_DIRECT_OAUTH_TOKEN")
    yandex_direct_client_login: str = Field(default="", alias="YANDEX_DIRECT_CLIENT_LOGIN")
    yandex_direct_api_base_url: str = Field(
        default="https://api.direct.yandex.com",
        alias="YANDEX_DIRECT_API_BASE_URL",
    )
    yandex_direct_reports_api_url: str = Field(
        default="https://api.direct.yandex.com/json/v501/reports",
        alias="YANDEX_DIRECT_REPORTS_API_URL",
    )
    yandex_direct_sandbox: bool = Field(default=False, alias="YANDEX_DIRECT_SANDBOX")
    yandex_direct_use_operator_units: bool = Field(default=False, alias="YANDEX_DIRECT_USE_OPERATOR_UNITS")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_decision_model: str = Field(default="gpt-5-codex", alias="OPENAI_DECISION_MODEL")
    openai_decision_timeout_seconds: int = Field(default=60, alias="OPENAI_DECISION_TIMEOUT_SECONDS")
    openai_decision_dry_run: bool = Field(default=True, alias="OPENAI_DECISION_DRY_RUN")

    marketing_automation_mode: Literal["read_only", "dry_run", "limited_write"] = Field(
        default="read_only",
        alias="MARKETING_AUTOMATION_MODE",
    )
    codex_executor_write_enabled: bool = Field(default=False, alias="CODEX_EXECUTOR_WRITE_ENABLED")
    marketing_approved_daily_budget: int = Field(default=0, alias="MARKETING_APPROVED_DAILY_BUDGET")
    marketing_bid_change_cycle_max_percent: int = Field(
        default=15,
        alias="MARKETING_BID_CHANGE_CYCLE_MAX_PERCENT",
    )
    marketing_budget_change_day_max_percent: int = Field(
        default=20,
        alias="MARKETING_BUDGET_CHANGE_DAY_MAX_PERCENT",
    )
    marketing_min_keyword_clicks: int = Field(default=50, alias="MARKETING_MIN_KEYWORD_CLICKS")
    marketing_min_ad_group_clicks: int = Field(default=100, alias="MARKETING_MIN_AD_GROUP_CLICKS")
    marketing_decision_confidence_min: float = Field(default=0.7, alias="MARKETING_DECISION_CONFIDENCE_MIN")
    marketing_max_actions_per_day: int = Field(default=1, alias="MARKETING_MAX_ACTIONS_PER_DAY")

    app_env: str = Field(default="production", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    domain: str = Field(default="bot.ascentprivate.com", alias="DOMAIN")
    telegram_webhook_url: str = Field(default="", alias="TELEGRAM_WEBHOOK_URL")
    telegram_webhook_secret: str = Field(default="", alias="TELEGRAM_WEBHOOK_SECRET")
    secret_key: str = Field(default="", alias="SECRET_KEY")
    payment_token_ttl_minutes: int = Field(default=60, alias="PAYMENT_TOKEN_TTL_MINUTES")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    @field_validator("bot_admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, value: str | int | list[int]) -> list[int]:
        if isinstance(value, int):
            return [value]
        if isinstance(value, list):
            return value
        if not value:
            return []
        return [int(item.strip()) for item in value.split(",") if item.strip()]

    @property
    def robokassa_password_for_payment(self) -> str:
        return self.robokassa_test_password1 if self.robokassa_is_test else self.robokassa_password1

    @property
    def robokassa_password_for_result(self) -> str:
        return self.robokassa_test_password2 if self.robokassa_is_test else self.robokassa_password2

    @property
    def cors_origins(self) -> list[str]:
        production = [self.site_url, self.site_url.replace("https://", "https://www.")]
        if self.app_env.lower() == "production":
            return production
        development = [origin.strip() for origin in self.auth_dev_cors_origins.split(",") if origin.strip()]
        return list(dict.fromkeys([*production, *development]))


@lru_cache
def get_settings() -> Settings:
    return Settings()
