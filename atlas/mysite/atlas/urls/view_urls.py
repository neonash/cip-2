"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url,include
from atlas import views
from atlas.forms import LoginForm
from atlas.forms import PasswordResetForm
from django.contrib.auth import views as vi

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.home, name='home'),
    url(r'^search/$', views.index, name='index'),
    url(r'^requests/$', views.requests, name='requests'),
    url(r'^sentiment/$', views.sentiment, name='sentiment'),
    url(r'^trigdriv/$', views.trigdriv, name='trigdriv'),
    url(r'^upload/$', views.upload, name='upload'),
    url(r'^summary/$', views.summary, name='summary'),
    url(r'^analysis/$', views.analysis, name='analysis'),
    url(r'^topicmodeling/$', views.topicmodeling, name='topicmodeling'),
    url(r'^clustering/$', views.clustering, name='clustering'),
    url(r'^compare/$', views.comparison, name='comparison'),

    #Login module views
    url(r'^login/$', vi.login, {'template_name': 'registration/login.html', 'authentication_form': LoginForm},
        name='login'),
    # url(r'^logout/$', views.logout_view, {'next_page': '/login'}),

    url(r'^password_reset/$', views.password_reset, name='password_reset_form'),
    url(r'^password_reset/done/$', views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        vi.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', vi.password_reset_complete, name='password_reset_complete'),

    url(r'^signup/$', views.signup, name='signup'),

]
