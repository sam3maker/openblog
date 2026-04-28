from app.routes.auth import auth_bp
from app.routes.blog import blog_bp
from app.routes.community import community_bp
from app.routes.admin import admin_bp
from app.routes.user import user_bp
from app.routes.api import api_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(api_bp)
