import hashlib
from django.apps import apps
import hashlib
import html
import unicodedata
import re

def hash_text(text):
    text = html.unescape(text)
    text = unicodedata.normalize('NFKC', text)
    text = text.strip()
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def count_model_records(app_names=set()):
    all_models = apps.get_models()
    check_apps = ['project.{}.models'.format(app_name) for app_name in app_names]
    models_map = dict()
    for model in all_models:
        if any([not check_apps, model.__module__ in check_apps]):
            models_map[model._meta.verbose_name_plural.capitalize()] = model
    for item in models_map.items():
        print('{}: {}'.format(item[0], item[1]._default_manager.count()))