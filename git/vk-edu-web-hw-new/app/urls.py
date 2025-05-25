from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name="index"),
    path('hot', views.hot, name="hot"),
    path('question/<int:question_id>', views.question, name="question"),
    path('tag/<str:tag_name>/', views.tag, name='tag'),
    path('question/<int:question_id>/like/', views.like_question, name='like_question'),
    path('ask/', views.ask, name='ask'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
]