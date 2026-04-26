from flask import Flask
from routes.auth_routes import auth
from routes.admin_routes import admin
from routes.face_routes import face

app = Flask(__name__)
app.secret_key = "secret"

app.register_blueprint(auth)
app.register_blueprint(admin)
app.register_blueprint(face)

if __name__ == "__main__":
    app.run(debug=True)