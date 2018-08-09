from __future__ import unicode_literals
from django.conf.urls import url
from . import views
from lense.views import AviatorMetric, LenseServer

app_name = 'lense'

urlpatterns = [
    url(r'^$', AviatorMetric.as_view(), name='AviatorList'),
    url(r'^update/$', LenseServer.as_view(), name='updateAviator')
]