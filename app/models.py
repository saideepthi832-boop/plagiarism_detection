from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from pytz import timezone

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')  # 'student' or 'instructor'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    ai_probability = db.Column(db.Integer, default=0)
    ai_verdict = db.Column(db.String(100), default='')
    overall_similarity = db.Column(db.Float, default=0.0)
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone('Asia/Kolkata')).replace(tzinfo=None))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)