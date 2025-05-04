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

    def test_play_quiz_with_all_category(self):
        """Test POST /quizzes endpoint with ALL category"""
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [],
                                   'quiz_category': {'id': 0, 'type': 'All'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertIn(data['question']['category'], ['1', '2', '3', '4', '5', '6'])

    def test_play_quiz_with_previous_questions(self):
        """Test POST /quizzes endpoint with previous questions"""
        # First get a question
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [],
                                   'quiz_category': {'id': 0, 'type': 'All'}
                               })
        data = json.loads(res.data)
        first_question = data['question']

        # Now get another question, excluding the first one
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [first_question['id']],
                                   'quiz_category': {'id': 0, 'type': 'All'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertNotEqual(data['question']['id'], first_question['id'])

    def test_play_quiz_with_specific_category(self):
        """Test POST /quizzes endpoint with specific category"""
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [],
                                   'quiz_category': {'id': 3, 'type': 'Geography'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], '3')

    def test_play_quiz_no_more_questions(self):
        """Test POST /quizzes endpoint when no more questions are available"""
        # Get all question IDs
        res = self.client().get('/questions')
        data = json.loads(res.data)
        all_question_ids = [q['id'] for q in data['questions']]

        # Try to get a question with all previous questions
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': all_question_ids,
                                   'quiz_category': {'id': 0, 'type': 'All'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertIsNone(data['question'])

    def test_play_quiz_invalid_category(self):
        """Test POST /quizzes endpoint with invalid category"""
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': [],
                                   'quiz_category': {'id': 999, 'type': 'Invalid'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

    def test_get_categories_failure(self):
        """Test GET /categories endpoint failure"""
        # Simulate database error by dropping the categories table
        with self.app.app_context():
            db.session.execute(text('DROP TABLE IF EXISTS categories CASCADE'))
            db.session.commit()
        
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Internal server error')

    def test_get_questions_failure(self):
        """Test GET /questions endpoint failure"""
        # Simulate database error by dropping the questions table
        with self.app.app_context():
            db.session.execute(text('DROP TABLE IF EXISTS questions CASCADE'))
            db.session.commit()
        
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 500)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Internal server error')

    def test_delete_question_success(self):
        """Test DELETE /questions/<id> endpoint success"""
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

        # Verify question is actually deleted by trying to delete it again
        res = self.client().delete(f'/questions/{question_id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_create_question_failure(self):
        """Test POST /questions endpoint failure cases"""
        # Test missing required fields
        incomplete_question = {
            'question': 'Test question',
            'answer': 'Test answer'
            # Missing category and difficulty
        }
        res = self.client().post('/questions', json=incomplete_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

        # Test empty request body
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_search_questions_failure(self):
        """Test POST /questions/search endpoint failure"""
        # Test with empty search term (should return all questions)
        res = self.client().post('/questions/search', 
                               json={'searchTerm': ''})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']) > 0)  # Should return all questions
        self.assertEqual(data['total_questions'], len(data['questions']))

        # Test with missing searchTerm
        res = self.client().post('/questions/search', 
                               json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad request')

    def test_get_questions_by_category_failure(self):
        """Test GET /categories/<id>/questions endpoint failure"""
        # Test with non-existent category
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_play_quiz_failure(self):
        """Test POST /quizzes endpoint failure cases"""
        # Test with missing quiz_category
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': []
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')

        # Test with invalid previous_questions format
        res = self.client().post('/quizzes', 
                               json={
                                   'previous_questions': 'not a list',
                                   'quiz_category': {'id': 1, 'type': 'Science'}
                               })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable entity')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
