from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class QuestionManager(models.Manager):
    def new(self):
        """Сортировка по дате создания (новые первые)"""
        return self.order_by('-created_at')

    def best(self):
        """Сортировка по рейтингу (лучшие первые)"""
        return self.order_by('-rating')

    def by_tag(self, tag_name):
        """Вопросы по тегу"""
        return self.filter(tags__name=tag_name)

    def with_details(self):
        """Оптимизированный запрос с подгрузкой связанных данных"""
        return self.select_related('author').prefetch_related('tags', 'answers')

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)  # для примера рейтинга
    tags = models.ManyToManyField(Tag, blank=True)

    objects = QuestionManager()

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        """URL вопроса (вместо hardcoding в шаблонах)"""
        return reverse('question', kwargs={'question_id': self.id})

    def answers_count(self):
        """Количество ответов"""
        return self.answers.count()

    def tags_list(self):
        """Список тегов для шаблона"""
        return list(self.tags.values_list('name', flat=True))
    
    def is_liked_by(self, user):
        """Проверяет, лайкнул ли пользователь вопрос"""
        if not user.is_authenticated:
            return False
        return self.questionlike_set.filter(user=user).exists()


class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f"Answer to {self.question.title} by {self.author.username}"
    
    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.answerlike_set.filter(user=user).exists()


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'question')


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'answer')
