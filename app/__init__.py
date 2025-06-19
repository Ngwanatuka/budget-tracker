from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import click
from flask.cli import with_appcontext

db = SQLAlchemy()

# ✅ Proper CLI command
@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('✅ Initialized the database.')

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'secret'

    if test_config:
        app.config.update(test_config)
    else:
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'budget.db')

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from . import routes
    app.register_blueprint(routes.bp)

    # ✅ Register the CLI command with the Flask app
    app.cli.add_command(init_db_command)

    return app
