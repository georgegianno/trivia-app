from django.test import TestCase, Client
from django.urls import reverse
from project.application.models import Question, Category, Answer, QuestionAnswer
from project.application.helpers import hash_text

class QuestionViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.category, _ = Category.objects.get_or_create(name='Maths', hash=hash_text('Maths'))
        cls.question, _ = Question.objects.get_or_create(
            text='What is 1+1?',
            defaults=dict(category=cls.category, difficulty='easy', type='multiple', hash=hash_text('What is 1+1?'))
        )
        cls.a1, _ = Answer.objects.get_or_create(text='1', hash=hash_text('1'))
        cls.a2, _ = Answer.objects.get_or_create(text='2', hash=hash_text('2'))
        cls.a3, _ = Answer.objects.get_or_create(text='3', hash=hash_text('3'))
        cls.a4, _ = Answer.objects.get_or_create(text='4', hash=hash_text('4'))

        QuestionAnswer.objects.get_or_create(question=cls.question, answer=cls.a1, is_correct=False)
        QuestionAnswer.objects.get_or_create(question=cls.question, answer=cls.a2, is_correct=True)
        QuestionAnswer.objects.get_or_create(question=cls.question, answer=cls.a3, is_correct=False)
        QuestionAnswer.objects.get_or_create(question=cls.question, answer=cls.a4, is_correct=False)

    def test_home_redirects_to_question_list(self):
        response = self.client.get(reverse('home'))
        self.assertRedirects(response, reverse('question-list'))

    def test_question_list_view_get(self):
        response = self.client.get(reverse('question-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application/question_list.html')
        self.assertIn('questions', response.context)
        self.assertIn('form', response.context)
        self.assertIn('num_total_results', response.context)
        self.assertEqual(response.context['num_total_results'], 1)

    def test_question_detail_get(self):
        url = reverse('question-detail', kwargs={'id': self.question.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'application/question_detail.html')
        self.assertEqual(response.context['question'], self.question)
        self.assertEqual(len(response.context['question_answers']), 4)
        answers_order_set = set(response.context['answers_order'])
        expected_set = {self.a1.id, self.a2.id, self.a3.id, self.a4.id}
        self.assertEqual(answers_order_set, expected_set)

    def test_question_detail_post_correct_answer(self):
        url = reverse('question-detail', kwargs={'id': self.question.id})
        response = self.client.post(url, {'answer': self.a2.id})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Correct answer" in m.message for m in messages))

    def test_question_detail_post_wrong_answer(self):
        url = reverse('question-detail', kwargs={'id': self.question.id})
        response = self.client.post(url, {'answer': self.a1.id})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Wrong answer" in m.message for m in messages))

    def test_question_detail_post_no_answer(self):
        url = reverse('question-detail', kwargs={'id': self.question.id})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertTrue(any("Please select an answer" in m.message for m in messages))
