from django.conf import settings

# Populates secret credentials for the games in the templates.
def game_secret(request):
    context = {
        'game_secret': getattr(settings, 'GAME_SECRET'),
        'game_update_action': getattr(settings, 'GAME_UPDATE_ACTION'),
        'game_start_action': getattr(settings, 'GAME_START_ACTION'),
        'player_loses_action': getattr(settings, 'PLAYER_LOSES_ACTION')
    }
    return context