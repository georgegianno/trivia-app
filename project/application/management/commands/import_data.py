from django.core.management.base import BaseCommand
import time
import requests
from project.application.models import Question, Category, Answer, QuestionAnswer
from project.application.helpers import hash_text
import html
from django.db import transaction
from django.conf import settings

class Command(BaseCommand):
    # The notes below explain the thoughts behind this logic:
    help = " \
        1. This command should populate the Trivia api database in our db. We could go with the traditional \
        get_or_create() way, which is more memory efficient, but heavy on the db. I wanted to demonstrate what I can do \
        with the least possible queries (can it go even lower?), going heavier on memory. For the size of api database, \
        this should be super efficient. If database would be larger, maybe we should re-evaluate the memory vs db load \
        and decide. The objects are created in atomic transaction (we want to make sure everything in the \
        batch is inserted correctly, or nothing is inserted). There could be risks of not syncing the db before every write, because I rely on memory checks, \
        but this command was made for performance over anything else. \
        \
        2. The argument --session-key can be used to keep fetching with the same session token in case something happens \
        (i.e. connection issues). \
        \
        3. The uniqueness of the texts is ensured by unique hashes. Hashing the texts allows to map the objects relations \
        even before the ids are created, and it makes queries faster. The uniqueness of relations is ensured \
        via unique_together() in application.models.py. The human-readable texts are stored after escaping special characters. \
        \
        4. When the text of a model is changed, it is re-hashed via signals.py. No duplicates are allowed in terms of text.\
        This means that if update() is used on model records, the pre-computedhash should also be included in update(). \
        \
        5. I have intentionally not used try-except blocks, because if something goes wrong, we want to re-import the \
        data until everything is ok.\
        \
        6. I use the format() function a lot, (f"" is better is probably better but does not work in older python versions)."
    
    def add_arguments(self, parser):
        parser.add_argument(
        '--session-key',
        type=str,
        help='Check record counts of each model'
        )
    
    def handle(self, *args, **options):
        self.session_token = None
        self.num_questions_per_request = getattr(settings, 'NUMBER_OF_QUESTIONS_FETCHED', 50)
        self.session_token_url = 'https://opentdb.com/api_token.php?command=request'
        self.api_search_url = 'https://opentdb.com/api.php?amount={}'.format(self.num_questions_per_request)
        self.decide_token(**options)
        self.construct_object_maps()
        self.trivia_import_data()
   
    def display_response_message(self, data):
        response_message = data.get('response_message')
        if response_message:
            self.stdout.write(response_message)
    
    def get_response_data(self, response):
        if response.status_code == 200:
            data = response.json()
            self.display_response_message(data)
            response_code = data.get('response_code')
            if response_code == 0:
                return data
            if response_code == 5:
                return {'exit_loop': True}
            if response_code == 5:
                return {'reached_rate_limit': True}
            self.stdout.write('No results, with response code: {}'.format(response_code))
        elif response.status_code == 529:
            return {'reached_rate_limit': True}
        self.stdout.write('Exception with code: {}'.format(response.status_code))
        return {}
        
    def decide_token(self, **options):
        if options['session_key']:
            self.session_token = options['session_key']
        else:
            self.trivia_get_token()
        
    def trivia_get_token(self):
        url = self.session_token_url
        response = requests.get(url)
        data = self.get_response_data(response)
        token = data.get('token')
        if token:
            self.session_token = token
    
    def update_category_map(self):
        self.category_map = {item['hash']: item['id'] for item in list(Category.objects.values('hash', 'id'))}
        
    def update_question_map(self):
        self.question_map = {item['hash']: item['id'] for item in list(Question.objects.values('hash', 'id'))}
        
    def update_answer_map(self):
        self.answer_map = {item['hash']: item['id'] for item in list(Answer.objects.values('hash', 'id'))}

    def update_question_answer_maps(self):
        self.question_map = {}
        self.answer_map  = {}
        self.question_answer_map = {}
        for item in list(QuestionAnswer.objects.values('question__id', 'question__hash', 'answer__hash', 'answer__id')):
            answer_hash = item['answer__hash']
            question_hash = item['question__hash']
            self.question_map[question_hash] = item['question__id']
            self.answer_map[answer_hash] = item['answer__id']
            self.question_answer_map[question_hash] = answer_hash
        
    def construct_object_maps(self):
        self.update_category_map()
        self.update_question_map()
        self.update_answer_map()
        self.update_question_answer_maps()
    
    @staticmethod
    def base_answer_create_kwargs(question_hash, answer_hash, is_correct=False):
        return {'question_hash': question_hash, 'answer_hash': answer_hash, 'is_correct': is_correct} 
    
    def create_categories_and_questions(self, data):
         
        categories_to_create = []
        uncreated_categories = []
        questions_to_create = []
        uncreated_questions = []
        for item in data:
            question_text = html.unescape(item['question'])
            question_hash = hash_text(question_text)
            category_name = html.unescape(item['category'])
            category_hash = hash_text(category_name)
            if not category_hash in self.category_map and not category_hash in uncreated_categories:
                categories_to_create.append(Category(name=category_name, hash=category_hash))
                uncreated_categories.append(category_hash)
            if not question_hash in self.question_map and not question_hash in uncreated_questions:
                question_create_kwargs = dict(
                    text = question_text,
                    hash=question_hash,
                    type = html.unescape(item['type']),
                    difficulty= html.unescape(item['difficulty']),
                )
                questions_to_create.append({
                    category_hash: Question(**question_create_kwargs), 
                })
                uncreated_questions.append(question_hash)
                
        Category.objects.bulk_create(categories_to_create, ignore_conflicts=True)
        self.update_category_map()

        for item in questions_to_create:
            for category_hash, object in item.items():
                object.category_id = self.category_map[category_hash]
        Question.objects.bulk_create([object for item in questions_to_create
            for object in item.values()], ignore_conflicts=True)
        
        self.update_question_map()
        
    def create_question_answers(self, data):
        uncreated_answers = []
        question_answers_to_create = []
        answer_questions_values = []
        for item in data:
            question_text = html.unescape(item['question'])
            question_hash = hash_text(question_text)
            correct_answer = html.unescape(item['correct_answer'])
            correct_hash = hash_text(correct_answer)
            incorrect_hashes_map = {hash_text(answer): html.unescape(answer) for answer in item['incorrect_answers']}
            correct_answer_map = self.base_answer_create_kwargs(question_hash, correct_hash, True)
            if not correct_hash in self.answer_map and not correct_hash in uncreated_answers:
                correct_answer_map.update({
                    'answer': Answer(text=correct_answer, hash=correct_hash)
                })
                uncreated_answers.append(correct_hash)
            answer_questions_values.append(correct_answer_map)
            for incorrect_hash, incorrect_answer in incorrect_hashes_map.items():
                incorrect_answer_map = self.base_answer_create_kwargs(question_hash, incorrect_hash, False)
                if not incorrect_hash in self.answer_map and not incorrect_hash in uncreated_answers:
                    incorrect_answer_map.update({
                        'answer': Answer(text=incorrect_answer, hash=incorrect_hash)
                    })
                    uncreated_answers.append(incorrect_hash) 
                answer_questions_values.append(incorrect_answer_map)
        Answer.objects.bulk_create([item['answer'] for item in answer_questions_values \
            if item.get('answer')], ignore_conflicts=True) 
        
        self.update_answer_map()
    
        for item in answer_questions_values:
            question_answers_to_create.append(
                QuestionAnswer(**{
                    'question_id': self.question_map[item['question_hash']],
                    'answer_id': self.answer_map[item['answer_hash']],
                    'is_correct': item['is_correct']
                })
            )
        
        QuestionAnswer.objects.bulk_create(question_answers_to_create, ignore_conflicts=True)  
    
    def trivia_import_data(self):
        if not self.session_token:
            self.stdout.write('No session token found.')
            return
        while True:
            self.stdout.write('Fetching {} questions with session token {}'.format(
                self.num_questions_per_request, self.session_token
            ))
            response = requests.get('{}&token={}'.format(self.api_search_url, self.session_token))
            data = self.get_response_data(response)
            self.display_response_message(data)
            if data.get('reached_rate_limit'):
                self.stdout.write('Hit rate limit, retrying in 5s.')
                time.sleep(5)
                continue
            if not data:
                self.stdout.write('No data, response code: {}'.format(response.status_code))
                break
            results = data.get('results')
            if not results:
                if data.get('exit_loop'):
                    self.stdout.write('No more results.')
                    break
            with transaction.atomic():
                self.create_categories_and_questions(results)
                self.create_question_answers(results)
                self.stdout.write('Latest batch successfully created in db')
            time.sleep(5)
            
                