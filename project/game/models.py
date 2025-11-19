from django.db import models
from django.db.models import Sum
from decimal import Decimal as D

# One time question for user to answer.
class GameQuestion(models.Model):
    question = models.ForeignKey('application.Question', related_name='played_in_games', on_delete=models.CASCADE)
    game = models.ForeignKey('game.Game', related_name='played_questions', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(null=True)

    class Meta:
        ordering = ['id']
        
class Game(models.Model):
    QUESTIONS_DIFFICULTY_MAP = {
        'easy': 4,
        'medium': 3,
        'hard': 3
    }
    DEFAULT_COST = 5
    TIME_LIMIT =  7

    # The session key represents some user credential for identification.
    session_key = models.CharField(max_length=100, unique=True)
    # Seen question by user with this session key.
    questions = models.ManyToManyField('application.Question', through='GameQuestion', related_name='games')
    # Number of questions in round is positive only when game is active.
    num_questions_in_round = models.IntegerField(default=0)
    cost_per_round = models.DecimalField(max_digits=10, decimal_places=2, default=DEFAULT_COST)
    times_played = models.IntegerField(default=1)
    #  This is used just for storing the question that user did not answer correct, on time or closed browser tab (just for the record, but nice to have.)
    rounds_data = models.JSONField(default=list)
    date_created = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.session_key
    
class Winner(models.Model):
    session_key = models.CharField(max_length=100)
    rewards = models.JSONField(default=list)
    
    @staticmethod
    def get_reward():
        totals = Game.objects.exclude(is_active=True).aggregate(
            total_times=Sum('times_played'), total_money=Sum('cost_per_round')
        )
        total_price = (totals.get('total_times') or D('0.00'))*(totals.get('total_money') or D('0.00'))
        return int(total_price) if total_price.to_integral_value() else float(total_price)
    