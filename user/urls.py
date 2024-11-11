from django.urls import path
from .views import RegisterView, LoginView, UserView, LogOutView,update_user, delete_user


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', UserView.as_view(), name='user'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('user/update/', update_user, name='update_user'),
    path('user/delete/', delete_user, name='delete_user'),

]