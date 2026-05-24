from datetime import datetime

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=False)
    app.config["SECRET_KEY"] = "change-this-secret-in-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.context_processor
    def inject_now():
        return {"now": datetime.utcnow()}

    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.admin import admin_bp
    from .routes.user import user_bp
    from .routes.ai import ai_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ai_bp)

    with app.app_context():
        db.create_all()
        ensure_admin_exists()

    return app


def ensure_admin_exists():
    from .models import User

    existing = User.query.filter_by(username="admin").first()
    if not existing:
        admin = User(
            username="admin",
            email="admin@library.local",
            role="admin",
            is_active=True,
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
