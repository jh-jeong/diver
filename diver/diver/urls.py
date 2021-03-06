"""diver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from diver import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.main, name='main'),
    url(r'^upload/$', views.upload),
    url(r'^upload_item/$', views.upload_item),
    url(r'^search/$', views.search),
    url(r'^auth/$', views.auth),
    url(r'^like/([0-9]+)$',views.like),
    url(r'^match_like/([0-9]+)/([0-9]+)$',views.match_like),
    url(r'^account/$', views.account),
    url(r'^hanger/$', views.hanger),
    url(r'^update_hanger/$', views.update_hanger, name="update_hanger"),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url('', include('django.contrib.auth.urls', namespace='auth')),
]
