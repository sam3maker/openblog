#!/usr/bin/env python3
"""博客平台启动入口"""
import os
from pathlib import Path
import pymysql
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.config import Config, BASE_DIR


def ensure_ssl_cert():
    """If MYSQL_SSL_CA_CONTENT env var is set, write it to isrgrootx1.pem"""
    cert_content = os.environ.get('MYSQL_SSL_CA_CONTENT', '')
    if cert_content:
        cert_path = BASE_DIR / 'isrgrootx1.pem'
        cert_path.write_text(cert_content)
        print(f'SSL cert written to {cert_path}')


def ensure_database():
    """确保数据库存在"""
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            ssl={'ca': Config.MYSQL_SSL_CA},
        )
        with conn.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        conn.commit()
        conn.close()
        print(f'Database {Config.MYSQL_DATABASE} ready')
    except Exception as e:
        print(f'Database init warning: {e}')


def init_app():
    """初始化数据库表和管理员账号"""
    ensure_database()
    with app.app_context():
        db.create_all()
        from app.models import User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@blog.com',
                role='admin',
                is_active=True
            )
            admin_password = os.environ.get('ADMIN_PASSWORD', '258852258852')
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f'Admin account created: admin')


app = create_app()
ensure_ssl_cert()
init_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
