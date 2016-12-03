from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm

from namubufferiapp import views

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^login', auth_views.login, {'template_name': 'namubufferiapp/base_login.html',
                                                       'extra_context': {'register_form': UserCreationForm()}}),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}),
    url(r'^register/$', views.register, name="register"),
    url(r'^buy/$', views.buy, name="buy"),
    url(r'^deposit/$', views.deposit, name="deposit"),
    url(r'^cancel/$', views.cancel_transaction, name="cancel"),
    url(r'^receipt/$', views.receipt, name="receipt"),
    url(r'^history/$', views.transaction_history, name="history"),
]
