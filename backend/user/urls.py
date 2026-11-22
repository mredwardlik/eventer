from django.urls import path

from user import views

urlpatterns = [
    path('register', views.RegisterUserView.as_view()),
    path('login', views.LoginUserView.as_view()),
    path('logout', views.LogoutUserView.as_view()),
    path('me', views.MeView.as_view()),
    path('editor', views.EditorSettingView.as_view()),
]
