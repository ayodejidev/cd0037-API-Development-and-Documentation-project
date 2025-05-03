import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

from flaskr import create_app
from models import setup_db, Question, Category, db

# Load environment variables
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = os.getenv('DB_TEST_NAME', 'trivia_test')
        self.database_user = os.getenv('DB_USER', 'postgres')
        self.database_password = os.getenv('DB_PASSWORD', '')
        self.database_host = os.getenv('DB_HOST', 'localhost')
        self.database_port = os.getenv('DB_PORT', '5432')
        
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        
        # Create app with test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()
            
            # Add test categories
            categories = [
                Category(type='Science'),
                Category(type='Art'),
                Category(type='Geography'),
                Category(type='History'),
                Category(type='Entertainment'),
                Category(type='Sports')
            ]
            for category in categories:
                db.session.add(category)
            
            # Add test questions
            questions = [
                Question(
                    question='What is the capital of France?',
                    answer='Paris',
                    category='3',  # Geography
                    difficulty=1
                ),
                Question(
                    question='Who painted the Mona Lisa?',
                    answer='Leonardo da Vinci',
                    category='2',  # Art
                    difficulty=2
                ),
                Question(
                    question='What is the largest planet in our solar system?',
                    answer='Jupiter',
                    category='1',  # Science
                    difficulty=3
                )
            ]
            for question in questions:
                db.session.add(question)
            
            db.session.commit()

        # Sample question for use in tests
        self.new_question = {
            'question': 'What is the capital of Spain?',
            'answer': 'Madrid',
            'difficulty': 1,
            'category': 3
        }

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.execute(text('DROP TABLE IF EXISTS questions CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS categories CASCADE'))
            db.session.commit()
            db.session.close()

    def test_get_categories(self):
        """Test GET /categories endpoint"""
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        """Test GET /questions endpoint"""
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_sent_requesting_beyond_valid_page(self):
        """Test error handling for invalid page number"""
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        """Test DELETE /questions/<id> endpoint"""
        # First create a question to delete
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        question_id = data['created']

        # Now delete the question
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

    def test_422_if_question_does_not_exist(self):
        """Test error handling for deleting non-existent question"""
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_create_question(self):
        """Test POST /questions endpoint for creating new question"""
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])

    def test_400_if_question_creation_fails(self):
        """Test error handling for invalid question creation"""
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_search_questions(self):
        """Test POST /questions/search endpoint"""
        res = self.client().post('/questions/search', 
                               json={'searchTerm': 'capital'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_get_questions_by_category(self):
        """Test GET /categories/<id>/questions endpoint"""
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 1)

    def test_404_if_category_does_not_exist(self):
        """Test error handling for non-existent category"""
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_play_quiz(self):
        """Test POST /quizzes endpoint"""
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [],
                                   'quiz_category': {'id': 1, 'type': 'Science'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_422_if_quiz_play_fails(self):
        """Test error handling for invalid quiz play"""
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
