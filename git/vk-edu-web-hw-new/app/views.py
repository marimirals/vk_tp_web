from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Question, Answer, Tag, Profile, QuestionLike, AnswerLike
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileEditForm
from .utils import paginate

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

    context = {'page_obj': page_obj}
    context.update(get_sidebar_context())
    return render(request, 'index.html', context)


def hot(request):
    questions = Question.objects.with_details().order_by('-rating')
    page_obj = paginate(questions, request, per_page=10)

    for q in page_obj.object_list:
        q.is_liked = q.is_liked_by(request.user)

    context = {'page_obj': page_obj}
    context.update(get_sidebar_context())
    return render(request, 'hot.html', context)

@login_required
def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.with_details(), id=question_id)
    user = request.user

    if request.method == 'POST':
        if 'like_answer' in request.POST:
            answer_id = request.POST.get('answer_id')
            answer = get_object_or_404(Answer, id=answer_id)
            AnswerLike.objects.get_or_create(user=user, answer=answer)
            return redirect('question_detail', question_id=question_id)

        elif 'answer_text' in request.POST:
            text = request.POST.get('answer_text', '').strip()
            if text:
                answer = Answer.objects.create(
                    question=question,
                    text=text,
                    author=user,
                    is_correct=False
                )
                all_answers = question.answers.all().order_by('created_at')
                answer_index = list(all_answers).index(answer)
                page_number = answer_index // 5 + 1
                return redirect(f"{request.path}?page={page_number}#answer-{answer.id}")

    answers = question.answers.select_related('author').all().order_by('created_at')
    page_obj = paginate(answers, request, per_page=5)

    for answer in page_obj:
        answer.is_liked = answer.answerlike_set.filter(user=user).exists()

    context = {
        'question': question,
        'page_obj': page_obj,
    }
    context.update(get_sidebar_context())
    return render(request, 'single_question.html', context)

@login_required
def like_question(request, question_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    question = get_object_or_404(Question, id=question_id)
    like, created = QuestionLike.objects.get_or_create(user=request.user, question=question)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    likes_count = question.questionlike_set.count()
    return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})

@login_required
def like_answer(request, answer_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    answer = get_object_or_404(Answer, id=answer_id)
    like, created = AnswerLike.objects.get_or_create(user=request.user, answer=answer)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    likes_count = answer.answerlike_set.count()
    return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})

def tag(request, tag_name):
    questions = Question.objects.with_details().filter(tags__name=tag_name)
    page_obj = paginate(questions, request, per_page=10)

    for q in page_obj.object_list:
        q.is_liked = q.is_liked_by(request.user)

    context = {
        'page_obj': page_obj,
        'tag_name': tag_name
    }
    context.update(get_sidebar_context())
    return render(request, 'tag.html', context)

@login_required
def ask(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        text = request.POST.get('text', '').strip()
        tag_string = request.POST.get('tags', '').strip()

        tag_names = [t.strip() for t in tag_string.split(',') if t.strip()]

        if len(tag_names) > 5:
            context = {
                'error': 'You can add up to 5 tags only.',
                'title': title,
                'text': text,
                'tags': tag_string
            }
            context.update(get_sidebar_context())
            return render(request, 'ask.html', context)

        if title and text:
            question = Question.objects.create(title=title, text=text, author=request.user)
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)

            return redirect('question_detail', question_id=question.id)

        context = {
            'error': 'Title and text are required.',
            'title': title,
            'text': text,
            'tags': tag_string
        }
        context.update(get_sidebar_context())
        return render(request, 'ask.html', context)

    context = get_sidebar_context()
    return render(request, 'ask.html', context)

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
    else:
        form = CustomUserCreationForm()

    for field in form.fields.values():
        field.widget.attrs["class"] = "form-control"

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Profile.objects.create(user=user)
        login(request, user)
        return redirect('index')

    context = {'form': form}
    context.update(get_sidebar_context())
    return render(request, 'signup.html', context)

def login_view(request):
    redirect_to = request.GET.get('continue', request.POST.get('continue', reverse('index')))

    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                redirect_to = reverse('index')
            return redirect(redirect_to)
    else:
        form = CustomAuthenticationForm()

    context = {'form': form, 'continue': redirect_to}
    context.update(get_sidebar_context())
    return render(request, 'login.html', context)

@login_required
def logout_view(request):
    redirect_to = request.META.get('HTTP_REFERER', 'index')
    logout(request)
    if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
        redirect_to = reverse('index')
    return redirect(redirect_to)

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            context = {
                'form': ProfileEditForm(instance=user),
                'success': 'Profile updated successfully',
                **get_sidebar_context()
            }
            return render(request, 'settings.html', context)
        else:
            context = {'form': form}
            context.update(get_sidebar_context())
            return render(request, 'settings.html', context)

    form = ProfileEditForm(instance=user)
    context = {'form': form}
    context.update(get_sidebar_context())
    return render(request, 'settings.html', context)

@login_required
def mark_correct_answer(request, answer_id):
    if request.method == 'POST':
        answer = get_object_or_404(Answer, id=answer_id)
        if answer.question.author != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)

        Answer.objects.filter(question=answer.question, is_correct=True).update(is_correct=False)
        answer.is_correct = True
        answer.save()

        return JsonResponse({'success': True, 'is_correct': True})

    return JsonResponse({'error': 'Метод не разрешен'}, status=405)