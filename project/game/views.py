import json
from django.shortcuts import render
from .models import Game, GameQuestion
from project.application.models import Question
from project.application.views import CorrectAnswerMixin
from django.views.generic import DetailView
from django.urls import reverse
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.db.models import F
from django.conf import settings
from project.game.models import Game, Winner
from django.contrib import messages
from .helpers import convert_timestamp_from_client, reset_game_state, can_play_game, game_is_valid
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

def welcome_to_the_game(request):
    if not can_play_game(request):
        raise Http404
    return render(request, 'game/welcome_to_the_game.html', {'game_cost': '{} money'.format(Game.DEFAULT_COST)})

def start_game(request):
    session_key = getattr(request.session, 'session_key', None)
    if game_is_valid(request):
        # We can optionally use a 'cost' parameter, but I use only the default cost to keep it simple
        cost_per_round = request.POST.get('cost') or Game.DEFAULT_COST
        game, _ = Game.objects.update_or_create(session_key=request.session.session_key,
            defaults = {'is_active': True, 'num_questions_in_round': 1, 'cost_per_round': cost_per_round})
        if not _:
            Game.objects.filter(id=game.id).update(times_played=F('times_played') + 1)
        redirect_url = reverse('play-game', kwargs={'id': game.id})
        # The following line ensures that the play-game page can be accesses only when we allow it
        request.session['internal_redirect'] = True
        return JsonResponse({'redirect_url': redirect_url}, status=200)
    game = Game.objects.filter(session_key=session_key, is_active=True).first()
    if game:
        redirect_url = reverse('play-game', kwargs={'id': game.id})
        request.session['internal_redirect'] = True
        return redirect(redirect_url)
    raise Http404

# This function ensures the server is up to date with the time that user sees the question 
def update_game_timestamp(request):
    session_key = getattr(request.session, 'session_key', None)
    if not session_key:
        return JsonResponse({'success': False}, status=404)
    game_secret = getattr(settings, 'GAME_SECRET')
    game_update_action = getattr(settings, 'GAME_UPDATE_ACTION')
    data = json.loads(request.body)
    if data and data.get('game_secret')==game_secret and data.get('action')==game_update_action:
        timestamp = convert_timestamp_from_client(data.get('timestamp'))
        if timestamp:
            last_question = GameQuestion.objects.filter(
                game__session_key=session_key, game__is_active=True).last()
            last_question.timestamp = timestamp
            last_question.save()
            message_html = render_to_string('messages.html', {'messages': ['Time is running!']}) \
                    if last_question.game.num_questions_in_round == 1 else None
            return JsonResponse({'success': True, 'message_html': message_html}, status=200)
    raise JsonResponse({'success': False}, status=404)
    
# This function is called when player loses on time or closes their tab. Csrf does not really matter in this situation.  
@csrf_exempt
def player_loses(request):
    session_key = getattr(request.session, 'session_key', None)
    if not session_key:
        return JsonResponse({'success': False}, status=404)
    player_loses_action = getattr(settings, 'PLAYER_LOSES_ACTION')
    game_secret = getattr(settings, 'GAME_SECRET')
    data = json.loads(request.body)
    if not data.get('no_message'):  
        messages.error(request, 'Your time finished. You lost this game.')
    if data and data.get('game_secret')==game_secret and data.get('action')==player_loses_action:
        game = Game.objects.filter(session_key=session_key, is_active=True).first()
        if game:
            reset_game_state(game)
            return JsonResponse({'success': True, 'redirect_url': reverse('start-game')}, status=200)
    return JsonResponse({'success': False}, status=404)            
        
