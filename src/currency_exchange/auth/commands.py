import asyncio
import datetime
from getpass import getpass
import argparse

from sqlalchemy import delete
from joserfc.jwk import RSAKey

from currency_exchange.db.session import async_session_factory
from .dbmodels import User, UserCategory, TokenState


async def _save_user_to_db(user: User):
	try:
		async with async_session_factory() as session:
			session.add(user)
			await session.commit()
	except Exception as e:
		print(e)


def create_admin():
	username = input("Enter admin username: ")
	while True:
		password1 = getpass("Enter admin password: ")
		password2 = getpass("Repeat password again: ")

		if password1 == password2:
			break
		else:
			print("Passwords don't match")

	asyncio.run(
		_save_user_to_db(
			User(username=username, password=password1, category=UserCategory.ADMIN)
		)
	)

	print("Admin account created")


def remove_expired_tokens():
	asyncio.run(_remove_expired_tokens())


async def _remove_expired_tokens():
	async with async_session_factory() as session:
		async with session.begin():
			res = await session.execute(
				delete(TokenState)
				.where(TokenState.expiry_date < datetime.datetime.now())
				.returning(TokenState.id)
			)
		print(f"Removed {len(res.fetchall())} expired tokens")


def generate_crypto_keys():
	parser = argparse.ArgumentParser(prog='generatecryptokeys', usage='%(prog)s [options]')
	parser.add_argument('--pub', type=str, help='Public key path', required=True)
	parser.add_argument('--priv', type=str, help='Private key path', required=True)
	args = parser.parse_args()

	key = RSAKey.generate_key()
	with (open(args.priv, "wb") as priv_key_file,
		  open(args.pub, "wb") as pub_key_file):
		priv_key_file.write(key.as_pem())
		pub_key_file.write(key.as_pem(private=False))

