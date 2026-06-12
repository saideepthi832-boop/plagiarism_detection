from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    app.config['SECRET_KEY'] = 'plagiarism-detector-secret-2024'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database', 'submissions.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please login to continue.'

    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.drop_all()   # Reset DB for new schema
        db.create_all()

    return app

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))