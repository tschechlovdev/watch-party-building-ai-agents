from flask import Flask
from flask_cors import CORS
from models import init_db

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])

# Initialise DB on startup (creates todos.db + table if missing)
with app.app_context():
    init_db()

# Routes are registered below (implemented in full here)
from routes import todos_bp  # noqa: E402
app.register_blueprint(todos_bp)


@app.errorhandler(404)
def not_found(e):
    from flask import jsonify
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
