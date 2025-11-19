from django.urls import path, include
from project.application.views import HomeView, QuestionListView, QuestionDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('questions/', QuestionListView.as_view(), name='question-list'),
    path('questions/<int:id>/', QuestionDetailView.as_view(), name='question-detail'),
]
