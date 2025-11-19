from django.test import TestCase
from project.game.models import Game, GameQuestion, Winner
from project.application.models import Question, Category

class GameModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name='Science')
        cls.q = Question.objects.create(
            text='What is 2+2?',
            category=cat,
            difficulty='easy',
            type='multiple'
        )
        cls.game = Game.objects.create(session_key='george1993', cost_per_round=5)
        GameQuestion.objects.create(game=cls.game, question=cls.q)

    def test_game_str(self):
        self.assertEqual(str(self.game), 'george1993')

    def test_winner_reward_calculation(self):
        self.game.is_active = True
        self.game.times_played = 3
        self.game.save()
        reward = Winner.get_reward()
        self.assertIsInstance(reward, (int, float))
