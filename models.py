from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Initialize SQLAlchemy instance
db = SQLAlchemy()

# User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    total_xp = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with scores
    scores = db.relationship('UserScore', backref='user', lazy=True)
    # Relationship with achievements
    achievements = db.relationship('Achievement', secondary='user_achievements', backref='users')
    # Relationship with completed lessons
    completed_lessons = db.relationship('UserLesson', backref='user', lazy=True)

# Quiz model
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationship with questions
    questions = db.relationship('Question', backref='quiz', lazy=True)
    # Relationship with scores
    scores = db.relationship('UserScore', backref='quiz', lazy=True)

# Question model
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(200), nullable=False)
    option_b = db.Column(db.String(200), nullable=False)
    option_c = db.Column(db.String(200), nullable=False)
    option_d = db.Column(db.String(200), nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # 'a', 'b', 'c', or 'd'

# UserScore model
class UserScore(db.Model):
    __tablename__ = 'user_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # Number of correct answers
    xp_earned = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

# Achievement model
class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))  # Path to achievement icon

# Junction table for User-Achievement many-to-many relationship
class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

# Lesson model (NEW)
class Lesson(db.Model):
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    xp_reward = db.Column(db.Integer, default=10)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with quiz
    quiz = db.relationship('Quiz', backref='lesson')

# UserLesson model to track completed lessons (NEW)
class UserLesson(db.Model):
    __tablename__ = 'user_lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    xp_earned = db.Column(db.Integer, nullable=False)
    
    # Relationship with lesson
    lesson = db.relationship('Lesson', backref='completions')