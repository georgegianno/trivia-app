from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from project.application.models import Question, Category
from project.game.models import Game, GameQuestion
from django.conf import settings
import json
from project.application.helpers import hash_text

class GameLogicFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        session = self.client.session
        session.save()  
        self.session_key = session.session_key
        settings.GAME_SECRET = 'secret'
        settings.GAME_START_ACTION = 'start'
        settings.GAME_UPDATE_ACTION = 'update'
        settings.PLAYER_LOSES_ACTION = 'lose'

        self.category = Category.objects.create(
            name='General',
            hash=hash_text('General')
        )
        self.question = Question.objects.create(
            text='Test Q',
            difficulty='easy',
            type='multiple',
            category=self.category,
            hash=hash_text('Test Q')
        )

    def test_starting_game_creates_game(self):
        url = reverse('starting-game')
        response = self.client.post(
            url,
            data=json.dumps({
                'action': settings.GAME_START_ACTION,
                'game_secret': settings.GAME_SECRET
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('redirect_url', response.json())
        self.assertTrue(Game.objects.filter(session_key=self.session_key).exists())


    def test_update_game_timestamp(self):
        game = Game.objects.create(
            session_key=self.session_key,
            is_active=True,
            num_questions_in_round=1
        )
        GameQuestion.objects.create(
            game=game,
            question=self.question,
            timestamp=timezone.now()
        )

        url = reverse('update-game-timestamp')
        response = self.client.post(
            url,
            data=json.dumps({
                'action': settings.GAME_UPDATE_ACTION,
                'game_secret': settings.GAME_SECRET,
                'timestamp': timezone.now().isoformat()
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

    def test_player_loses(self):
        game = Game.objects.create(
            session_key=self.session_key,
            is_active=True,
            num_questions_in_round=1
        )

        url = reverse('player-loses')
        response = self.client.post(
            url,
            data=json.dumps({
                'action': settings.PLAYER_LOSES_ACTION,
                'game_secret': settings.GAME_SECRET
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        game.refresh_from_db()
        self.assertFalse(game.is_active)
