from django.db import models


class Channel(models.Model):
    """渠道名称"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25)
    channel_main = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'ygj_channel'
        verbose_name = "渠道"
        verbose_name_plural = verbose_name


class Form(models.Model):
    """推广部提供信息流表单"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, null=True, blank=True)  # 客户姓名
    phone = models.BigIntegerField(verbose_name="手机号")  # 客户手机号
    channel = models.IntegerField(verbose_name="渠道")  # 渠道id
    title = models.IntegerField()  # 信息流专题
    mark = models.CharField(max_length=100)  # 备注
    promoter = models.IntegerField()  # 推广人
    consult = models.IntegerField(null=True, blank=True, verbose_name="人员")  # 咨询人
    active = models.IntegerField(null=True, blank=True)  # 有效：1，无效：2-9,重复：10-15,未联系上：16
    submit_time = models.DateField(verbose_name="提交时间")  # 客户提交时间
    up_time = models.DateField(verbose_name="上传时间")  # 上传时间
    distribute_time = models.DateField(null=True, blank=True)  # 分配咨询时间

    def __str__(self):
        return self.channel

    class Meta:
        db_table = 'ygj_form'
        verbose_name = "表单"
        verbose_name_plural = verbose_name
