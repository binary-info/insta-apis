import os

from dotenv import load_dotenv
from fastapi.security import APIKeyHeader

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))

# DOMAIN = "https://127.0.0.1:8000/"
DOMAIN = "https://instaapis-125d3323b5e6.herokuapp.com/"


INSTAGRAM_CLIENT_ID = os.getenv("INSTAGRAM_APP_ID")
INSTAGRAM_CLIENT_SECRET = os.getenv("INSTAGRAM_SECRET_ID")
INSTAGRAM_REDIRECT_URI = f'{DOMAIN}api/v1/instagram/callback/'
# INSTAGRAM_REDIRECT_URI = f'{DOMAIN}auth/instagram/callback/'
INSTAGRAM_ACCESS_TOKEN_HEADER = APIKeyHeader(name="Access-Token", scheme_name="instagram access token")
