from __future__ import unicode_literals
from mongoengine import EmbeddedDocument, StringField, IntField, Document, ListField, EmbeddedDocumentField, DictField, \
    DateTimeField, BooleanField, FloatField
from django.db import models
from .constants import type_of_alerts

# Create your models here.

# class Memory(EmbeddedDocument):
#     avail = IntField(max_length=50)
#     total = IntField(max_length=50)
#     usage_per = FloatField(max_length=5)
#
#     def __str__(self):
#         return self.usage_per
#
#
# class Process(EmbeddedDocument):
#     active = ListField()
#     greater_than_memory = ListField()
#     top_cpu = ListField()
#     top_memory = ListField()
#
#     def __str__(self):
#         return self.active
#
#
# class Metric(EmbeddedDocument):
#     created_on = DateTimeField(auto_now_add=True, null=True)
#     cpu = DictField()
#     usb = ListField()
#     memory = EmbeddedDocumentField(Memory)
#     process = EmbeddedDocumentField(Process)
#     uptime = DateTimeField()
#
#     def __str__(self):
#         return self.created_on
#
#
# class Aviator(EmbeddedDocument):
#     pi_id = StringField(max_length=20)
#     is_active = DateTimeField()
#     metric = EmbeddedDocumentField(Metric)
#
#     def __str__(self):
#         return self.pi_id
#
# class House(Document):
#     id = StringField(max_length=10)
#     name = StringField(max_length=50)
#     aviator = ListField(EmbeddedDocumentField(Aviator))
#
#     def __str__(self):
#         return self.id
#
# class Alerts(Document):
#     h_id = StringField(max_length=10)
#     Name = StringField(max_length=50)
#     level = StringField(max_length=50)
#     time = DateTimeField()
#     house = StringField(max_length=50)
#     value = FloatField()
#
#     def __str__(self):
#         return self.Name
#
#
# class AlertThreshold(Document):
#     mem_usage = FloatField()
#     cpu_usage = FloatField()
#     disk_usage = FloatField()
#     usb = BooleanField(default=True)
#
#     def __str__(self):
#         return self.aviator_status

class Memory(models.Model):
    total = models.DecimalField(max_digits=10, decimal_places=3)
    avail = models.DecimalField(max_digits=10, decimal_places=3)
    per_used = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.per_used)

class Usb(models.Model):
    name = models.CharField(max_length=500, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Aviator(models.Model):
    pi_did = models.CharField(max_length=5)
    houseId = models.CharField(max_length=10)
    house_name = models.CharField(max_length=100)
    uptime = models.DateTimeField()
    cpu_use = models.DecimalField(max_digits=5,decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    memory = models.OneToOneField(Memory, on_delete=models.CASCADE)
    usb = models.ForeignKey(Usb, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.house_name+", "+self.houseId

class AviatorConfiguration(models.Model):
    aviator = models.OneToOneField(Aviator, on_delete=models.CASCADE)
    mem_threshold = models.DecimalField(max_digits=6, decimal_places=3)
    cpu_threshold = models.DecimalField(max_digits=5, decimal_places=2)
    update_freq = models.IntegerField(default=300)
    process_limit = models.IntegerField(default=5)
    memory_greater_than = models.IntegerField(default=200)


class Alert(models.Model):
    aviator = models.ForeignKey(Aviator, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    generated_at = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, choices=type_of_alerts, default='Information')
    value = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Activeprocess(models.Model):
    aviator = models.OneToOneField(Aviator, on_delete=models.CASCADE)
    pid = models.IntegerField()
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TopCpuProcess(models.Model):
    aviator = models.ForeignKey(Aviator, on_delete=models.CASCADE)
    pid = models.IntegerField()
    name = models.CharField(max_length=100)
    usage = models.DecimalField(max_digits=7, decimal_places=3)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name, self.pid, self.usage

class TopMemoryProcess(models.Model):
    aviator = models.ForeignKey(Aviator, on_delete=models.CASCADE)
    pid = models.IntegerField()
    name = models.CharField(max_length=100)
    memory_percent_usage = models.DecimalField(max_digits=5, decimal_places=3)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name, self.pid, self.memory_percent_usage

class ProcessOnMemoryThreshold(models.Model):
    aviator = models.ForeignKey(Aviator, on_delete=models.CASCADE)
    pid = models.IntegerField()
    name = models.CharField(max_length=100)
    mem_used = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name, self.pid, self.mem_used