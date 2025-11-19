from django.db import models

# I decided to keep the Question and Answer models completely separated to each other. Nothing indicates \
# that an answer can not belong to many questions. This reduces the writes in db.'

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    hash = models.CharField(max_length=64, unique=True, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    TYPE_CHOICES = [
        ('multiple', 'Multiple selection'),
        ('boolean', 'True/False')
    ]

    text = models.TextField(unique=True)
    hash = models.CharField(max_length=64, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)
    type = models.CharField(max_length=70, choices=TYPE_CHOICES)

    def __str__(self):
        return self.text
    
    def display_category(self):
        return self.category.name
    
    def display_difficulty(self):
        return 'Difficulty: {}'.format(dict(self.DIFFICULTY_CHOICES).get(self.difficulty, ''))
    
    def display_type(self):
        return 'Type: {}'.format(dict(self.TYPE_CHOICES).get(self.type, ''))

class Answer(models.Model):
    text = models.CharField(max_length=255, unique=True)
    hash = models.CharField(max_length=64, unique=True, blank=True)

    def __str__(self):
        return self.text

class QuestionAnswer(models.Model):
    question = models.ForeignKey('application.Question', on_delete=models.CASCADE, related_name='answers')
    answer = models.ForeignKey('application.Answer', on_delete=models.CASCADE, related_name='questions')
    is_correct = models.BooleanField(default=False)
    display_order = models.IntegerField(default=0) # This field is not used currently, I randomize the order of
    # questions in page, but could be used for different orderings in answers. 

    class Meta:
        unique_together = ('question', 'answer')  
        indexes = [
            models.Index(fields=['question']),
            models.Index(fields=['answer']),
        ]  
        ordering = ['display_order']
