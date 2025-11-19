# Maybe a question/answers page is repeated in the project so I created this mixin to avoid repetitions of logic.
import random

class CorrectAnswerMixin:
    template_name = 'application/question_detail.html'
    # I prefer to use id over pk, its just a matter of taste.
    pk_url_kwarg = 'id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_question()
        question_answers = list(question.answers.select_related('answer'))
        if question_answers:
            if self.request.method == 'GET':
                random.shuffle(question_answers)
                context['question_answers'] = question_answers
                context.update(self.question_answers_order_map(question_answers))
            elif self.request.method == 'POST' and self.request.POST.get('answers_order'):
                posted_answers = self.request.POST['answers_order'].split(',')
                context.update(self.reorder_posted_answers(posted_answers, question_answers))
        context['question'] = question
        return context
    
    # The purpose of this function is to keep the same order in answers when user keeps reposting answers (it's a bit akward to change the order in every try)
    @staticmethod
    def question_answers_order_map(question_answers):
            return {'answers_order': [q_a.answer.id for q_a in question_answers]}
    
    # This is used to reorder the questions based on what the form posted
    @staticmethod
    def reorder_posted_answers(posted_answers, question_answers):
        sorted_answers = []
        if posted_answers:
            sorted_answers = [obj for id in posted_answers for obj in question_answers if str(obj.answer.id)==id]
        return {'answers_order': posted_answers, 'question_answers': sorted_answers}
    
    def answer_is_correct(self, *args, **kwargs):
        question = self.get_question()
        selected_answer_id = self.request.POST.get('answer')
        return self.validate_answer(question, selected_answer_id)
    
    # None: no answer provided, False: provided answer is wrong, True: provided answer is correct
    @staticmethod
    def validate_answer(question, answer_id=None):
        correct_answer_id = question.answers.get(is_correct=True).answer.id
        if not answer_id:
            return None
        if str(correct_answer_id) != str(answer_id):
            return False
        return True
