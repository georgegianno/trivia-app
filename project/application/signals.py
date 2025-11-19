from django.db.models.signals import pre_save
from django.dispatch import receiver
from project.application.models import Answer, Question, Category
from project.application.helpers import hash_text

@receiver(pre_save, sender=Answer)
@receiver(pre_save, sender=Question)
def update_question_answers_hash(sender, instance, **kwargs):
    sender._default_manager.filter(id=instance.id).update(hash=hash_text(instance.text))
    
@receiver(pre_save, sender=Category)
def update_categories_hash(sender, instance, **kwargs):
    sender._default_manager.filter(id=instance.id).update(hash=hash_text(instance.name))