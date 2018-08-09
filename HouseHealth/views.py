# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.views import APIView
from rest_framework.response import Response
from serializers import HouseSerializer, ConfigurationSerializer, \
    LongDisconnectSerializer
from models import House, Configs, LongDisconnect, Restart, QuickInterrupt
from view_utils import handle_UpdateRestarts, handle_UpdateQInterrupts, handle_UpdateHouse, handle_UpdateLongCutoff, \
    handle_UpdateAviatorDisconnections, get_AstroRestarts, get_Quick_Interrupts, handle_UpdateAll, handle_GenerateReport
from django.shortcuts import render
from rest_framework import status
from DyfoHouseHealth import DyfoHouseHealth
from constants import LAST_UPDATED
from utils import get_start_time, getConfigValue, get_astro_states, authorization
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import Http404

import logging

logger = logging.getLogger('__name__')


# **********************Only For Direct Api Calls*****************************

class UpdateRestartsFromGraylogView(APIView):
    """
    Update Restarts through Api Call
    """

    def put(self, request):
        house_id = request.GET.get('house_id', 'all')
        duration = request.GET.get('duration', '')
        data = DyfoHouseHealth(house_id).checkAstroRestarts(int(duration))
        data = handle_UpdateRestarts(data)
        return Response(data)


class UpdateQInterruptsFromGraylogView(APIView):
    """
    Update Quick Interrupts through Api Call
    """

    def put(self, request):
        house_id = request.GET.get('house_id', 'all')
        duration = request.GET.get('duration', '')
        data = DyfoHouseHealth(house_id).checkQuickInterrupt(duration)
        data = handle_UpdateQInterrupts(data, house_id)
        return Response({"success": "success"})


class UpdateHouse(APIView):
    """
    Updates  All Houses through Api Call
    """

    def put(self, request):
        data = handle_UpdateHouse()
        return Response(data)


class UpdateLongCutoff(APIView):
    """
    Updates  Long Disconnects through Api Call
    """

    def put(self, request):
        house_id = request.GET.get('house_id', 'all')
        data = DyfoHouseHealth(house_id).checkLongDisconnect()

        data = handle_UpdateLongCutoff(data, house_id)
        return Response(data)


class UpdateAviator(APIView):
    """
    Updates Aviator Disconnections through Api Call
    """

    def put(self, request):
        house_id = request.GET.get('house_id', 'all')
        duration = request.GET.get('duration', '')
        data = DyfoHouseHealth(house_id).checkAviatorDisconnection(duration)
        data = handle_UpdateAviatorDisconnections(data)
        return Response(data)


# ***********************************************************************************

class UpdateAll(APIView):
    """
    Updates all Houses, when called via celery or Update button
    """

    def get(self, request):
        try:
            handle_UpdateAll()
            return Response({"Success": "Success"}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Exception in Updating data. Exception " + str(e))
            return Response({"Error": "Error"}, status=status.HTTP_400_BAD_REQUEST)


class AstroRestartsLocalDbView(APIView):
    """
    Returns restarts of house based on interval defined in DB
    """

    def get(self, request, house_id):
        data = get_AstroRestarts()
        return Response(data)


class QuickInterruptsLocalDbView(APIView):
    """
    Returns Quick Interrupts of house based on interval defined in DB
    """

    def get(self, request, house_id):
        data = get_Quick_Interrupts(house_id)
        return Response(data)


@login_required
def homePageView(request):
    """
    Renders Home Page
    """
    try:
        data = handle_UpdateHouse()
        hs = HouseSerializer(House.objects.filter(to_update=True), many=True)
        attributes = ["#", "House ID", "House Name", "Status", "Restarts", "Quick Interrupts", "Long Disconnect"]

        last_updated = getConfigValue(LAST_UPDATED)

        return render(request, template_name='HouseHealth/layouts.html', context={"house_data": hs.data,
                                                                                  "attributes": attributes,
                                                                                  "last_updated": last_updated})
    except Exception as e:
        print(str(e))
        raise Http404("Error")
        # return render(request, template_name='HouseHealth/layouts.html', context={"house_data": hs.data,
        # "attributes": attributes,
        # "last_updated": last_updated})


@method_decorator(login_required, name='get')
class ConfigsView(APIView):
    """
    Renders Configuration
    """

    def get(self, request):
        cs = ConfigurationSerializer(Configs.objects.all(), many=True)
        return render(request, template_name='HouseHealth/configurations.html', context={"config_data": cs.data})

    def post(self, request):
        for key, value in request.data.iteritems():
            if key == 'csrfmiddlewaretoken':
                continue
            c = Configs.objects.get(key=key)
            c.value = value
            c.save()
        return self.get(request)


@method_decorator(login_required, name='get')
class RestartView(APIView):
    def get(self, request, house_id):
        time = get_start_time()
        restarts = get_AstroRestarts(house_id)
        aviator_disconnections = []
        # AviatorDisconnection.objects.filter(house_id=house_id, time_from__gt=time)
        return render(request, template_name='HouseHealth/restarts.html',
                      context={'restarts': restarts,
                               'house_id': house_id,
                               'aviator_disconnections': aviator_disconnections})


@method_decorator(login_required, name='get')
class QuickInterruptView(APIView):
    def get(self, request, house_id):
        qis = get_Quick_Interrupts(house_id)
        return render(request, template_name='HouseHealth/quick_interrupts.html',
                      context={'q_interrupts': qis,
                               'house_id': house_id})


@method_decorator(login_required, name='get')
class LongDisconnectView(APIView):
    """
    Renders Page with only those Long Disconnects which are still Inactive.
    """

    def get(self, request, house_id):
        long_disconnect = LongDisconnectSerializer(
            LongDisconnect.objects.filter(status='INACTIVE', house_id=house_id).order_by('-disconnected_at'),
            many=True)

        return render(request, template_name='HouseHealth/long_disconnect.html',
                      context={'long_disconnect': long_disconnect.data,
                               'house_id': house_id})


class GenerateReport(APIView):

    def get(self, request):
        house_id = request.GET['house_id']

        return handle_GenerateReport(house_id)


class HouseAstroState(APIView):

    def get(self, request):
        states_from_drona = get_astro_states()
        hs = HouseSerializer(House.objects.all(), many=True)
        return render(request, template_name='HouseHealth/house_astro_state.html', context={"houses": hs.data,
                                                                                            "states": states_from_drona})

    def post(self, request):
        for key, value in request.data.iteritems():

            if key == 'csrfmiddlewaretoken':
                continue
            id, action = key.split('_')

            # print(id,action)
            c = House.objects.get(house_id=id)
            if action == "astrostate":
                c.astro_state = value
            else:

                if value == "True":
                    c.to_update = True
                else:
                    c.to_update = False
            c.save()
        return self.get(request)


class DeleteHouseData(APIView):
    def post(self, request):
        house_id = request.data["house_id"]
        Restart.objects.filter(house_id=house_id).delete()
        QuickInterrupt.objects.filter(house_id=house_id).delete()
        LongDisconnect.objects.filter(house_id=house_id).delete()
        return Response({"Success": "Success"})


def checkAuth(request):
    if str(request.user) == 'Telescope':
        return redirect('home')

    try:
        res = int(authorization(request.user.email))
        if res == 0:
            logout(request)
            return render(request, template_name="unauthorised_user.html")
        else:
            return redirect('home')
    except:
        return render(request, template_name="auth_server_unavailable.html")


class DeleteUser(APIView):
    def get(self, request):
        email = request.GET["email"]
        try:
            User.objects.get(email=email).delete()
            return Response(status=status.HTTP_200_OK)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
