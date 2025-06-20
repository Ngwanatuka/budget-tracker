from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import click
from flask.cli import with_appcontext

# ✅ Models package imports
from app.models import db
from app.models.user import User

# ✅ Flask-Login config
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect unauthorized users

# ✅ CLI to initialize DB
@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('✅ Initialized the database.')

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'super-secret-key'  # ⚠️ Replace with env var in prod

    # ✅ Config setup
    if test_config:
        app.config.update(test_config)
    else:
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'budget.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # ✅ Register Blueprints
    from .routes import bp as main_bp
    from .auth import auth as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # ✅ Use actual User model to load users
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Register CLI commands
    app.cli.add_command(init_db_command)

    return app
