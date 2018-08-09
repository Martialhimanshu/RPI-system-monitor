from django.contrib import admin
from lense.models import Aviator, Memory, AviatorConfiguration, Usb, TopCpuProcess, TopMemoryProcess,ProcessOnMemoryThreshold
# Register your models here.
admin.site.register(Usb)
admin.site.register(TopMemoryProcess)
admin.site.register(Aviator)
admin.site.register(TopCpuProcess)
admin.site.register(Memory)
# admin.site.register(Process)
admin.site.register(ProcessOnMemoryThreshold)
admin.site.register(AviatorConfiguration)