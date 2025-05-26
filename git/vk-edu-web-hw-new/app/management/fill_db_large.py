import os
import gc
import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
from django.db import transaction

class Command(BaseCommand):
    help = 'Safe large data filler with unique checks'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Base ratio')
        parser.add_argument('--skip-likes', action='store_true', help='Skip likes creation')

    def handle(self, *args, **options):
        ratio = options['ratio']
        total_questions = ratio * 10
        total_answers = ratio * 100
        
        with transaction.atomic():
            # 1. Создание пользователей
            self.stdout.write(f"Creating {ratio} users...")
            for i in range(ratio):
                User.objects.get_or_create(
                    username=f'user_{i}',
                    defaults={'email': f'user_{i}@example.com', 'password': 'testpass123'}
                )
            
            # 2. Профили
            self.stdout.write("Creating profiles...")
            for user in User.objects.all():
                Profile.objects.get_or_create(user=user)
            
            # 3. Теги
            self.stdout.write(f"Creating {ratio} tags...")
            for i in range(ratio):
                Tag.objects.get_or_create(name=f'tag_{i}')
            
            # 4. Вопросы
            self.stdout.write(f"Creating {total_questions} questions...")
            users = list(User.objects.values_list('id', flat=True))
            for i in range(total_questions):
                Question.objects.get_or_create(
                    title=f'Question {i}',
                    defaults={
                        'author_id': random.choice(users),
                        'text': f'Text for question {i}',
                        'rating': random.randint(0, 100)
                    }
                )
            
            # 5. Ответы
            self.stdout.write(f"Creating {total_answers} answers...")
            questions = list(Question.objects.values_list('id', flat=True))
            for i in range(total_answers):
                Answer.objects.get_or_create(
                    question_id=random.choice(questions),
                    defaults={
                        'author_id': random.choice(users),
                        'text': f'Answer text {i}',
                        'rating': random.randint(0, 50)
                    }
                )
            
            if not options['skip_likes']:
                # 6. Лайки вопросов
                self.stdout.write("Creating question likes...")
                existing = set()
                for i in range(ratio * 100):
                    while True:
                        user_id = random.choice(users)
                        question_id = random.choice(questions)
                        if (user_id, question_id) not in existing:
                            QuestionLike.objects.get_or_create(
                                user_id=user_id,
                                question_id=question_id
                            )
                            existing.add((user_id, question_id))
                            break
                
                # 7. Лайки ответов
                self.stdout.write("Creating answer likes...")
                answers = list(Answer.objects.values_list('id', flat=True))
                existing = set()
                for i in range(ratio * 100):
                    while True:
                        user_id = random.choice(users)
                        answer_id = random.choice(answers)
                        if (user_id, answer_id) not in existing:
                            AnswerLike.objects.get_or_create(
                                user_id=user_id,
                                answer_id=answer_id
                            )
                            existing.add((user_id, answer_id))
                            break

        self.stdout.write(self.style.SUCCESS(f'Successfully created data for ratio {ratio}'))