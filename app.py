from flask import Flask
from routes.user_routes import user_bp
from routes.account_routes import account_bp

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(account_bp)

if __name__ == "__main__":
    app.run(debug=True, port=8080)
