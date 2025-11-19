from .models import Game
from project.application.models import Question
import json 
from django.conf import settings
from django.utils import timezone
from project.game.models import Game
from django.utils.dateparse import parse_datetime
from django.db.models import Count

# Helper file for this app.
def can_play_game(session_key, game=None): 
    conditions = [questions_number_is_sufficient(session_key), getattr(game, 'is_active') if game else True]
    return all(conditions)

def game_is_valid(request):
    # We want to ensure that the player enters the game from the link we provide
    if request.method == 'POST':
        game_secret = getattr(settings, 'GAME_SECRET')
        start_game = getattr(settings, 'GAME_START_ACTION')
        data = json.loads(request.body)
        if data and data.get('action')==start_game and data.get('game_secret')==game_secret:
            return True
    return None

# This should work for all combinations of questions, did not have the time to test it much though
def questions_number_is_sufficient(session_key):
    difficulty_map = Game.QUESTIONS_DIFFICULTY_MAP
    difficulty_totals = Question.objects.exclude(played_in_games__game__session_key=session_key) \
        .values('difficulty').annotate(num_questions=Count('id'))
    for diff, num in difficulty_map.items():
        match = next((item for item in difficulty_totals \
            if item['difficulty']==diff and num < item['num_questions']), None)
        if not match:
            return None
    return True

# Maybe the incoming date from client is timezone unaware.
def convert_timestamp_from_client(timestamp):
    dt = parse_datetime(timestamp)
    dt = timezone.make_aware(dt) if timezone.is_naive(dt) else dt
    return dt

def reset_game_state(game):
    record = {'lost_question': game.num_questions_in_round}
    game.rounds_data += [record]
    game.is_active = False
    game.num_questions_in_round = 0
    game.save()