from __future__ import unicode_literals
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from serializers import AviatorConfigurationserializer
from lense.models import *
from django.views import generic
from utils import *
import time
from HouseHealth import urls
import logging
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

logger = logging.getLogger('__name__')
# # Create your views here.
# class UpdateClient(APIView):
#     """Update aviator client metrics to lense server"""
#     def post(self, request):
#         sys_up = request.data['uptime']
#         memory = request.data['memory']
#         cpu = request.data['CPU']
#         process = request.data['process']
#         usb = request.data['USB']
#         houseId = request.data['houseId']
#         pi_id = request.data['pi']
#         h_name = request.data['name']
#         """Object created for every models"""
#         memory_obj = Memory.objects.create(avail=memory['available'], total=memory['total'], usage_per=memory['percent_used'])
#         memory_obj.save()
#         process_obj = Process.objects.create(active=process['active'], greater_than_memory=process['gt_memory'], top_cpu=process['top_cpu'], top_memory=process['top_memory'])
#         process_obj.save()
#         metric_obj = Metric.objects.create(uptime=sys_up, cpu=cpu, usb=usb, memory=memory_obj, process=process_obj)
#         metric_obj.save()
#         aviator_obj = Aviator.objects.create(pi_id=pi_id,metric=metric_obj, is_active=time.time())
#         aviator_obj.save()
#         house = House.objects.get_or_create(id(houseId), name = h_name, aviator=aviator_obj)
#         house.save()
#         data = [memory,cpu,usb]
#         if checkAlertThreshold(memory,cpu,usb):
#             generate_alert(data)
#         return Response(status=status.HTTP_200_OK)

class AviatorMetric(generic.ListView):
    template_name = 'lense/index.html'
    context_object_name = 'latest_aviator_list'

    def get_queryset(self):
        """Returns list of aviator metrics order by houseId"""
        return Aviator.objects.order_by('-memory','-cpu_use')[:5]


@method_decorator(login_required, name='get')
class ConfigsView(APIView):
    def get(self, request, houseId):
        AConf = AviatorConfigurationserializer(AviatorConfiguration.objects.get(aviator__houseId=houseId), many=True)
        return render(request, template_name='lense/Aviatorconf.html', context={"config_list":AConf})

    def post(self, request, aviator_id):
        for key, value in request.data.iteritems():
            if key == 'csrfmiddlewaretoken':
                continue
            c = AviatorConfiguration.objects.get(key)
            c.value = value
            c.save()
        return self.get(request)

def AviatorDetail(request, houseId):
    aviator = Aviator.objects.filter(houseId=houseId)
    aviator_conf = AviatorConfiguration.objects.filter(aviator__houseId=houseId)

class LenseServer(APIView):
    """Aviator will update its system metrics if records exist in db or create one """
    def put(self, request):
        try:
            house_did = request.data.get('house_id')
            pi_did = request.data.get('pi')
            uptime = request.data.get('uptime')
            memory = request.data.get('memory')
            cpu = request.data.get('CPU')
            process = request.data.get('process')
            # list of active process for an instance
            active = process['active']
            # list of processes using memory than defined threshold
            gt_memory = process['gt_memory']
            # list of processes according to cpu usage
            top_cpu = process['top_cpu']
            # list of processes according to memory usage
            top_memory = process['top_memory']
            usb = request.data.get('USB')
            house_name = request.data.get('name')
            logger.info('Updating lense server for aviator with Pi_id: '+str(pi_did)+'and house Id: '+str(house_did)+'having name: '+str(house_name))
            pi_from_db = Aviator.objects.get_or_create(pi_did=pi_did)
            if pi_from_db:
                pi_from_db.houseId = house_did
                pi_from_db.house_name = house_name
                pi_from_db.uptime = uptime
                pi_from_db.memory.total = memory['total']
                pi_from_db.memory.avail = memory['available']
                pi_from_db.memory.per_used = memory['percent_used']
                pi_from_db.cpu_use = cpu
                pi_from_db.usb = usb
                pi_from_db.save()
            else:
                logger.info('Aviator is not registered in lense DB with Pi: '+str(pi_did))

            active_process_obj = Activeprocess.objects.get_or_create(aviator__pi_did=pi_did)
            active_process_obj.pid = active[0][0]
            active_process_obj.name = active[0][1]['name']
            active_process_obj.status =active[0][1]['status']
            active_process_obj.save()

            topCpuProcess = TopCpuProcess.objects.bulk_create(
                [
                    TopCpuProcess(aviator__pi_did=pi_did, pid=pid, name=name, usage=usage) for pid,name,usage in top_cpu
                ]
            )
            topCpuProcess.save()

            topMemoryProcess = TopMemoryProcess.objects.bulk_create(
                [
                    TopMemoryProcess(aviator__pi_did=pi_did, pid=pid, memory_percent_usage=memory_percent,name=name) for pid,memory_percent,name in top_memory
                ]
            )
            topMemoryProcess.save()

            processOnMemoryThreshold = ProcessOnMemoryThreshold.objects.bulk_create(
                [
                    ProcessOnMemoryThreshold(aviator__pi_did=pi_did, pid=pid, name=name, mem_used=usage) for pid,name,usage in gt_memory
                ]
            )


            return Response({'Done'}, status=status.HTTP_200_OK)
        except BaseException, e:
            logger.exception('Exception while updating Master Pi. Exception: '+ str(e) +'.')
            error_data = {
                'error_text':'Some error has occured. Pls contact support@dyfolabs.com'
            }
            return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):

        aviator = Aviator.objects.filter(houseId=str(request.data.get('house_id')))
        return

