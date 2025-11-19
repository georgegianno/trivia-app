# This is an example of how the model's structure should be if the Game rounds really mattered. 
# The way I designed the game, it is not needed. If the game concept expands, then maybe this should be more appropriate
# but for now we save some joins by keeping things simple.

from django.db import models
from project.application.models import Question
from django.db.models import Count, Sum

class Game(models.Model):
    QUESTIONS_DIFFICULTY_MAP = {
        'easy': 4,
        'medium': 3,
        'hard': 3
    }
    session_key = models.CharField(max_length=100, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.session_key
    
class GameRound(models.Model):
    DEFAULT_COST = 5
    game = models.ForeignKey('game.Game', related_name='rounds', on_delete=models.CASCADE)
    questions = models.ManyToManyField('application.Question', through='game.RoundQuestion', related_name='rounds')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=DEFAULT_COST)
    date_created = models.DateTimeField(auto_now_add=True)
    
class RoundQuestion(models.Model):
    question = models.ForeignKey('application.Question', related_name='played_in_rounds', on_delete=models.CASCADE)
    round = models.ForeignKey('game.GameRound', related_name='question_rounds', on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True)
    answered_at = models.DateTimeField(null=True)