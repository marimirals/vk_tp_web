from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import Http404
from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
from .utils import paginate
from django.db.models import Count

# Сайдбар: популярные теги и лучшие участники
def get_sidebar_context():
    return {
        'popular_tags': Tag.objects.annotate(num_questions=Count('question')).order_by('-num_questions')[:10],
        'best_members': Profile.objects.annotate(num_answers=Count('user__answer')).order_by('-num_answers')[:5]
    }

def index(request):
    questions = Question.objects.with_details().order_by('-created_at')
    page_obj = paginate(questions, request, per_page=10)

    for q in page_obj.object_list:
        q.is_liked = q.is_liked_by(request.user)

    context = {
        'page_obj': page_obj,
    }
    context.update(get_sidebar_context())
    return render(request, 'index.html', context)

def hot(request):
    questions = Question.objects.with_details().order_by('-rating')
    page_obj = paginate(questions, request, per_page=10)

    for q in page_obj.object_list:
        q.is_liked = q.is_liked_by(request.user)

    context = {
        'page_obj': page_obj,
    }
    context.update(get_sidebar_context())
    return render(request, 'hot.html', context)

def question(request, question_id):
    question = get_object_or_404(Question.objects.with_details(), id=question_id)
    answers = question.answers.all()
    page_obj = paginate(answers, request, per_page=5)

    if request.method == 'POST' and 'like_answer' in request.POST:
        answer_id = request.POST.get('answer_id')
        answer = get_object_or_404(Answer, id=answer_id)
        AnswerLike.objects.get_or_create(user=request.user, answer=answer)
        return redirect('question', question_id=question_id)

    context = {
        'question': question,
        'page_obj': page_obj,
    }
    context.update(get_sidebar_context())
    return render(request, 'single_question.html', context)

def tag(request, tag_name):
    questions = Question.objects.with_details().filter(tags__name=tag_name)
    page_obj = paginate(questions, request, per_page=10)

    context = {
        'page_obj': page_obj,
        'tag_name': tag_name
    }
    context.update(get_sidebar_context())
    return render(request, 'tag.html', context)

@login_required
def like_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question
    )
    if not created:
        like.delete()
    return redirect(request.META.get('HTTP_REFERER', 'index'))

@login_required
def ask(request):
    if request.method == 'POST':
        # Тут должна быть логика создания вопроса
        pass
    context = get_sidebar_context()
    return render(request, 'ask.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.create(user=user)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    context = {'form': form}
    context.update(get_sidebar_context())
    return render(request, 'signup.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    context = {'form': form}
    context.update(get_sidebar_context())
    return render(request, 'login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def settings_view(request):
    if request.method == 'POST':
        # Обновление профиля
        pass
    return render(request, 'settings.html', get_sidebar_context())
