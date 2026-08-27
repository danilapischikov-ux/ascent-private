import importlib.util
import unittest
from types import SimpleNamespace


BACKEND_DEPS_AVAILABLE = all(
    importlib.util.find_spec(package) is not None
    for package in ("fastapi", "pydantic", "sqlalchemy", "pydantic_settings")
)


@unittest.skipUnless(BACKEND_DEPS_AVAILABLE, "FastAPI backend dependencies are not installed in this Python runtime")
class BackendContractTestCase(unittest.TestCase):
    @staticmethod
    def imports():
        from fastapi import Response
        from pydantic import ValidationError

        from app.api.routes.auth import _set_session_cookie
        from app.api.schemas.auth import RegisterRequest
        from app.core.config import Settings
        from app.core.security import hash_secret
        from app.services.account_auth import build_auth_summary

        return Response, ValidationError, _set_session_cookie, RegisterRequest, Settings, hash_secret, build_auth_summary


class RegistrationContractTests(BackendContractTestCase):
    def test_registration_rejects_a_password_field(self) -> None:
        _Response, ValidationError, _set_session_cookie, RegisterRequest, _Settings, _hash_secret, _build_auth_summary = self.imports()
        with self.assertRaises(ValidationError):
            RegisterRequest.model_validate(
                {
                    "name": "Иван",
                    "email": "ivan@example.com",
                    "phone": "+7 999 123-45-67",
                    "consent_personal_data": True,
                    "consent_offer": True,
                    "consent_risk_disclaimer": True,
                    "password": "MustNotBeAccepted123",
                }
            )


class AuthResponseContractTests(BackendContractTestCase):
    def test_summary_contains_only_safe_website_account_data(self) -> None:
        _Response, _ValidationError, _set_session_cookie, _RegisterRequest, _Settings, _hash_secret, build_auth_summary = self.imports()
        account = SimpleNamespace(
            id=17,
            name="Иван",
            email="ivan@example.com",
            phone="+7 999 123-45-67",
            password_hash="must-not-leak",
            email_verification_token_hash="must-not-leak",
            password_reset_token_hash="must-not-leak",
            must_change_password=True,
        )
        entitlement = SimpleNamespace(access_status="trial_active", current_period_end=None)

        summary = build_auth_summary(account, entitlement)
        rendered = repr(summary)

        self.assertEqual(summary["account"], {"id": "17", "name": "Иван", "email": "ivan@example.com", "phone": "+7 999 123-45-67"})
        self.assertEqual(summary["access"]["status"], "trial_active")
        self.assertNotIn("password_hash", rendered)
        self.assertNotIn("verification_token", rendered)
        self.assertNotIn("reset_token", rendered)

    def test_session_cookie_is_opaque_httponly_and_secure_in_production(self) -> None:
        Response, _ValidationError, _set_session_cookie, _RegisterRequest, Settings, _hash_secret, _build_auth_summary = self.imports()
        response = Response()
        settings = Settings(APP_ENV="production")
        token = "opaque-session-token"

        _set_session_cookie(response, settings, token)
        cookie = response.headers["set-cookie"]

        self.assertIn(f"{settings.auth_session_cookie_name}={token}", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Secure", cookie)
        self.assertIn("SameSite=lax", cookie)

    def test_session_hash_is_not_the_cookie_value(self) -> None:
        _Response, _ValidationError, _set_session_cookie, _RegisterRequest, _Settings, hash_secret, _build_auth_summary = self.imports()
        token = "opaque-session-token"
        self.assertNotEqual(token, hash_secret(token))


class CorsContractTests(BackendContractTestCase):
    def test_production_only_allows_public_site_origins(self) -> None:
        _Response, _ValidationError, _set_session_cookie, _RegisterRequest, Settings, _hash_secret, _build_auth_summary = self.imports()
        settings = Settings(
            APP_ENV="production",
            SITE_URL="https://ascentprivate.com",
            AUTH_DEV_CORS_ORIGINS="http://localhost:5176,http://127.0.0.1:5176",
        )

        self.assertEqual(settings.cors_origins, ["https://ascentprivate.com", "https://www.ascentprivate.com"])

    def test_development_includes_explicit_dev_origins(self) -> None:
        _Response, _ValidationError, _set_session_cookie, _RegisterRequest, Settings, _hash_secret, _build_auth_summary = self.imports()
        settings = Settings(
            APP_ENV="development",
            SITE_URL="https://ascentprivate.com",
            AUTH_DEV_CORS_ORIGINS="http://localhost:5176,http://127.0.0.1:5176",
        )

        self.assertEqual(
            settings.cors_origins,
            [
                "https://ascentprivate.com",
                "https://www.ascentprivate.com",
                "http://localhost:5176",
                "http://127.0.0.1:5176",
            ],
        )
