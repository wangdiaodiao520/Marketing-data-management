from django.db import models


# Create your models here.
class DoctorType(models.Model):
    """项目判断依据"""
    id = models.AutoField(primary_key=True)
    doctor_type = models.CharField(max_length=50)

    def __str__(self):
        return self.doctor_type

    class Meta:
        db_table = 'ygj_doctor_type'
        verbose_name = "项目判断"
        verbose_name_plural = verbose_name
