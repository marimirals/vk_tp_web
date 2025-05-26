import os
import gc
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike
import random
from tqdm import tqdm
from django.db import transaction, connection

class Command(BaseCommand):
    help = 'Simple database filler with guaranteed uniqueness'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Base fill ratio')
        parser.add_argument('--no-progress', action='store_true', help='Disable progress bars')

    def memory_safe(self, objects, model_class, batch_size=200, desc=""):
        if not self.progress:
            for i in range(0, len(objects), batch_size):
                model_class.objects.bulk_create(objects[i:i + batch_size])
                gc.collect()
        else:
            for i in tqdm(range(0, len(objects), batch_size), desc=desc):
                model_class.objects.bulk_create(objects[i:i + batch_size])
                gc.collect()

    def handle(self, *args, **options):
        self.progress = not options['no_progress']
        ratio = options['ratio']
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET work_mem TO '32MB';")
                cursor.execute("SET maintenance_work_mem TO '128MB';")

            with transaction.atomic():
                # 1. Пользователи (гарантируем уникальность)
                last_user_id = User.objects.last().id if User.objects.exists() else 0
                users = [
                    User(
                        username=f"user_{last_user_id + i + 1}",
                        email=f"user_{last_user_id + i + 1}@example.com",
                        password='testpass123'
                    )
                    for i in range(ratio)
                ]
                self.memory_safe(users, User, 200, "Creating Users")

                # 2. Профили (только для новых пользователей)
                new_users = User.objects.order_by('-id')[:ratio]
                profiles = [Profile(user=user) for user in new_users]
                self.memory_safe(profiles, Profile, 200, "Creating Profiles")

                # 3. Теги (гарантируем уникальность)
                last_tag_id = Tag.objects.last().id if Tag.objects.exists() else 0
                tags = [Tag(name=f"tag_{last_tag_id + i + 1}") for i in range(ratio)]
                self.memory_safe(tags, Tag, 200, "Creating Tags")

                # 4. Вопросы
                user_ids = list(User.objects.values_list('id', flat=True))
                questions = [
                    Question(
                        author_id=random.choice(user_ids),
                        title=f"Question {i}",
                        text=f"Text for question {i}",
                        rating=random.randint(0, 100)
                    )
                    for i in range(ratio * 10)
                ]
                self.memory_safe(questions, Question, 200, "Creating Questions")

                # 5. Ответы
                question_ids = list(Question.objects.values_list('id', flat=True))
                answers = [
                    Answer(
                        author_id=random.choice(user_ids),
                        question_id=random.choice(question_ids),
                        text=f"Answer {i}",
                        rating=random.randint(0, 50)
                    )
                    for i in range(ratio * 100)
                ]
                self.memory_safe(answers, Answer, 200, "Creating Answers")

                # 6. Лайки (с проверкой уникальности)
                answer_ids = list(Answer.objects.values_list('id', flat=True))
                
                # Лайки вопросов
                q_likes = []
                existing_pairs = set(QuestionLike.objects.values_list('user_id', 'question_id'))
                for _ in range(ratio * 100):
                    user_id = random.choice(user_ids)
                    question_id = random.choice(question_ids)
                    if (user_id, question_id) not in existing_pairs:
                        q_likes.append(QuestionLike(user_id=user_id, question_id=question_id))
                        existing_pairs.add((user_id, question_id))
                self.memory_safe(q_likes, QuestionLike, 200, "Question Likes")

                # Лайки ответов
                a_likes = []
                existing_pairs = set(AnswerLike.objects.values_list('user_id', 'answer_id'))
                for _ in range(ratio * 100):
                    user_id = random.choice(user_ids)
                    answer_id = random.choice(answer_ids)
                    if (user_id, answer_id) not in existing_pairs:
                        a_likes.append(AnswerLike(user_id=user_id, answer_id=answer_id))
                        existing_pairs.add((user_id, answer_id))
                self.memory_safe(a_likes, AnswerLike, 200, "Answer Likes")

        finally:
            with connection.cursor() as cursor:
                cursor.execute("RESET work_mem;")
                cursor.execute("RESET maintenance_work_mem;")

            self.stdout.write(self.style.SUCCESS(
                f'Successfully created: \n'
                f'- Users: {ratio}\n'
                f'- Questions: {ratio*10}\n'
                f'- Answers: {ratio*100}\n'
                f'- Likes: {ratio*200}'
            ))