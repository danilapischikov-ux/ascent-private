import unittest

from app.core.security import (
    create_temporary_password,
    hash_password,
    normalize_phone,
    validate_password,
    verify_password,
)


class PhoneNormalizationTests(unittest.TestCase):
    def test_russian_phone_variants_share_one_canonical_value(self) -> None:
        expected = "79991234567"
        for value in ("+7 999 123-45-67", "8 (999) 123 45 67", "79991234567"):
            self.assertEqual(normalize_phone(value), expected)

    def test_invalid_phone_is_rejected(self) -> None:
        self.assertIsNone(normalize_phone("+1 202 555 0100"))
        self.assertIsNone(normalize_phone("7999123456"))


class PasswordSecurityTests(unittest.TestCase):
    def test_scrypt_hash_verifies_only_the_same_password(self) -> None:
        password = "CorrectPassword123"
        encoded = hash_password(password)
        self.assertNotIn(password, encoded)
        self.assertTrue(verify_password(password, encoded))
        self.assertFalse(verify_password("IncorrectPassword123", encoded))

    def test_generated_temporary_password_meets_policy(self) -> None:
        password = create_temporary_password()
        self.assertTrue(validate_password(password))
        self.assertGreaterEqual(len(password), 12)

    def test_password_policy_rejects_excessive_length(self) -> None:
        self.assertFalse(validate_password("A1" + ("a" * 255)))


if __name__ == "__main__":
    unittest.main()
