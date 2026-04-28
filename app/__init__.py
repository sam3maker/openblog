from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from app.config import Config, BASE_DIR

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__,
                template_folder=str(BASE_DIR / 'templates'),
                static_folder=str(BASE_DIR / 'static'))
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        return User.query.get(int(user_id))

    # i18n + 全局模板变量
    @app.context_processor
    def inject_globals():
        from app.models import SiteConfig
        from app.i18n import t, get_language, get_supported_languages
        return {
            'site_name': SiteConfig.get('site_name', 'OpenBlog'),
            'site_footer': SiteConfig.get('site_footer', 'OpenBlog - Open Source Blog Platform'),
            'site_notice': SiteConfig.get('site_notice', ''),
            'github_enabled': bool(Config.GITHUB_CLIENT_ID),
            't': t,
            'current_lang': get_language(),
            'languages': get_supported_languages(),
        }

    from app.routes import register_blueprints
    register_blueprints(app)

    return app
