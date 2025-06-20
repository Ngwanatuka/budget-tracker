from app import create_app
from app.models import db
import os

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

