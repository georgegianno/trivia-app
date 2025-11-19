from django.shortcuts import render
from .mixins import CorrectAnswerMixin
from django.views.generic import ListView, DetailView, TemplateView
from .models import Question
from .forms import FilteringForm
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
import random

class HomeView(TemplateView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('question-list'))

class QuestionListView(ListView):
    model = Question
    template_name = 'application/question_list.html'
    context_object_name = 'questions'
    paginate_by = 5

    def get_queryset(self):
        return self.filter_questions(super().get_queryset().order_by('text'))  
    
    def filter_questions(self, qs):
        category = self.request.GET.get('category')
        difficulty = self.request.GET.get('difficulty')
        type = self.request.GET.get('type')
        # I assumed the 'question term' in the description of the task means some 
        # string (i)contained in the question's text.
        text = self.request.GET.get('text')  
        if category:
            qs = qs.filter(category__id=category)
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if type:
            qs = qs.filter(type=type)
        if text:
            qs = qs.filter(text__icontains=text)
        return qs          
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = FilteringForm(self.request.GET)
        context['num_total_results'] = self.get_queryset().count()
        return context

class QuestionDetailView(CorrectAnswerMixin, DetailView):
    model = Question
    context_object_name = 'question'
    pk_url_kwarg = 'id'
    
    def get_question(self):
        return self.get_object()
    
    def get_success_url(self):
        return reverse('question-detail', kwargs={'id': self.get_question().id})
    
    def post(self, *args, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        result = super().answer_is_correct(*args, **kwargs)
        if result is None:
            messages.warning(self.request, 'Please select an answer!')
        else:
            if result is False:
                messages.error(self.request, 'Wrong answer!')
            else:
                messages.success(self.request, 'Correct answer!')
        return render(self.request, self.template_name, context)