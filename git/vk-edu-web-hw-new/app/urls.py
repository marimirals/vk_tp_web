from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name="index"),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('hot', views.hot, name="hot"),
    path('question/<int:question_id>', views.question_detail, name="question"),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('like/question/<int:question_id>/', views.like_question, name='like_question'),
    path('like/answer/<int:answer_id>/', views.like_answer, name='like_answer'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('answer/<int:answer_id>/mark-correct/', views.mark_correct_answer, name='mark_correct_answer'),
    path('ajax/update-avatar/', views.ajax_update_avatar, name='ajax_update_avatar'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

