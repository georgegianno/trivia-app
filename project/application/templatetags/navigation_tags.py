from django import template

register = template.Library()

# A simple templatetag
@register.simple_tag
def get_play_game_button(request):
    from project.game.helpers import can_play_game
    data = {}
    if can_play_game(request.session.session_key):
        data['button_text'] = 'Squiz Game'
    return data