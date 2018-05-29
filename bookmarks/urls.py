from django.urls import path

from .views import main_page, user_page


urlpatterns = [
    path('', main_page),
    path('user/<str:username>/', user_page)
]
