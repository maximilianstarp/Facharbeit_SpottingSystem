# import libraries
import base64
import bcrypt
import hashlib
import secrets
import string

import base64
import bcrypt
import hashlib
import secrets
import string

class Hasher:
    """
    A class for generating and verifying hashed credentials and generating API tokens.
    The functions using bcrypt for hashing and verifying credentials are adapted from the tutorial: 
    https://www.youtube.com/watch?v=VVKFuZf9jNw&t=805s
    """

    def __init__(self) -> None:
        pass

    def generate_hash(self, to_hash: str) -> str:
        """
        Generates a hashed string using SHA-256 and bcrypt.
        
        Args:
            to_hash (str): The string to be hashed.
        
        Returns:
            str: The hashed string.
        """
        to_hash = to_hash.encode("utf-8")
        to_hash = base64.b64encode(hashlib.sha256(to_hash).digest())

        hashed = bcrypt.hashpw(
            to_hash,
            bcrypt.gensalt(12)
        )

        return hashed.decode()

    def check_hashed_credentials(self, username_try: str, password_try: str, username: str, password: str) -> bool:
        """
        Checks if the provided username and password match the stored hashed credentials.
        
        Args:
            username_try (str): The username to verify.
            password_try (str): The password to verify.
            username (str): The stored username.
            password (str): The stored password.
        
        Returns:
            bool: True if the credentials match, False otherwise.
        """
        username = username.encode("utf-8")
        password = password.encode("utf-8")
        username_try = str(username_try).encode("utf-8")
        password_try = str(password_try).encode("utf-8")

        username_try = base64.b64encode(hashlib.sha256(username_try).digest())
        password_try = base64.b64encode(hashlib.sha256(password_try).digest())
        
        if bcrypt.checkpw(username_try, username) and bcrypt.checkpw(password_try, password):
            return True
        else:
            return False

    def generate_api_token(self, length: int = 60) -> str:
        """
        Generates a random API token.
        
        Args:
            length (int): Length of the token. Default is 60.
        
        Returns:
            str: The generated API token.
        """
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for i in range(length))
        return token
