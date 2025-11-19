from django.test import TestCase
from project.game.helpers import reset_game_state, questions_number_is_sufficient
from project.game.models import Game
from project.application.models import Question, Category

class HelpersTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cat = Category.objects.create(name='Math')
        cls.q = Question.objects.create(
            text='What is 3+5?', category=cls.cat, difficulty='easy', type='multiple'
        )
        cls.game = Game.objects.create(session_key='key1')

    def test_questions_number_is_sufficient(self):
        result = questions_number_is_sufficient(self.game.session_key)
        self.assertIsNone(result) 

    def test_reset_game_state(self):
        self.game.num_questions_in_round = 1
        reset_game_state(self.game)
        self.assertFalse(self.game.is_active)
        self.assertEqual(self.game.num_questions_in_round, 0)
        self.assertEqual(self.game.rounds_data[-1], {'lost_question': 1})
