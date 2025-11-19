from django.test import TestCase
from project.application.models import Question, Category, Answer, QuestionAnswer
from project.application.helpers import hash_text
from project.application.mixins import CorrectAnswerMixin
from django.db.utils import IntegrityError

class QuestionModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c1, _ = Category.objects.get_or_create(name='Maths', hash=hash_text('Maths'))
        cls.q1, _ = Question.objects.get_or_create(
            text='What is 1+1?', defaults = dict(
                category=cls.c1,
                difficulty='easy',
                type='multiple',
                hash=hash_text('What is 1+1?')
            )
        )
        cls.a1, _ = Answer.objects.get_or_create(text='1', hash=hash_text('1'))
        cls.a2, _ = Answer.objects.get_or_create(text='2', hash=hash_text('2'))
        cls.a3, _ = Answer.objects.get_or_create(text='3', hash=hash_text('3'))
        cls.a4, _ = Answer.objects.get_or_create(text='4', hash=hash_text('4'))

        QuestionAnswer.objects.get_or_create(question=cls.q1, answer=cls.a1, is_correct=False)
        QuestionAnswer.objects.get_or_create(question=cls.q1, answer=cls.a2, is_correct=True)
        QuestionAnswer.objects.get_or_create(question=cls.q1, answer=cls.a3, is_correct=False)
        QuestionAnswer.objects.get_or_create(question=cls.q1, answer=cls.a4, is_correct=False)
        
    def test_duplicate_question(self):
        with self.assertRaises(IntegrityError):
            Question.objects.create(text='What is 1+1?', hash=hash_text('What is 1+1?'))
        
    def test_duplicate_answer(self):
        with self.assertRaises(IntegrityError):
            Answer.objects.create(text='1', hash=hash_text('1'))
        
    def test_correct_answer(self):
        self.assertFalse(CorrectAnswerMixin.validate_answer(self.q1, self.a1.id))
        self.assertTrue(CorrectAnswerMixin.validate_answer(self.q1, self.a2.id))
        
        




