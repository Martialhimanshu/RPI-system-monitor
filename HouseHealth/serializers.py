from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer
from models import Restart, WifiDisconnection, QuickInterrupt, House, Configs, LongDisconnect, \
    AviatorDisconnection
from rest_framework import serializers
from constants import DYFO_TIME_FORMAT_OUTPUT
import datetime


class HouseSerializer(DocumentSerializer):
    last_updated = serializers.DateTimeField(DYFO_TIME_FORMAT_OUTPUT)

    class Meta:
        model = House
        fields = '__all__'


# ************************************RestartsSerializerStart*********************************

class WifiDisconnectionSerializer(EmbeddedDocumentSerializer):
    class Meta:
        model = WifiDisconnection
        fields = '__all__'


class RestartsSerializer(DocumentSerializer):
    wifi_disconnections = WifiDisconnectionSerializer(many=True)
    restart_time = serializers.DateTimeField(DYFO_TIME_FORMAT_OUTPUT)

    def create(self, validated_data):
        wifi_disconnections_data = validated_data.pop('wifi_disconnections')
        w_list = []
        for disconnections in wifi_disconnections_data:
            w_list.append(WifiDisconnection(**disconnections))

        restart = Restart.objects.create(wifi_disconnections=w_list, **validated_data)
        return restart

    class Meta:
        model = Restart
        depth = 2
        fields = '__all__'

class RestartsReportSerializer(DocumentSerializer):
    restart_time = serializers.DateTimeField(DYFO_TIME_FORMAT_OUTPUT)
    class Meta:
        model=Restart
        fields=('house_id','astro_id','restart_time','reason','comment', 'device_type')


# ************************************RestartsSerializerEnd*********************************

class QuickInterruptSerializer(DocumentSerializer):
    time=serializers.DateTimeField(DYFO_TIME_FORMAT_OUTPUT)
    class Meta:
        model = QuickInterrupt
        fields = '__all__'


class ConfigurationSerializer(DocumentSerializer):
    class Meta:
        model = Configs
        fields = '__all__'


class LongDisconnectSerializer(DocumentSerializer):
    disconnected_at = serializers.DateTimeField(DYFO_TIME_FORMAT_OUTPUT)

    class Meta:
        model = LongDisconnect
        fields = "__all__"


class AviatorDisconnectSerializer(DocumentSerializer):
    class Meta:
        model = AviatorDisconnection
        fields = "__all__"
