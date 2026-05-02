import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file (for local development)
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

    # TiDB Database
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 4000))
    MYSQL_USER = os.environ.get('MYSQL_USER', '')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'openblog')
    MYSQL_SSL_CA = os.environ.get('MYSQL_SSL_CA', str(BASE_DIR / 'isrgrootx1.pem'))

    SQLALCHEMY_DATABASE_URI = (
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
        '?charset=utf8mb4'
    )
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'ssl': {'ca': MYSQL_SSL_CA}},
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # GitHub OAuth
    GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID', '')
    GITHUB_CLIENT_SECRET = os.environ.get('GITHUB_CLIENT_SECRET', '')
    SITE_URL = os.environ.get('SITE_URL', '')  # e.g. https://sam3maker-openblog.hf.space

    # File Upload — SVG removed to prevent stored XSS
    # HF Spaces: use /data/uploads for persistent storage
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', str(BASE_DIR / 'static' / 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Pagination
    ARTICLES_PER_PAGE = 10
    COMMENTS_PER_PAGE = 20
    USERS_PER_PAGE = 20

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Please log in first'
