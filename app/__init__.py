from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
import click
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuration
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev-key'),
        DEBUG=os.getenv('DEBUG', 'False').lower() in ['true', '1'],
        WTF_CSRF_ENABLED=True,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL') + os.path.join(
            os.path.abspath(os.path.dirname(__file__)), 
            'budget.db'
        )
    )
    
    if test_config:
        app.config.update(test_config)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import and register blueprints
    from .routes import bp as main_bp
    from .auth import auth as auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        from .models.user import User  # Local import to prevent circular imports
        return User.query.get(int(user_id))

    # CLI commands
    @app.cli.command('init-db')
    def init_db_command():
        """Initialize the database."""
        with app.app_context():
            db.create_all()
        click.echo('✅ Initialized the database.')

    return app