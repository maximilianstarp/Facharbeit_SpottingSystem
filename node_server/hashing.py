# import libraries
import base64
import bcrypt
import hashlib
import secrets
import string

class Hasher():
    def __init__(self) -> None:
        pass

    def genenrate_hash(self, to_hash:str) -> str:
        to_hash = to_hash.encode("utf-8")
        to_hash = base64.b64encode(hashlib.sha256(to_hash).digest())

        hashed = bcrypt.hashpw(
            to_hash,
            bcrypt.gensalt(12)
        )

        return hashed.decode()
    
    def check_hashed_credentials(self, username_try:str, password_try:str, username:str, password:str) -> bool:
        username = username.encode("utf-8")
        password = password.encode("utf-8")
        username_try = str(username_try).encode("utf-8")
        password_try = str(password_try).encode("utf-8")

        username_try = base64.b64encode(hashlib.sha256(username_try).digest())
        password_try = base64.b64encode(hashlib.sha256(password_try).digest())
        
        if(bcrypt.checkpw(username_try, username) and bcrypt.checkpw(password_try, password)): return True
        else: return False
    
    def generate_api_token(self, length: int = 60) -> str:
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(length))
        return token