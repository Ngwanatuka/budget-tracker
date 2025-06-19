from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)
    app.secret_key = 'secret'

    if test_config:
        app.config.update(test_config)

    from . import routes
    app.register_blueprint(routes.bp)

    return app