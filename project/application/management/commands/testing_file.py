from project.application.models import *
from django.core.management.base import BaseCommand
from django.db.models import JSONField
from django.apps import apps
from django.db.models import Q
from project.application.helpers import count_model_records
from django.shortcuts import render
from project.game.models import Game, GameQuestion
from project.application.models import Question, Answer, QuestionAnswer
from project.application.views import CorrectAnswerMixin
from django.views.generic import ListView, DetailView
from django.urls import reverse
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
import json
from project.game.models import Game
from project.application.models import Question
from django.utils.dateparse import parse_datetime
from django.contrib import messages

# class Command(BaseCommand):
#     def handle(self, *args, **options):
        # questions = Question.objects.all()
        # dubs_qs =questions.annotate(c=Count('answers', filter=Q(answers__is_correct=True))).filter(c__gt=1).values_list('id',flat=True)
        # duplicates = list(questions.filter(id__in=dubs_qs))
        # for duplicate in duplicates:
        #     correct_answers = duplicate.answers.filter(is_correct=True)
        #     print('Question with more correct answers: Question{}: Answers:{}'.format(duplicate, correct_answers))
        # print('Db records counts')
        # count_model_records(['application', 'game'])
        # for question in list(questions):
        #     if question.answers.count() not in [2, 4]:
        #         print('Wrong answers number for question with id: {}'.format(question.id))
        # print('Ectra check for duplicates')
        # print(QuestionAnswer.objects.filter(is_correct=True).count())
        # print(questions.count())
        # games = Game.objects.all()
        # q = 0
        # for game in games:
        #     q += game.times_played * game.cost_per_round
        # print(q)
        # print(Game.objects.filter(is_active=True).values('id'))
        # q = Question.objects.filter(difficulty='hard').first()
        # Question.objects.exclude(id=q.id).delete()
        # print(Question.objects.filter(difficulty='hard').count())
        # print(Game.objects.last().__dict__)
        # print(Game.objects.all().delete())
        # print(Game.objects.values())
        # print(Question.objects.last().text)
        # text = "What is the name of the villian in the 2015 Russian-American Sci-Fi Movie \"Hardcore Henry\"?"
        # w = Question.objects.first()
        # w.text = text
        # w.save()
        # print(Question.objects.filter(text=text))
        # print(Question.objects.first().answers.all())
        # questions_to_create = []
        # answers_to_create = []
        # base_string = ['What is num + num ?']*10
        # q_pairs = [(i, i) for i in range(1, 11)]
        # for num, q in enumerate(base_string):
        #     base_string[num] = q.replace('num', str(q_pairs[num][0]))
        # for num, text in enumerate(base_string):
        #     q = Question(text=text, hash=hash_text(text), category=)
        #     questions_to_create.append()
        # print(Game.objects.all().count())
        # print(Game.objects.all().filter(is_active=True))
        # print(Game.objects.first().__dict__)
        
        