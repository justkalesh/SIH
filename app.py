from flask import Flask, render_template, jsonify, request
from models import db, User, Quiz, Question, UserScore, Achievement, UserAchievement, Lesson, UserLesson
from flask_login import LoginManager, login_user, login_required, current_user
import os

def create_app():
    # Create Flask app instance
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ecoquest-secret-key-2024'  # Change this in production!
    
    # Configure database
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'ecoquest.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize database with app
    db.init_app(app)
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Basic route for testing
    @app.route('/')
    def hello():
        return "EcoQuest API is running! Database initialized successfully."
    
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
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)