class PlayGame(CorrectAnswerMixin, DetailView):
    model = Game
    context_object_name = 'game'
    losing_template = 'game/welcome_to_the_game.html'
    winning_template = 'game/winner.html'
    time_limit = Game.TIME_LIMIT
    
    def get_invalid_url(self):
        return redirect(reverse('start-game'))
    
    def get_question_difficulty(self):
        counter = []
        for key, value in Game.QUESTIONS_DIFFICULTY_MAP.items():
            counter.append(value)
            if self.object.num_questions_in_round <= sum(counter):
                return key
        return ''
    
    def dispatch(self, request, *args, **kwargs):  
        self.object = self.get_object() 
        if not self.object.is_active:
            messages.error(request, 'This game is not active anymore.')
            return self.get_invalid_url()
        self.session_key = self.request.session.session_key 
        if self.request.method == 'GET':
            # I use this way to communicate between requests. The 'internal_redirect' allows me to manipulate
            # when the page is available to the user. SHould be one time use, so it's best to immidiately delete
            # it from session when seen.
            if not request.session.get('internal_redirect'):
                return self.get_invalid_url()
            del request.session['internal_redirect']
            request.session.modified = True
            self.question = Question.objects.filter(difficulty=self.get_question_difficulty()) \
                .exclude(played_in_games__game__session_key=self.session_key).order_by('?').first()
            if self.question:
                GameQuestion.objects.create(question=self.question, game=self.object)
            else:
                messages.error(request, 'No questions in db at the moment')
                return self.get_invalid_url()
        elif self.request.method == 'POST':
            game_question = GameQuestion.objects.filter(game=self.object).last()
            if not game_question:
                messages.error(request, 'No question found.')
                return self.get_invalid_url()
            self.question = game_question.question
            self.timestamp = game_question.timestamp
        else:
            return self.get_invalid_url()
        return super().dispatch(request, *args, **kwargs)
    
    def get_question(self):
        return self.question
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context['update_game_timestamp'] = True
            context['num_question'] = self.object.num_questions_in_round
            context['time_limit'] = Game.TIME_LIMIT
            context['payer_loses_action'] = getattr(settings, 'PLAYER_LOSES_ACTION')
        return context
    
    def answer_is_in_time(self):
        if not self.timestamp:
            return False
        client_timestamp = convert_timestamp_from_client(self.request.POST.get('client_timestamp'))
        if not client_timestamp:
            return False
        difference = client_timestamp - self.timestamp
        return difference.total_seconds() <= self.time_limit
    
    def player_lost_response(self, **kwargs):
        reset_game_state(self.object)
        if kwargs.get('reason') == 'time':
            messages.error(self.request, 'Your time finished. You lost this game.')  
        else:
            messages.error(self.request, 'Your answer is wrong. You lost this game.')
        return self.get_invalid_url()
    
    def winner_response(self, **kwargs):
        context = self.get_context_data(**kwargs)
        self.request.session['internal_redirect'] = True
        self.object.is_active = False
        record = {'winner': True}
        self.object.rounds_data += [record]
        self.object.num_questions_in_round = 0
        self.object.save()
        winner = Winner.objects.filter(session_key=self.request.session.session_key).first() or \
            Winner.objects.create(session_key=self.request.session.session_key)
        winner.rewards.append(Winner.get_reward())
        winner.save()
        context['reward'] = winner.get_reward()
        context['game_cost'] = '{} money'.format(Game.DEFAULT_COST)
        Game.objects.all().delete()
        return render(self.request, self.winning_template, context)
    
    def player_wins_actions(self, **kwargs):
        self.request.session['internal_redirect'] = True
        self.object.num_questions_in_round += 1
        self.object.save()
        total_questions = kwargs['total_questions']
        if 0 < self.object.num_questions_in_round <= total_questions:
            message = 'Your answer is correct! '
            if 1 <= self.object.num_questions_in_round < total_questions:
                message += 'Time is running!'
            messages.success(self.request, message)
    
    def post(self, *args, **kwargs):
        if not self.answer_is_in_time():
            kwargs['reason'] = 'time'
            return self.player_lost_response(**kwargs)
        answer_is_correct = super().answer_is_correct()
        if not answer_is_correct:
            return self.player_lost_response(**kwargs)
        total_questions = sum(Game.QUESTIONS_DIFFICULTY_MAP.values())
        kwargs['total_questions'] = total_questions
        if 0 < self.object.num_questions_in_round < total_questions:
            self.player_wins_actions(**kwargs)
            return redirect(self.request.path)
        return self.winner_response(**kwargs)
        
def destroy_game(request):
    if not request.session.get('internal_redirect'):
        raise Http404
    # Let the request pass through the middleware and terminate this horrible game.
    return redirect(request.path)
    