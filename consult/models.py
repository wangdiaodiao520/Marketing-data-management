from django.db import models


class InfoWork(models.Model):
    """信息流工作表"""
    id = models.AutoField(primary_key=True)
    channel = models.IntegerField()
    order = models.IntegerField()
    arrive = models.IntegerField()
    title = models.IntegerField()
    sale = models.IntegerField()
    time = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ygj_info_work'


class SwtWork(models.Model):
    """商务通工作表"""
    id = models.AutoField(primary_key=True)
    swt_form_or_zz = models.IntegerField()
    swt_active_form_or_jz = models.IntegerField()
    swt_phone_or_tm = models.IntegerField()
    swt_active_phone_or_xxm = models.IntegerField()
    swt_xm = models.IntegerField()  # 1:预约，2：到院，3：种植，4：矫正，5：贴面，6：小项目
    sale = models.IntegerField()
    time = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'ygj_swt_work'


class Active(models.Model):
    """表单有效性"""
    id = models.AutoField(primary_key=True)
    title = models.IntegerField()
    active = models.CharField(max_length=20)

    def __str__(self):
        return self.active

    class Meta:
        db_table = 'ygj_active'
        verbose_name = "有效性"
        verbose_name_plural = verbose_name
