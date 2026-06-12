import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY ='plagiarism_detection-secret'
    SQLALCHEMY_BATABASE_URI ='sqlite:///'+ os.path.join(BASE_DIR, 'database', 'submissions.db')
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_EXTENSIONS ={'pdf','docx','txt'}