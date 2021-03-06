
"""bookmarks_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os

from django.contrib import admin
from django.contrib.auth.views import login
from django.urls import include, path
from django.views.generic import TemplateView
from django.views.static import serve


from .views import logout_page, register_page

site_media = os.path.join(
    os.path.dirname(__file__), 'site_media'
)

urlpatterns = [
    path('bookmarks/', include('bookmarks.urls')),
    path('register/', register_page),
    path('register/success/',
         TemplateView.as_view(
             template_name='registration/register_success.html')),
    path('login/', login),
    path('logout/', logout_page),
    path('admin/', admin.site.urls),
    path('site_media/<str:path>', serve, {'document_root': site_media}),
]
