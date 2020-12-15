from django.shortcuts import render, redirect, HttpResponse
from up_load.models import Form, Channel
from .models import SwtWork, Active
from django.contrib import messages
import datetime
from distribute.views import get_dates, get_info_statistical, get_swt_statistical, get_rate_statistical, \
    get_sale_turnover
from login.views import is_login


def today():
    return datetime.date.today()


def consult(request):
    """任务页入口"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 1 and request.session.get('user_limit') != 2:
        sale = request.session.get('user_id')
        data = get_consult_form(sale)
        data['turnover'] = get_sale_turnover(request)
        return render(request, 'consult/consult.html', data)
    else:
        return redirect('/index/')


def get_consult_form(sale):
    """咨询页数据"""
    t = today()
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    active = Active.objects.all().values()
    active = {i['title']: i['active'] for i in active}
    form = Form.objects.filter(consult=sale, distribute_time=t).values('channel', 'title',
                                                                       'name', 'active',
                                                                       'phone', 'mark', 'id')
    form_complete_num = 0
    data = {'form': [], 'statistical': {
        'form_today': len(form),
        'no_consult_num': 0,
        'form_active_num': 0,
        'form_no_active_num': 0,
        'form_re_num': 0,
        'form_no_line_num': 0,
    }}
    for i in form:
        if i['active'] is None:
            data['statistical']['no_consult_num'] += 1
        else:
            if i['active'] == 1:
                data['statistical']['form_active_num'] += 1
            elif 2 <= i['active'] <= 9:
                data['statistical']['form_no_active_num'] += 1
            elif 10 <= i['active'] <= 15:
                data['statistical']['form_re_num'] += 1
            elif i['active'] == 16:
                data['statistical']['form_no_line_num'] += 1
            else:
                pass
            form_complete_num += 1
            i['active'] = active[i['active']]
        i['channel'] = channel[i['channel']]
        data['form'].append(i)
    if form_complete_num != 0 and len(form) != 0:
        data['statistical']['form_complete_rate'] = round(form_complete_num/len(form)*100, 2)
    else:
        data['statistical']['form_complete_rate'] = 0
    return data


def submit_result(request):
    """提交咨询结果"""
    if request.method == 'POST':
        data = request.POST.lists()
        data = dict((x, y) for x, y in data)
        active = data['active'][0]
        if active == '':
            messages.success(request, '请填写表单有效性')
        else:
            form_id = data['form_id'][0]
            Form.objects.filter(id=form_id).update(active=active)
            messages.success(request, '咨询结果已提交')
            if request.session.get('user_limit') == 1:
                return redirect('/consult/')
            elif request.session.get('user_limit') >= 9:
                # return redirect('/index/')
                return render(request, 'frame.html')
            else:
                pass
    return redirect('/index/')


def talk_work(request):
    """易聊提交对话页"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 1 and request.session.get('user_limit') != 2:
        return render(request, 'consult/talk_work.html')
    else:
        return redirect('/index/')


def add_talk(request):
    """提交对话"""
    if request.method == 'POST':
        data = request.POST.lists()
        data = dict((x, y) for x, y in data)
        swt_xm = data['swt_xm'][0]
        if swt_xm == '':
            messages.success(request, '请填写商务通项目')
            return redirect('/talk_work/')
        else:
            t = data['swt_date'][0]
            sale = data['sale_id'][0]
            swt_a = data['swt_a'][0]
            swt_b = data['swt_b'][0]
            swt_c = data['swt_c'][0]
            swt_d = data['swt_d'][0]
            swt_point = SwtWork.objects.filter(time=t, sale=sale, swt_xm=swt_xm).count()
            if swt_point >= 1:
                SwtWork.objects.filter(time=t, sale=sale, swt_xm=swt_xm).update(swt_form_or_zz=swt_a,
                                                                                swt_active_form_or_jz=swt_b,
                                                                                swt_phone_or_tm=swt_c,
                                                                                swt_active_phone_or_xxm=swt_d)
            else:
                SwtWork.objects.create(time=t, sale=sale, swt_xm=swt_xm, swt_form_or_zz=swt_a,
                                       swt_active_form_or_jz=swt_b, swt_phone_or_tm=swt_c,
                                       swt_active_phone_or_xxm=swt_d)
            messages.success(request, '提交成功')
            return redirect('/talk_work/')
    return HttpResponse(1)


def sale_statistical(request, sale):
    """个人月统计函数"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') != 2:
        pass
    else:
        return redirect('/index/')
    # 日期和渠道
    # sale = request.session.get('user_id')
    dates = get_dates()
    channel_data = Channel.objects.all().values()
    channel = {}
    for i in channel_data:
        if i['channel_main'] in channel.keys():
            pass
        else:
            channel[i['channel_main']] = i['name']
    channel_main = {i['id']: i['channel_main'] for i in channel_data}
    # 统计数据
    mouth_info_hz, mouth_info_data = get_info_statistical(channel_main, channel, dates, sale)
    mouth_swt_hz, mouth_swt_data = get_swt_statistical(dates, sale)
    mouth_rate_data = get_rate_statistical(dates, mouth_info_hz, mouth_swt_hz, sale)
    return render(request, 'distribute/statistical.html',
                  {
                      'channel': channel,
                      'swt_xm': [1, 2, 3, 4, 5, 6],
                      'mouth_info_hz': mouth_info_hz,
                      'mouth_info_data': mouth_info_data,
                      'mouth_swt_hz': mouth_swt_hz,
                      'mouth_swt_data': mouth_swt_data,
                      'mouth_rate_data': mouth_rate_data
                  }
                  )


def no_consult(request):
    """未咨询表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 1 and request.session.get('user_limit') != 2:
        sale = request.session.get('user_id')
        data = get_no_consult(sale)
        return render(request, 'consult/consult.html', data)
    else:
        return redirect('/index/')


def get_no_consult(sale):
    """获取未咨询表单"""
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    form = Form.objects.filter(consult=sale, active=None).values('channel', 'title',
                                                                 'name', 'active',
                                                                 'phone', 'mark', 'id')
    data = {'form': []}
    for i in form:
        i['channel'] = channel[i['channel']]
        data['form'].append(i)
    return data


def no_line(request):
    """未联系上表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 1 and request.session.get('user_limit') != 2:
        sale = request.session.get('user_id')
        data = get_no_line(sale)
        return render(request, 'consult/consult.html', data)
    else:
        return redirect('/index/')


def get_no_line(sale):
    """获取未联系上表单"""
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    active = Active.objects.all().values()
    active = {i['title']: i['active'] for i in active}
    form = Form.objects.filter(consult=sale, active=16).values('channel', 'title',
                                                               'name', 'active',
                                                               'phone', 'mark', 'id')
    data = {'form': []}
    for i in form:
        i['channel'] = channel[i['channel']]
        i['active'] = active[i['active']]
        data['form'].append(i)
    return data









