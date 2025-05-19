import string

from currency_exchange.utils.importobject import import_object
from currency_exchange.config import auth_settings


def min_length_validator(password: str) -> None:
	if len(password) < auth_settings.MIN_PASSWORD_LENGTH:
		raise ValueError(
			f"Required minimum password length is {auth_settings.MIN_PASSWORD_LENGTH}."
		)


def no_whitespace_chars_validator(password: str) -> None:
	if set(string.whitespace).intersection(password):
		raise ValueError("Whitespace characters are not allowed in password.")


def get_all_password_validators():
	return [
		import_object(validator_string)
		for validator_string in auth_settings.PASSWORD_VALIDATORS
	]
