from django.shortcuts import render, get_object_or_404
from copy import deepcopy
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .utils import paginate

QUESTIONS = [
    {
        'title': f'Title {i}',
        'id': i,
        'text': f'Text for question #{i}',
        'img_path': "img/ava.jpg",  
        'answers_count': 0, 
        'likes': 0,
        'tags': ['django', 'python'],
        'answers': [
        {'user': 'blablabla', 'text': 'text blablabla'},
        {'user': 'blebleble', 'text': 'text blebleble'},
        ]
    } for i in range(1, 31)  
]

answers = [
    {
        'user': {'username': 'john_doe', 'avatar': 'path_to_avatar'},  
        'text': 'This is an answer to the question.',
        'likes': 10,
    },
]


def get_all_tags():
    return {tag for question in QUESTIONS for tag in question['tags']}

def index(request):
    page_obj = paginate(QUESTIONS, request, per_page=10)
    return render(request, 'index.html', {'page_obj': page_obj})


def hot(request):
    hot_questions = sorted(deepcopy(QUESTIONS), key=lambda x: -x['id'])
    paginator = Paginator(hot_questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_tags = get_all_tags()
    return render(request, 'hot.html', {'page_obj': page_obj, 'all_tags': all_tags})

def question(request, question_id):
    question_obj = next((q for q in QUESTIONS if q['id'] == question_id), None)
    if question_obj is None:
        raise Http404("Question not found")
    
    answers = question_obj.get('answers', [])
    
    paginator = Paginator(answers, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    tags = question_obj.get('tags', []) 
    all_tags = get_all_tags() 
    
    if request.method == 'POST' and 'like_answer' in request.POST:
        answer_id = request.POST.get('answer_id')
        for answer in answers:
            if answer['id'] == answer_id:
                answer['likes'] += 1
                break
    
    return render(request, 'single_question.html', {
        'question': question_obj,
        'page_obj': page_obj,
        'tags': tags, 
        'all_tags': all_tags
    })


def tag(request, tag_name):
    tagged_questions = [q for q in QUESTIONS if tag_name in q['tags']]
    paginator = Paginator(tagged_questions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    all_tags = get_all_tags() 
    return render(request, 'tag.html', {
        'page_obj': page_obj,
        'tag_name': tag_name,
        'all_tags': all_tags,
        'selected_tag': tag_name,
    })

def like_question(request, question_id):
    if request.method == 'POST':
        liked_questions = request.session.get('liked_questions', [])

        for q in QUESTIONS:
            if q['id'] == question_id:
                if question_id in liked_questions:
                    q['likes'] -= 1
                    liked_questions.remove(question_id)
                else:
                    q['likes'] += 1
                    liked_questions.append(question_id)
                break

        request.session['liked_questions'] = liked_questions

    return redirect(request.META.get('HTTP_REFERER', 'index'))

def ask(request):
    all_tags = get_all_tags()
    return render(request, 'ask.html', {'all_tags': all_tags})

def signup_view(request):
    all_tags = get_all_tags() 
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form, 'all_tags': all_tags})

def login_view(request):
    all_tags = get_all_tags() 
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form, 'all_tags': all_tags})

def logout_view(request):
    logout(request)
    return redirect('index') 

@login_required
def settings_view(request):
    all_tags = get_all_tags()  # Получаем все теги
    return render(request, 'settings.html', {'all_tags': all_tags})