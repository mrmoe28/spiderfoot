# -*- coding: utf-8 -*-
import hashlib
import secrets

import requests
from authlib.integrations.requests_client import OAuth2Session

GOOGLE_AUTHORIZE_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USERINFO_URL = 'https://openidconnect.googleapis.com/v1/userinfo'


def google_login_url(client_id: str, redirect_uri: str, state: str) -> str:
    """Build Google OAuth authorization URL."""
    client = OAuth2Session(client_id, redirect_uri=redirect_uri, scope='openid email profile')
    url, _ = client.create_authorization_url(GOOGLE_AUTHORIZE_URL, state=state)
    return url


def google_fetch_user(client_id: str, client_secret: str, redirect_uri: str, code: str) -> dict:
    """Exchange authorization code for Google user info (sub, email, name, picture)."""
    client = OAuth2Session(client_id, redirect_uri=redirect_uri)
    token = client.fetch_token(
        GOOGLE_TOKEN_URL,
        code=code,
        client_secret=client_secret,
    )
    resp = requests.get(
        GOOGLE_USERINFO_URL,
        headers={'Authorization': f'Bearer {token["access_token"]}'},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
    return f'{salt}${dk.hex()}'


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, dk_hex = stored.split('$', 1)
        dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 200_000)
        return secrets.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False
