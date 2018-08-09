from rest_framework import serializers
from lense.models import AviatorConfiguration

class AviatorConfigurationserializer(serializers.Serializer):
    aviator = serializers.CharField(max_length=200)
    mem_threshold = serializers.DecimalField(max_digits=6, decimal_places=3)
    cpu_threshold = serializers.DecimalField(max_digits=5, decimal_places=2)
    update_freq = serializers.IntegerField(default=300)
    process_limit = serializers.IntegerField(default=5)
    memory_greater_than = serializers.IntegerField(default=200)