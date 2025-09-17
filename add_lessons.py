from app import create_app
from models import db, Lesson, Quiz

app = create_app()

with app.app_context():
    # Create sample lessons
    lessons = [
        Lesson(
            title="Recycling Basics",
            topic="recycling",
            content="Learn about recycling processes and benefits",
            xp_reward=10,
            quiz_id=1  # Assuming you have a quiz with ID 1
        ),
        Lesson(
            title="Understanding Climate Change",
            topic="climate",
            content="Learn about climate change causes and effects",
            xp_reward=10,
            quiz_id=2
        ),
        Lesson(
            title="Biodiversity Conservation",
            topic="biodiversity",
            content="Learn about biodiversity and conservation efforts",
            xp_reward=10,
            quiz_id=3
        ),
        Lesson(
            title="Water Conservation",
            topic="water",
            content="Learn about water conservation techniques",
            xp_reward=10,
            quiz_id=4
        )
    ]
    
    for lesson in lessons:
        db.session.add(lesson)
    
    db.session.commit()
    print("Sample lessons added successfully!")