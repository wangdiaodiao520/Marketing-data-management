from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import *
from longqi.consumers import R


def is_login(request):
    if request.session.get('is_login', None):
        r = R()
        request.session['top_info'] = r.get()
        return request
    else:
        return False


def index(request):
    """主页引导"""
    if is_login(request):
        if request.session.get('user_limit') == 1:
            return redirect('/consult/')
        if request.session.get('user_limit') == 2:
            return redirect('/form_quality/')
        if request.session.get('user_limit') == 9:
            return redirect('/distribute/')
        if request.session.get('user_limit') == 10:
            return redirect('/handle/')
        if request.session.get('user_limit') == 11:
            return redirect('/longqi/')
    return render(request, '../templates/login/login.html')


def login(request):
    """登录函数"""
    if is_login(request):
        return redirect('/index')
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        if login_form.is_valid():
            user_name = login_form.cleaned_data['user_name']
            user_pd = login_form.cleaned_data['user_pd']
            try:
                user = User.objects.get(user_name=user_name)
            except User.DoesNotExist:
                messages.success(request, "用户不存在！")
                return render(request, '../templates/login/login.html')
            if user.user_pd == user_pd:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.user_name
                request.session['user_limit'] = user.user_limit
                return redirect('/index')
            else:
                messages.success(request, "密码不正确！")
        messages.success(request, "登录信息错误！")
        return render(request, '../templates/login/login.html')
    login_form = UserForm()
    return render(request, '../templates/login/login.html', locals())


def logout(request):
    """登出函数"""
    if not is_login(request):
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")
