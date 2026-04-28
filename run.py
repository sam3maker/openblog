#!/usr/bin/env python3
"""博客平台启动入口"""
import os
import sys
import pymysql
from dotenv import load_dotenv

load_dotenv()

from app import create_app, db
from app.config import Config

# 先连接并创建数据库（如果不存在）
def ensure_database():
    try:
        conn = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            ssl={'ca': Config.MYSQL_SSL_CA},
        )
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{Config.MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        conn.close()
        print(f'数据库 {Config.MYSQL_DATABASE} 就绪')
    except Exception as e:
        print(f'数据库初始化警告: {e}')

ensure_database()

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # 创建管理员账号
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
            print(f'管理员账号已创建: admin / {admin_password}')
    app.run(debug=True, host='0.0.0.0', port=5000)
