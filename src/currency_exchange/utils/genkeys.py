import argparse

from joserfc.jwk import RSAKey


parser = argparse.ArgumentParser(prog='generatecryptokeys', usage='%(prog)s [options]')
parser.add_argument('--pub', type=str, help='Public key path', required=True)
parser.add_argument('--priv', type=str, help='Private key path', required=True)


def generate_crypto_keys(priv_path: str, pub_path: str):
	key = RSAKey.generate_key()
	with (open(priv_path, "wb") as priv_key_file,
		  open(pub_path, "wb") as pub_key_file):
		priv_key_file.write(key.as_pem())
		pub_key_file.write(key.as_pem(private=False))


if __name__ == '__main__':
	args = parser.parse_args()
	generate_crypto_keys(args.pub, args.priv)