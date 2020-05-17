import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_username = "aliceletourneur"
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}@{}/{}".format(self.database_username, 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_questions_without_page_specified_default_to_first_page(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(len(data['questions']), 10)
        self.assertTrue(len(data['questions']) < data['total_questions'])
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_with_valid_page_specified(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(len(data['questions']), 9)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_with_invalid_page_specified(self):
        res = self.client().get('/questions?page=45')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_get_questions_matching_search_term_when_results_found(self):
        res = self.client().get('/questions?search=what')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))
        self.assertEqual(len(data['questions']), 8)
        self.assertEqual(data['total_questions'], 19)
        self.assertEqual(data['current_category'], None)

    def test_get_questions_matching_search_term_when_no_results_found(self):
        res = self.client().get('/questions?search=noresults')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Not found")

    def test_delete_question_when_it_doesn_t_exist(self):
        initial_total_questions = Question.query.count()
        res = self.client().delete('/questions/41')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Unprocessable")
        self.assertEqual(Question.query.count(), initial_total_questions)

    def test_create_then_delete_question(self):
        initial_total_questions = Question.query.count()

        new_question = {
            'question': 'Are all tests passing?',
            'answer': 'Yes',
            'category': 2,
            'diffculty': 4
        }

        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['id'])
        new_question_id = str(data['id'])

        self.assertEqual(Question.query.count(), initial_total_questions + 1)
        self.assertTrue(Question.query.get(new_question_id))

        res = self.client().delete('/questions/' + new_question_id)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], new_question_id)
        self.assertEqual(Question.query.count(), initial_total_questions)

    def test_get_category_questions(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 3)
        self.assertEqual(data['total_questions'], 3)
        self.assertEqual(data['current_category'], {'id': 1, 'type': 'Science'})

    def test_get_quizz_question_without_category_specified(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_get_quizz_question_with_category_specified(self):
        res = self.client().post('/quizzes', json={'quiz_category': '1', 'previous_questions': []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        question_id = str(data['question']['id'])
        self.assertEqual(Question.query.get(question_id).category, 1)


    def test_get_quizz_question_when_no_more_question_available(self):
        res = self.client().post('/quizzes', json={'quiz_category': '1', 'previous_questions': [20, 21, 22]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], False)

    def test_fail_when_undefined_method(self):
        res = self.client().get('/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()