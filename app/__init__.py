from flask import Flask

def create_app():
    app = Flask(__name__)
    app.secret_key = 'secret'

    from . import routes
    app.register_blueprint(routes.bp)

    return app