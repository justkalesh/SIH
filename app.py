from flask import Flask, render_template, jsonify, request
from models import db, User, Quiz, Question, UserScore, Achievement, UserAchievement, Lesson, UserLesson
from flask_login import LoginManager, login_user, login_required, current_user
import os

def create_app():
    # Create Flask app instance
    app = Flask(__name__, template_folder='templates', static_folder='templates/static')
    app.config['SECRET_KEY'] = 'ecoquest-secret-key-2024'
    
    # Configure database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ecoquest.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'login'  # Using simple login page
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Landing page
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Lesson routes
    @app.route('/lesson/<int:lesson_id>')
    @login_required
    def view_lesson(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has already completed this lesson
        completed = UserLesson.query.filter_by(
            user_id=current_user.id, 
            lesson_id=lesson_id
        ).first() is not None
        
        return render_template(f'lesson_{lesson.topic.lower()}.html', 
                             lesson=lesson, 
                             completed=completed)
    
    @app.route('/complete_lesson/<int:lesson_id>', methods=['POST'])
    @login_required
    def complete_lesson(lesson_id):
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Check if user has already completed this lesson
        existing_completion = UserLesson.query.filter_by(
            user_id=current_user.id, 
            lesson_id=lesson_id
        ).first()
        
        if existing_completion:
            return jsonify({
                'success': False, 
                'message': 'Lesson already completed',
                'xp': current_user.total_xp
            })
        
        # Award XP to user
        current_user.total_xp += lesson.xp_reward
        
        # Record lesson completion
        user_lesson = UserLesson(
            user_id=current_user.id,
            lesson_id=lesson_id,
            xp_earned=lesson.xp_reward
        )
        db.session.add(user_lesson)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'You earned {lesson.xp_reward} XP!',
            'xp': current_user.total_xp
        })
    
    # Mock login route for testing (replace with real authentication later)
    @app.route('/mock_login/<int:user_id>')
    def mock_login(user_id):
        user = User.query.get(user_id)
        if user:
            login_user(user)
            return f"Logged in as {user.username}"
        return "User not found"
    
    # Simple login page for Flask-Login redirects
    @app.route('/login')
    def login():
        return "Please visit /mock_login/1 to log in for testing"
    
    # Quiz routes
    @app.route('/quiz/<int:quiz_id>')
    @login_required
    def take_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        if not questions:
            return "No questions available for this quiz yet."
        
        return render_template('quiz.html', quiz=quiz, questions=questions)
    
    @app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
    @login_required
    def submit_quiz(quiz_id):
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        # Check if user has already completed this quiz
        existing_score = UserScore.query.filter_by(
            user_id=current_user.id, 
            quiz_id=quiz_id
        ).first()
        
        # Calculate score
        correct_answers = 0
        total_questions = len(questions)
        
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer == question.correct_answer:
                correct_answers += 1
        
        # Calculate XP (10 XP per correct answer)
        xp_earned = correct_answers * 10
        
        if existing_score:
            # User has already completed this quiz - don't give XP again
            return jsonify({
                'success': True,
                'score': correct_answers,
                'total': total_questions,
                'percentage': round((correct_answers / total_questions) * 100, 1),
                'xp_earned': 0,  # No XP for retaking
                'total_xp': current_user.total_xp,
                'retake': True
            })
        else:
            # First time completing - give XP
            current_user.total_xp += xp_earned
            
            # Record quiz completion
            user_score = UserScore(
                user_id=current_user.id,
                quiz_id=quiz_id,
                score=correct_answers,
                xp_earned=xp_earned
            )
            db.session.add(user_score)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'score': correct_answers,
                'total': total_questions,
                'percentage': round((correct_answers / total_questions) * 100, 1),
                'xp_earned': xp_earned,
                'total_xp': current_user.total_xp,
                'retake': False
            })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)