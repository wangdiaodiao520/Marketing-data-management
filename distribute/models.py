from django.db import models


class ToothWash(models.Model):
    """每日洗牙数量"""
    id = models.AutoField(primary_key=True)
    arrive_num = models.IntegerField()
    time = models.DateField()

    class Meta:
        db_table = 'ygj_tooth_wash'
