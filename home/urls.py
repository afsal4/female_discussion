from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login, name="login"),
    path("signup/", views.signup, name="signup"),
    path("home/", views.home, name="home"),
    path("discussion/", views.discussion, name="discussion"),
    path("add_discussion/", views.add_discussion, name="add_discussion"),
    path("add_question/", views.add_question, name="add_question"),
    path("search_question/", views.search_question, name="search_question"),
    path("question_post/", views.question_post, name="question_post"),
    path("logout/", views.logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("articles/", views.articles, name="articles"),
    path("chat/", views.chat, name="chat"),
    path("chat_bot/", views.chat_bot, name="chat_bot"),
    path("remove_discussion/", views.remove_discussion, name="remove_discussion"),
]
