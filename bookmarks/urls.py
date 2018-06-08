from django.urls import path

from .views import main_page, user_page, bookmark_save_page, tag_page, tag_cloud_page


urlpatterns = [
    path('', main_page),
    path('save/', bookmark_save_page),
    path('tags/', tag_cloud_page),
    path('tag/<slug:tag_name>/', tag_page),
    path('user/<str:username>/', user_page)
]
