from django.db import models


class Turnover(models.Model):
    """营业额"""
    id = models.AutoField(primary_key=True)
    phone = models.IntegerField(verbose_name="手机号")
    # turnover = models.DecimalField(max_digits=10, decimal_places=2)
    turnover = models.CharField(max_length=50, verbose_name="营业额")
    channel_main = models.IntegerField()
    consult = models.IntegerField()
    title = models.IntegerField()
    time = models.DateField(verbose_name="时间")

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'ygj_turnover'
        verbose_name = "营业额"
        verbose_name_plural = verbose_name


class ArriveData(models.Model):
    """到院数据"""
    id = models.AutoField(primary_key=True)
    phone = models.IntegerField(verbose_name="手机号")
    channel_main = models.IntegerField()
    consult = models.IntegerField()
    title = models.IntegerField()
    time = models.DateField(verbose_name="时间")

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'ygj_arrive'
        verbose_name = "到院"
        verbose_name_plural = verbose_name


class OrderData(models.Model):
    """预约数据"""
    id = models.AutoField(primary_key=True)
    phone = models.IntegerField(verbose_name="手机号")
    channel_main = models.IntegerField()
    consult = models.IntegerField()
    title = models.IntegerField()
    time = models.DateField(verbose_name="时间")

    def __str__(self):
        return self.phone

    class Meta:
        db_table = 'ygj_order'
        verbose_name = "预约"
        verbose_name_plural = verbose_name
