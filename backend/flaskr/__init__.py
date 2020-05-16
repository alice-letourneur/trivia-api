import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  CORS(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET')
    return response

  @app.route('/categories')
  def get_categories():
    categories = Category.query.all()
    formatted_categories = {category.id:category.type for category in categories}

    return jsonify(
      {
        'success': True,
        'categories': formatted_categories,
      }
    )

  @app.route('/questions')
  def get_questions():
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    start = (page - 1) * 10
    end = start + 10
    all_questions = Question.query.all()

    if search_term:
      questions = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
    else:
      questions = all_questions[start:end]

    if not questions:
      abort(404)

    formatted_questions = [question.format() for question in questions]
    categories = Category.query.all()
    formatted_categories = {category.id:category.type for category in categories}

    return jsonify(
      {
        'success': True,
        'questions': formatted_questions,
        'total_questions': len(all_questions),
        'categories': formatted_categories,
        'current_category': None,
      }
    )

  @app.route('/questions/<id>', methods=['DELETE'])
  def delete_question(id):
    question = Question.query.get(id)

    try:
      question.delete()

      return jsonify(
        {
          'id': id,
          'success': True,
        }
      )
    except:
      abort(422)

  @app.route('/questions', methods=['POST'])
  def create_question():
    try:
      body = request.get_json()
      question = Question(
        question=body.get('question'),
        answer=body.get('answer'),
        difficulty=body.get('difficulty'),
        category=body.get('category'),
      )
      question.insert()

      return jsonify(
        {
          'success': True,
          'id': question.id,
        }
      )
    except:
      abort(422)

  @app.route('/categories/<id>/questions')
  def get_category_questions(id):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.filter_by(category=id).all()
    formatted_questions = [question.format() for question in questions]
    current_category = Category.query.get(id)

    if not formatted_questions:
      abort(404)

    return jsonify(
      {
        'success': True,
        'questions': formatted_questions[start:end],
        'total_questions': len(formatted_questions),
        'current_category': current_category.format(),
      }
    )

  @app.route('/quizzes', methods=['POST'])
  def quiz_question():
    body = request.get_json()
    previous_questions = body.get('previous_questions', [])
    quiz_category_id = body.get('quiz_category', 0)

    if quiz_category_id == 0:
      next_question = Question.query.filter(Question.id.notin_(previous_questions)).order_by(func.random()).first()
    else:
      next_question = Question.query.filter(Question.id.notin_(previous_questions), Question.category == quiz_category_id).order_by(func.random()).first()

    if next_question:
      formatted_question = next_question.format()
    else:
      formatted_question = False

    return jsonify(
      {
        'success': True,
        'question': formatted_question,
      }
    )

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Not found",
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unprocessable",
    }), 422

  @app.errorhandler(405)
  def not_allowed(error):
    return jsonify({
      "success": False,
      "error": 405,
      "message": "Method not allowed",
    }), 405

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "error": 400,
      "message": "Bad request",
    }), 400

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Server error",
    }), 500

  return app
