from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Submission
from app.file_parser import extract_text, allowed_file
from app.detector import compare_documents
from app.ai_detector import detect_ai_content
import os

main = Blueprint('main', __name__)
UPLOAD_FOLDER = 'uploads'

# ─────────────────────────────
#  AUTH ROUTES
# ─────────────────────────────

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'student')

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('main.register'))

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            if user.role == 'instructor':
                return redirect(url_for('main.dashboard'))
            return redirect(url_for('main.index'))

        flash('Invalid email or password!', 'error')

    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ─────────────────────────────
#  STUDENT ROUTES
# ─────────────────────────────

@main.route('/')
@login_required
def index():
    return render_template('index.html', user=current_user)


@main.route('/submit', methods=['POST'])
@login_required
def submit():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF, DOCX, TXT files allowed'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Extract text from file
        new_text = extract_text(filepath)

        if not new_text or len(new_text.strip()) < 20:
            return jsonify({'error': 'File appears to be empty or too short'}), 400

        # Plagiarism detection vs previous submissions
        all_subs = Submission.query.all()
        existing = [{"title": s.filename, "text": s.content} for s in all_subs]
        report = compare_documents(new_text, existing)

        # ChatGPT / AI content detection
        ai_result = detect_ai_content(new_text)

        # Calculate overall similarity
        overall_sim = max(
            (r['overall_similarity'] for r in report),
            default=0.0
        )

        # Save submission to database
        sub = Submission(
            student_name=current_user.name,
            filename=filename,
            content=new_text,
            ai_probability=ai_result['ai_probability'],
            ai_verdict=ai_result['verdict'],
            overall_similarity=overall_sim,
            user_id=current_user.id
        )
        db.session.add(sub)
        db.session.commit()

        return jsonify({
            'report': report,
            'student': current_user.name,
            'ai_detection': {
                'ai_probability': ai_result['ai_probability'],
                'verdict': ai_result['verdict'],
                'is_chatgpt': ai_result.get('is_chatgpt', False),
                'method': ai_result.get('method', 'local'),
                'signals': ai_result['signals'],
                'found_phrases': ai_result.get('found_phrases', [])
            }
        })

    except Exception as e:
        print(f"Submit error: {e}")
        return jsonify({'error': 'An error occurred while processing the file'}), 500


# ─────────────────────────────
#  INSTRUCTOR ROUTES
# ─────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'instructor':
        return redirect(url_for('main.index'))

    submissions = Submission.query.order_by(
        Submission.submitted_at.desc()
    ).all()

    return render_template(
        'dashboard.html',
        submissions=submissions,
        user=current_user
    )


@main.route('/dashboard/delete/<int:sub_id>', methods=['POST'])
@login_required
def delete_submission(sub_id):
    if current_user.role != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403

    sub = Submission.query.get_or_404(sub_id)
    db.session.delete(sub)
    db.session.commit()
    flash('Submission deleted.', 'success')
    return redirect(url_for('main.dashboard'))