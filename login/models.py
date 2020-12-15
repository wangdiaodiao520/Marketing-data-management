from django.db import models
from django import forms


class User(models.Model):
    """用户表"""
    id = models.AutoField(primary_key=True)  # id
    user_name = models.CharField(max_length=50, unique=True, verbose_name="姓名")  # 用户名
    user_pd = models.CharField(max_length=50, verbose_name="密码")  # 用户密码
    user_limit = models.IntegerField(verbose_name="权限")  # 权限标识，1：咨询，2：推广，9：管理
    status = models.IntegerField(verbose_name="状态")  # 在职状态，0为离职，1为在职

    def __str__(self):
        return self.user_name

    class Meta:
        db_table = 'ygj_users'
        verbose_name = "人员"
        verbose_name_plural = verbose_name


class UserForm(forms.Form):
    """用户构造form"""
    user_name = forms.CharField(label="用户名", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_pd = forms.CharField(label="密码", max_length=50, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
