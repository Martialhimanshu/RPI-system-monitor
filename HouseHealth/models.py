# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from mongoengine import EmbeddedDocument, StringField, IntField, Document, ListField, EmbeddedDocumentField, DictField, \
    DateTimeField, BooleanField


# Create your models here.

class House(Document):
    """
    Represents Each house in Database
    """
    last_updated = DateTimeField()
    house_id = StringField(max_length=10, required=True, unique=True)
    house_name = StringField(max_length=100)
    status = StringField(max_length=100, default="ACTIVE")
    qi_count = IntField(default=0)
    restart_count = IntField(default=0)
    ld_count = IntField(default=0)
    astro_state = StringField(max_length=20, default="live")
    to_update = BooleanField(default=True)
    code_version = StringField(max_length=5, default="1.1")


# ***********************Restart****************************************

class WifiDisconnection(EmbeddedDocument):
    """
    Represents Wifi disconnections of Astro restarted
    """
    epoch_to = IntField(default=0)
    time_from = StringField(max_length=100)
    epoch_from = IntField(default=0)
    period = IntField(default=0)
    time_to = StringField(max_length=100)


class Restart(Document):
    """
    Represents restart state of an astro
    """
    house_id = StringField(max_length=10, null=False)
    astro_id = StringField(max_length=50, null=False)
    restart_time = DateTimeField(required=True, unique_with='astro_id')
    reason = StringField(max_length=500, null=False)
    wifi_disconnections = ListField(EmbeddedDocumentField(WifiDisconnection))
    comment = StringField(max_length=200, default='')
    mobile_pin_status = DictField()
    interrupt_pin_status = DictField()
    device_type = StringField(max_length=10, default='')


# ***********************END_Restart****************************************

# ***********************Quick_Interrupt****************************************


class QuickInterrupt(Document):
    """
    Represents quick interrupts of Astro
    """
    house_id = StringField(max_length=10)
    astro_id = StringField(max_length=50, null=False)
    time = DateTimeField(required=True, unique_with=('astro_id', 'pin'))
    count = IntField()
    pin = IntField()
    interrupt_pin_state = DictField()
    mobile_pin_state = DictField()
    other_interrupt_pin_state = DictField()
    other_mobile_pin_state = DictField()


class LongDisconnect(Document):
    """
    Represents Long Cutoff of Astro
    """
    house_id = StringField(max_length=10, null=False)
    astro_id = StringField(max_length=10, null=False, unique=True)
    status = StringField(max_length=10, default='INACTIVE')
    disconnected_at = DateTimeField(null=False)


class Configs(Document):
    """
    Represents Configurations set by user
    """
    key = StringField(null=False, unique=True, max_length=128)
    value = StringField(null=False)
    details = StringField(max_length=100)


class AviatorDisconnection(Document):
    """
    Represents Disconnections of Aviator.
    """
    house_id = StringField(max_length=10, null=False)
    time_from = DateTimeField(required=True, unique_with='house_id')
    time_to = DateTimeField()
    period = IntField()
