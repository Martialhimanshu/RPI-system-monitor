"""Telescope URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.conf.urls import url
from views import AstroRestartsLocalDbView, QuickInterruptsLocalDbView, UpdateQInterruptsFromGraylogView, \
    UpdateRestartsFromGraylogView, homePageView, ConfigsView, RestartView, QuickInterruptView, UpdateHouse, UpdateAll, \
    UpdateLongCutoff, LongDisconnectView, UpdateAviator, GenerateReport, HouseAstroState, DeleteHouseData, checkAuth, DeleteUser

app_name = 'HouseHealth'

urlpatterns = [
    # url(r'^long_astro_disconnect/', LongDisconnect.as_view(),),
    # url(r'^aviator_disconnect/', AviatorDisconnect.as_view()),
    url(r'^astro_restarts_local_db/(?P<house_id>[a-zA-Z0-9\-]+)$', AstroRestartsLocalDbView.as_view()),
    url(r'^quick_interrupts_local_db/(?P<house_id>[a-zA-Z0-9\-]+)$', QuickInterruptsLocalDbView.as_view()),

    # url(r'^quick_interrupts/', QuickInterrupts_____.as_view()),
    # url(r'^long_wifi_disconnect/', WifiDisconnect.as_view()),
    # url(r'^update_house_health/', Health.as_view()),
    url(r'^update_restarts_graylog/', UpdateRestartsFromGraylogView.as_view()),
    url(r'^update_houses/', UpdateHouse.as_view()),
    url(r'^update_quickinterrupts_graylog/', UpdateQInterruptsFromGraylogView.as_view()),
    url(r'^houses/$', homePageView, name='get_house_template'),
    url(r'^configs/', ConfigsView.as_view(), name='get_configs_template'),
    url(r'^houses/restarts/(?P<house_id>[a-zA-Z0-9\-]+)$', RestartView.as_view(), name='get_house_restarts_template'),
    url(r'^houses/interrupts/(?P<house_id>[a-zA-Z0-9\-]+)$', QuickInterruptView.as_view(),
        name='get_house_interrupts_template'),
    url(r'^houses/long_disconnects/(?P<house_id>[a-zA-Z0-9\-]+)$', LongDisconnectView.as_view(),
        name='get_long_disconnects_template'),

    url(r'^update_all/$', UpdateAll.as_view()),
    url(r'^update_long_disconnect/$', UpdateLongCutoff.as_view()),
    url(r'^update_aviator_disconnect/$', UpdateAviator.as_view()),
    url(r'^generate_report/$', GenerateReport.as_view()),
    url(r'^house_astro_state/$', HouseAstroState.as_view(), name='house_astro_state'),
    url(r'^delete_house/$', DeleteHouseData.as_view(), name='delete_house_data'),
    url(r'^check_user/$', checkAuth, name='check_auth'),
    url(r'^delete_user/$',DeleteUser.as_view() , name='delete_user'),

]
