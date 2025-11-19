from django.urls import path, include
from project.game.views import *

urlpatterns = [
    path('', welcome_to_the_game, name='start-game'),
    path('starting-game/', start_game, name='starting-game'),
    path('play-game/<int:id>/', PlayGame.as_view(), name='play-game'),
    path('update-game-timestamp/', update_game_timestamp, name='update-game-timestamp'),
    path('player-loses/', player_loses, name='player-loses'),
    path('destroy-game/', destroy_game, name='destroy-game')
]
