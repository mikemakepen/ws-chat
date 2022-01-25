import click
import getpass
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class FernetTool:
    def __init__(self, password, salt=None) -> None:
        self.password = password
        self.salt = salt
        self.test_salt= ';\x9c\xc6E\x7f\x83j\n\xf6\xd7t\xa2\xa2\xa9\x9d\x87'
        self.init_fernet()

    def init_fernet(self):
        if self.salt is None:
            self.salt = self.test_salt
            print("WARNING: using test salt")
        
        salt = self.salt.encode()
        password = self.password.encode()
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=390000)
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.f = Fernet(key)
        
    def encrypt(self, data: str) -> bytes:
        return self.f.encrypt(data.encode())

    def decrypt(self, data: str) -> bytes:
        return self.f.decrypt(data.encode())

def read_pass() -> str:
    return getpass.getpass()

@click.group()
def main():
    pass

@main.command('en')
@click.argument('data')
@click.option('--salt', default=None, help='salt str')
def encrypt(data: str, salt: str):
    ''' encrpyt data '''
    password = read_pass()
    f = FernetTool(password, salt)
    try:
        encrypted = f.encrypt(data)
        print(f'encrypted: {encrypted.decode()}')
    except:
        print('encrypt fail')

@main.command('de')
@click.argument('data')
@click.option('--salt', default=None, help='salt str')
def decrypt(data: str, salt: str):
    ''' decrypt data'''
    password = read_pass()
    f = FernetTool(password, salt)
    try:
        decrypted = f.decrypt(data)
        print(f'decrypted: {decrypted.decode()}')
    except:
        print('decrypt fail')

if __name__ == '__main__':
    main()
