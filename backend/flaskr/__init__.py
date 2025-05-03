from flask import Flask, request, abort, jsonify
from flask_cors import CORS
import random
from werkzeug.exceptions import HTTPException

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    # Set up CORS
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}
            return jsonify({
                'success': True,
                'categories': formatted_categories
            })
        except Exception as e:
            abort(500)

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            page = request.args.get('page', 1, type=int)
            start = (page - 1) * QUESTIONS_PER_PAGE
            end = start + QUESTIONS_PER_PAGE

            questions = Question.query.order_by(Question.id).all()
            formatted_questions = [question.format() for question in questions]
            current_questions = formatted_questions[start:end]

            if len(current_questions) == 0:
                abort(404)

            categories = Category.query.all()
            formatted_categories = {category.id: category.type for category in categories}

            return jsonify({
                'success': True,
                'questions': current_questions,
                'total_questions': len(formatted_questions),
                'categories': formatted_categories,
                'current_category': None
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(500)

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                abort(422)

            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(422)

    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            body = request.get_json()
            if not body:
                abort(400)

            new_question = body.get('question', None)
            new_answer = body.get('answer', None)
            new_category = body.get('category', None)
            new_difficulty = body.get('difficulty', None)

            if not all([new_question, new_answer, new_category, new_difficulty]):
                abort(400)

            question = Question(
                question=new_question,
                answer=new_answer,
                category=new_category,
                difficulty=new_difficulty
            )
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(422)

    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            body = request.get_json()
            search_term = body.get('searchTerm', '')
            
            questions = Question.query.filter(
                Question.question.ilike(f'%{search_term}%')
            ).all()
            
            formatted_questions = [question.format() for question in questions]
            
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': None
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(422)

    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_questions_by_category(category_id):
        try:
            # Check if category exists
            category = Category.query.get(category_id)
            if not category:
                abort(404)
                
            questions = Question.query.filter_by(category=str(category_id)).all()
            formatted_questions = [question.format() for question in questions]
            
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': category_id
            })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(422)

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()
            if not body:
                abort(422)
                
            previous_questions = body.get('previous_questions', [])
            quiz_category = body.get('quiz_category', None)

            if quiz_category:
                questions = Question.query.filter_by(category=str(quiz_category['id']))
            else:
                questions = Question.query

            questions = questions.filter(Question.id.notin_(previous_questions)).all()
            
            if questions:
                question = random.choice(questions)
                return jsonify({
                    'success': True,
                    'question': question.format()
                })
            else:
                return jsonify({
                    'success': True,
                    'question': None
                })
        except Exception as e:
            if isinstance(e, HTTPException):
                abort(e.code)
            abort(422)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable entity'
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app

