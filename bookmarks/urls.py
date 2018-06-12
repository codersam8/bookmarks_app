from django.urls import path

from .views import (ajax_tag_autocomplete,
                    main_page, search_page,
                    user_page,
                    bookmark_save_page,
                    bookmark_vote_page,
                    popular_page,
                    tag_page, tag_cloud_page)


urlpatterns = [
    path('', main_page),
    path('ajax/tag/autocomplete/', ajax_tag_autocomplete),
    path('popular/', popular_page),
    path('save/', bookmark_save_page),
    path('search/', search_page),
    path('tags/', tag_cloud_page),
    path('tag/<slug:tag_name>/', tag_page),
    path('vote/', bookmark_vote_page),
    path('user/<str:username>/', user_page)
]
