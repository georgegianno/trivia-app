from django.contrib import admin
from django.urls import path, include
from project.application.views import QuestionListView, QuestionDetailView
from django.conf.urls import handler404, handler500
from django.shortcuts import render

# def error_404(request, exception):
#     return render(request, 'error_404.html', status=404)

# def error_500(request):
#     return render(request, 'error_500.html', status=500)

# handler404 = error_404
# handler500 = error_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project.application.urls')),
    path('game/', include('project.game.urls')),
]
