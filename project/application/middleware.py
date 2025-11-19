import os
from django.shortcuts import render
from django.conf import settings
from project.game.models import Game
import psycopg2
from django.urls import reverse

# Force creation of session key in case of stale cookies
class SessionRefreshMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        not_stale = request.session.get('refresh_me')
        if not not_stale:
            request.session['refresh_me'] = True
        response = self.get_response(request)
        return response

class CustomErrorPagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        try:
            response = self.get_response(request)
            # Processing the response after the view level, to catch the result. 
            if response.status_code == 404:
                return render(request, 'error_404.html', status=404)
            if response.status_code == 500:
                return render(request, 'error_500.html', status=500)
            return response
        except Exception as e:
            return render(request, 'error_500.html', status=500)

class SelfDestructionMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request): 
        response = self.get_response(request)
        if request.path == reverse('destroy-game') and getattr(request, 'session', None) \
            and request.session.get('internal_redirect', None)==True:
            # We compensate people who might be in games at the moment of destruction 
            # (would need emails or strong credentials in real world, here its just for fun.)
            active_games = list(Game.objects.filter(is_active=True).values_list('id', flat=True).values_list('session_key'))
            base_dir = settings.BASE_DIR
            file_path = os.path.join(base_dir, 'compensations.txt')
            with open(file_path, 'w') as f:
                for session_key in active_games:
                    f.write('{}\n'.format(session_key))
            # I allow them to destroy the game, so let's be suicidal here. I know this should never happen in production.
            default_db = settings.DATABASES['default']
            db_name = default_db['NAME']
            db_user = default_db['USER']
            db_password = default_db['PASSWORD']
            db_host = default_db['HOST']
            connection = psycopg2.connect(dbname='postgres', user=db_user, password=db_password, host=db_host)
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{}';""".format(db_name))
            cursor.execute("DROP DATABASE IF EXISTS {};".format(db_name))
            connection.close()
        return response 
