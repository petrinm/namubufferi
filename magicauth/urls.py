from django.conf.urls import url

from magicauth import views

urlpatterns = [
    url(r'^magic/$', views.magic_auth),
    url(r'^magic/(?P<magic_token>.*)/$', views.magic_auth, name="magic"),
]
