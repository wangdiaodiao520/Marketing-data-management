from django.shortcuts import render, redirect
from django.db.models import Sum, Q
from django.contrib import messages
import datetime
import time
from login.models import User
from up_load.models import Form, Channel
from consult.models import InfoWork, SwtWork, Active
import collections
from handle.models import Turnover, ArriveData, OrderData
from decimal import Decimal
from login.views import is_login


def today():
    return datetime.date.today()


def get_dates():
    day_now = time.localtime()
    start = '%d-%02d-01' % (day_now.tm_year, day_now.tm_mon)
    end = datetime.datetime.now().strftime('%Y-%m-%d')
    # start = '2020-11-23'
    # end = '2020-11-29'
    dates = []
    dt = datetime.datetime.strptime(start, "%Y-%m-%d")
    date = start[:]
    while date <= end:
        dates.append(date)
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    # return ['2020-12-02', '2020-12-08']
    return dates


def get_sale_turnover(request):
    dates = get_dates()
    dates = [dates[0], dates[-1]]
    if request.session.get('user_limit') == 1:
        sale = request.session.get('user_id')
        turnover = Turnover.objects.filter(consult=sale, time__range=dates).values('turnover')
    else:
        turnover = Turnover.objects.filter(time__range=dates).values('turnover')
    turnover_all = 0
    for i in turnover:
        turnover_all += Decimal(i['turnover']).quantize(Decimal('0.00'))
    return turnover_all


def distribute(request):
    """分配主页入口"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 9:
        re_data = distribute_data()
        re_data['form_data'] = get_form()
        re_data['complete_rate'] = complete_rate(re_data)
        re_data['active_rate'] = active_rate(re_data)
        re_data['turnover'] = get_sale_turnover(request)
        return render(request, 'distribute/distribute.html', re_data)
    else:
        return redirect('/index/')


def distribute_data():
    """分配页显示基础数据"""
    data = {}
    t = today()
    # 咨询人员
    consultant = User.objects.filter(user_limit=1, status=1).values()
    consultant = {i['id']: i['user_name'] for i in consultant}
    data['consultant'] = consultant
    # 未分配表单数量
    form = Form.objects.filter(consult=None).count()
    data['form'] = form
    # 当日分配表单
    form_today = Form.objects.filter(~Q(consult=None), distribute_time=t).values('consult', 'active')
    distribute_today = len(form_today)
    data['distribute_today'] = distribute_today
    # 当日咨询量
    consult_today = Form.objects.filter(~Q(active=None), distribute_time=t).count()
    data['consult_today'] = consult_today
    # 当日有效量
    active_today = Form.objects.filter(distribute_time=t, active=1).count()
    data['active_today'] = active_today
    # 咨询人表单情况
    sale_form = {}
    complete = 0
    for i in form_today:
        sale = consultant[i['consult']]
        if sale in sale_form.keys():
            pass
        else:
            sale_form[sale] = {'all': 0, 'suc': 0, 'fal': 0}
        sale_form[sale]['all'] = sale_form[sale]['all'] + 1
        if i['active'] is None:
            sale_form[sale]['fal'] = sale_form[sale]['fal'] + 1
        else:
            sale_form[sale]['suc'] = sale_form[sale]['suc'] + 1
            complete = complete + 1
    data['sale_form'] = sale_form
    data['complete'] = complete
    return data


def get_form():
    """获取未分配表单详情"""
    # 获取渠道
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    # 获取未分配表单
    forms = Form.objects.filter(consult=None).values()
    # 未分配表单按渠道分类
    form_data = {}
    for form in forms:
        if form['channel'] in form_data.keys():
            form_data[form['channel']]['num'] += 1
        else:
            form_data[form['channel']] = {'name': channel[form['channel']], 'num': 1}
    return form_data


def complete_rate(data):
    """当日完成率"""
    form_all = data['distribute_today']
    form_consult = data['complete']
    if form_all == 0:
        return 0
    else:
        return round((form_consult / form_all * 100), 2)


def active_rate(data):
    """当日有效率"""
    form_consult = data['consult_today']
    form_active = data['active_today']
    if form_consult == 0:
        return 0
    else:
        return round((form_active / form_consult * 100), 2)


def distribute_form(request):
    """分配表单"""
    if request.method == 'POST':
        data = request.POST.lists()
        data = dict((x, y) for x, y in data)
        if data['consult'] == ['']:
            messages.success(request, '请选择咨询人')
        else:
            t = today()
            # channel = Channel.objects.all().values()
            # channel = {i['name']: i['id'] for i in channel}
            consult = data['consult'][0]
            form_num = data['form_num'][0]
            channel = data['channel'][0]
            data = Form.objects.filter(consult=None,
                                       channel=channel).order_by('submit_time').values('id')[:int(form_num)]
            for i in data:
                Form.objects.filter(id=i['id']).update(consult=consult, distribute_time=t)
            messages.success(request, '分配成功')
            return redirect('/distribute/')
    return redirect('/distribute/')


def mouth_statistical(request):
    """月统计函数"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 9:
        pass
    else:
        return redirect('/index/')
    # 日期和渠道
    sale = None
    dates = get_dates()
    channel_data = Channel.objects.all().values()
    channel = {}
    for i in channel_data:
        if i['channel_main'] in channel.keys():
            pass
        else:
            channel[i['channel_main']] = i['name']
    channel_main = {i['id']: i['channel_main'] for i in channel_data}
    mouth_info_hz, mouth_info_data = get_info_statistical(channel_main, channel, dates, sale)
    mouth_swt_hz, mouth_swt_data = get_swt_statistical(dates, sale)
    mouth_rate_data = get_rate_statistical(dates, mouth_info_hz, mouth_swt_hz, sale)
    week_data = sale_week_rate()
    return render(request, 'distribute/statistical.html',
                  {
                      'channel': channel,
                      'swt_xm': [1, 2, 3, 4, 5, 6],
                      'mouth_info_hz': mouth_info_hz,
                      'mouth_info_data': mouth_info_data,
                      'mouth_swt_hz': mouth_swt_hz,
                      'mouth_swt_data': mouth_swt_data,
                      'mouth_rate_data': mouth_rate_data,
                      'week_data': week_data,
                      'frame_data': {'zz_active': mouth_rate_data['汇总'][1],
                                     'another_active': mouth_rate_data['汇总'][5],
                                     'form_active_rate': mouth_rate_data['汇总'][-4],
                                     'order_rate': mouth_rate_data['汇总'][-2],
                                     'arrive_rate': mouth_rate_data['汇总'][-1],
                                     }
                  }
                  )


def get_info_statistical(channel_main, channel, dates, sale):
    """信息流表单月度统计"""
    # 月度表单数据
    if not sale:
        mouth_info_form = Form.objects.filter(distribute_time__range=[dates[0], dates[-1]]).values(
            'channel', 'title', 'active', 'distribute_time'
        )
        """
         mouth_info_work = InfoWork.objects.filter(time__range=[dates[0], dates[-1]]).values(
            'channel', 'title', 'order', 'arrive', 'time'
        )
        """
        mouth_info_arrive = ArriveData.objects.filter(~Q(channel_main=999), time__range=[dates[0], dates[-1]]).values(
            'time', 'title', 'channel_main'
        )
        mouth_info_order = OrderData.objects.filter(~Q(channel_main=999), time__range=[dates[0], dates[-1]]).values(
            'time', 'title', 'channel_main'
        )
    else:
        mouth_info_form = Form.objects.filter(distribute_time__range=[dates[0], dates[-1]], consult=sale).values(
            'channel', 'title', 'active', 'distribute_time'
        )
        """
        mouth_info_work = InfoWork.objects.filter(time__range=[dates[0], dates[-1]], sale=sale).values(
            'channel', 'title', 'order', 'arrive', 'time'
        )
        """
        mouth_info_arrive = ArriveData.objects.filter(~Q(channel_main=999), time__range=[dates[0], dates[-1]],
                                                      consult=sale).values('time', 'title', 'channel_main')
        mouth_info_order = OrderData.objects.filter(~Q(channel_main=999), time__range=[dates[0], dates[-1]],
                                                    consult=sale).values('time', 'title', 'channel_main')
    # 信息流表单统计和汇总
    mouth_info_data = {}
    for i in dates:
        mouth_info_data[i] = {}
    mouth_info_hz = {}
    for i in dates:
        mouth_info_hz[i] = {'no_active': 0, 're_form': 0, 'hz': {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}}
    for i in mouth_info_form:
        i_time = i['distribute_time'].strftime("%Y-%m-%d")
        if channel_main[i['channel']] in mouth_info_data[i_time].keys():
            pass
        else:
            mouth_info_data[i_time][channel_main[i['channel']]] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
        # 渠道表单+1
        mouth_info_data[i_time][channel_main[i['channel']]][i['title']][0] += 1
        # 排除支付宝表单总数统计
        if '支付宝' in channel[channel_main[i['channel']]]:
            pass
        else:
            # 汇总表单+1
            mouth_info_hz[i_time]['hz'][i['title']][0] += 1
        # 有效情况
        if i['active']:
            if i['active'] == 1:
                # 渠道有效+1
                mouth_info_data[i_time][channel_main[i['channel']]][i['title']][1] += 1
                # 汇总有效+1
                mouth_info_hz[i_time]['hz'][i['title']][1] += 1
            elif 2 <= i['active'] <= 9:
                # 汇总无效+1
                mouth_info_hz[i_time]['no_active'] = mouth_info_hz[i_time]['no_active'] + 1
            elif 10 <= i['active'] <= 15:
                # 汇总重复+1
                mouth_info_hz[i_time]['re_form'] = mouth_info_hz[i_time]['re_form'] + 1
    # 信息流预约到院
    """
    for i in mouth_info_work:
        i_time = i['time'].strftime("%Y-%m-%d")
        if i['channel'] in mouth_info_data[i_time].keys():
            pass
        else:
            mouth_info_data[i_time][i['channel']] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
        mouth_info_data[i_time][i['channel']][i['title']][2] += i['order']
        mouth_info_data[i_time][i['channel']][i['title']][3] += i['arrive']
        mouth_info_hz[i_time]['hz'][i['title']][2] += i['order']
        mouth_info_hz[i_time]['hz'][i['title']][3] += i['arrive']
    """
    for i in mouth_info_order:
        i_time = i['time'].strftime("%Y-%m-%d")
        if i['channel_main'] in mouth_info_data[i_time].keys():
            pass
        else:
            mouth_info_data[i_time][i['channel_main']] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
        if i['title'] == 1:
            mouth_info_data[i_time][i['channel_main']][1][2] += 1
            mouth_info_hz[i_time]['hz'][1][2] += 1
        else:
            mouth_info_data[i_time][i['channel_main']][2][2] += 1
            mouth_info_hz[i_time]['hz'][2][2] += 1
    for i in mouth_info_arrive:
        i_time = i['time'].strftime("%Y-%m-%d")
        if i['channel_main'] in mouth_info_data[i_time].keys():
            pass
        else:
            mouth_info_data[i_time][i['channel_main']] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
        if i['title'] ==1:
            mouth_info_data[i_time][i['channel_main']][1][3] += 1
            mouth_info_hz[i_time]['hz'][1][3] += 1
        else:
            mouth_info_data[i_time][i['channel_main']][2][3] += 1
            mouth_info_hz[i_time]['hz'][2][3] += 1
    # 汇总
    hz_hz = {'no_active': 0, 're_form': 0, 'hz': {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}}
    data_hz = {}
    for k, v in mouth_info_hz.items():
        hz_hz['no_active'] += v['no_active']
        hz_hz['re_form'] += v['re_form']
        hz_hz['hz'][1] = [i + j for i, j in zip(hz_hz['hz'][1], v['hz'][1])]
        hz_hz['hz'][2] = [i + j for i, j in zip(hz_hz['hz'][2], v['hz'][2])]
    for k, v in mouth_info_data.items():
        if v == {}:
            pass
        else:
            for m, n in v.items():
                if m in data_hz.keys():
                    pass
                else:
                    data_hz[m] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
                data_hz[m][1] = [i + j for i, j in zip(data_hz[m][1], n[1])]
                data_hz[m][2] = [i + j for i, j in zip(data_hz[m][2], n[2])]
    mouth_info_hz['汇总'] = hz_hz
    mouth_info_data['汇总'] = data_hz
    return mouth_info_hz, mouth_info_data


def get_swt_statistical(dates, sale):
    """商务通月度统计"""
    # 月度表单数据
    if not sale:
        mouth_swt_form = SwtWork.objects.filter(time__range=[dates[0], dates[-1]], swt_xm__gt=2).values(
            'swt_form_or_zz', 'swt_active_form_or_jz', 'swt_xm',
            'swt_phone_or_tm', 'swt_active_phone_or_xxm', 'time'
        )
        mouth_info_arrive = ArriveData.objects.filter(channel_main=999, time__range=[dates[0], dates[-1]]).values(
            'time', 'title', 'channel_main'
        )
        mouth_info_order = OrderData.objects.filter(channel_main=999, time__range=[dates[0], dates[-1]]).values(
            'time', 'title', 'channel_main'
        )
    else:
        mouth_swt_form = SwtWork.objects.filter(time__range=[dates[0], dates[-1]], sale=sale, swt_xm__gt=2).values(
            'swt_form_or_zz', 'swt_active_form_or_jz', 'swt_xm',
            'swt_phone_or_tm', 'swt_active_phone_or_xxm', 'time'
        )
        mouth_info_arrive = ArriveData.objects.filter(channel_main=999, time__range=[dates[0], dates[-1]],
                                                      consult=sale).values('time', 'title')
        mouth_info_order = OrderData.objects.filter(channel_main=999, time__range=[dates[0], dates[-1]],
                                                    consult=sale).values('time', 'title')
    # 商务通统计
    mouth_swt_data = {}
    for i in dates:
        mouth_swt_data[i] = {1: [0, 0, 0, 0], 2: [0, 0, 0, 0]}
    mouth_swt_hz = {}
    for i in dates:
        mouth_swt_hz[i] = [0, 0, 0, 0, 0, 0,
                           0, 0, 0, 0, 0, 0]
    for i in mouth_swt_form:
        i_time = i['time'].strftime("%Y-%m-%d")
        if i['swt_xm'] in mouth_swt_data[i_time].keys():
            pass
        else:
            mouth_swt_data[i_time][i['swt_xm']] = [0, 0, 0, 0]
        # 每日数据
        mouth_swt_data[i_time][i['swt_xm']][0] += i['swt_form_or_zz']
        mouth_swt_data[i_time][i['swt_xm']][1] += i['swt_active_form_or_jz']
        mouth_swt_data[i_time][i['swt_xm']][2] += i['swt_phone_or_tm']
        mouth_swt_data[i_time][i['swt_xm']][3] += i['swt_active_phone_or_xxm']
        """
        # 汇总预约，分种植其他
        if i['swt_xm'] == 1:
            mouth_swt_hz[i_time][4] += i['swt_form_or_zz']
            mouth_swt_hz[i_time][10] += i['swt_active_form_or_jz']
            mouth_swt_hz[i_time][10] += i['swt_phone_or_tm']
            mouth_swt_hz[i_time][10] += i['swt_active_phone_or_xxm']
        # 汇总到院，分种植其他
        elif i['swt_xm'] == 2:
            mouth_swt_hz[i_time][5] += i['swt_form_or_zz']
            mouth_swt_hz[i_time][11] += i['swt_active_form_or_jz']
            mouth_swt_hz[i_time][11] += i['swt_phone_or_tm']
            mouth_swt_hz[i_time][11] += i['swt_active_phone_or_xxm']
        """
        # 汇总种植对话
        if i['swt_xm'] == 3:
            mouth_swt_hz[i_time][0] += i['swt_form_or_zz']
            mouth_swt_hz[i_time][1] += i['swt_active_form_or_jz']
            mouth_swt_hz[i_time][2] += i['swt_phone_or_tm']
            mouth_swt_hz[i_time][3] += i['swt_active_phone_or_xxm']
        # 汇总其他对话
        else:
            mouth_swt_hz[i_time][6] += i['swt_form_or_zz']
            mouth_swt_hz[i_time][7] += i['swt_active_form_or_jz']
            mouth_swt_hz[i_time][8] += i['swt_phone_or_tm']
            mouth_swt_hz[i_time][9] += i['swt_active_phone_or_xxm']
    for i in mouth_info_order:
        i_time = i['time'].strftime("%Y-%m-%d")
        mouth_swt_data[i_time][1][i['title']-1] += 1
    for i in mouth_info_arrive:
        i_time = i['time'].strftime("%Y-%m-%d")
        mouth_swt_data[i_time][2][i['title']-1] += 1
    for k, v in mouth_swt_hz.items():
        v[4] = mouth_swt_data[k][1][0]
        v[5] = mouth_swt_data[k][2][0]
        v[10] = mouth_swt_data[k][1][1] +\
                mouth_swt_data[k][1][2] +\
                mouth_swt_data[k][1][3]
        v[11] = mouth_swt_data[k][2][1] + \
                mouth_swt_data[k][2][2] + \
                mouth_swt_data[k][2][3]
    # 汇总
    hz_hz = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    data_hz = {}
    for k, v in mouth_swt_hz.items():
        hz_hz = [i + j for i, j in zip(hz_hz, v)]
    for k, v in mouth_swt_data.items():
        if v == {}:
            pass
        else:
            for m, n in v.items():
                if m in data_hz.keys():
                    pass
                else:
                    data_hz[m] = [0, 0, 0, 0]
                data_hz[m] = [i + j for i, j in zip(data_hz[m], n)]
    mouth_swt_hz['汇总'] = hz_hz
    mouth_swt_data['汇总'] = data_hz
    return mouth_swt_hz, mouth_swt_data


def get_rate_statistical(dates, mouth_info_hz, mouth_swt_hz, sale):
    """转化率月度统计"""
    # 转化率计算
    mouth_rate_data = {}
    for i in dates:
        mouth_rate_data[i] = [0, 0, 0, 0,
                              0, 0, 0, 0]
    for k, v in mouth_rate_data.items():
        v_ = [i + j for i, j in zip(v, mouth_info_hz[k]['hz'][1] + mouth_info_hz[k]['hz'][2])]
        v_ = [i + j for i, j in zip(v_, mouth_swt_hz[k][2:6] + mouth_swt_hz[k][8:])]
        mouth_rate_data[k] = v_
    """
    for k, v in mouth_rate_data.items():
    try:
        tooth_wash_num = ToothWash.objects.filter(time=k).values('arrive_num')
        v.append(tooth_wash_num[0]['arrive_num'])
    # 待指定未搜索到错误类型
    except:
        v.append(0)
    """
    for k, v in mouth_rate_data.items():
        v += [0, 0, 0, 0]
    if not sale:
        arrive = ArriveData.objects.filter(time__range=[dates[0], dates[-1]]).values('time', 'title')
    else:
        arrive = ArriveData.objects.filter(time__range=[dates[0], dates[-1]], consult=sale).values('time', 'title')
    for i in arrive:
        i_time = i['time'].strftime("%Y-%m-%d")
        if i['title'] == 2:
            mouth_rate_data[i_time][9] += 1
        elif i['title'] == 3:
            mouth_rate_data[i_time][11] += 1
        elif i['title'] == 4:
            mouth_rate_data[i_time][10] += 1
    for k, v in mouth_rate_data.items():
        v[8] = v[3]
        v.append(v[3]+v[7])
        v.append(0)
    if not sale:
        turnover = Turnover.objects.filter(time__range=[dates[0], dates[-1]]).values('turnover', 'time')
    else:
        turnover = Turnover.objects.filter(time__range=[dates[0], dates[-1]], consult=sale).values('turnover', 'time')
    for i in turnover:
        i_time = i['time'].strftime("%Y-%m-%d")
        mouth_rate_data[i_time][13] += Decimal(i['turnover']).quantize(Decimal('0.00'))
    hz = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for k, v in mouth_rate_data.items():
        hz = [i + j for i, j in zip(hz, v)]
    mouth_rate_data['汇总'] = hz
    for k, v in mouth_rate_data.items():
        mouth_rate_data[k] = mouth_rate_data[k] + ratio(v)
    return mouth_rate_data


def ratio(data):
    """月度转化率计算"""
    d = []
    try:
        data.append('{:.2%}'.format(data[1]/data[0]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[2]/data[0]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[2]/data[1]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[3]/data[0]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[5]/data[4]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[6]/data[4]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[6]/data[5]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format(data[7]/data[4]))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format((data[1]+(data[5]))/(data[0]+data[4])))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format((data[2]+(data[6]))/(data[0]+data[4])))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format((data[2]+(data[6]))/(data[1]+data[5])))
    except ZeroDivisionError:
        data.append(0)
    try:
        data.append('{:.2%}'.format((data[3]+(data[7]))/(data[0]+data[4])))
    except ZeroDivisionError:
        data.append(0)
    return d


def all_no_consult(request):
    """全部未咨询表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 9:
        data = get_all_no_consult()
        return render(request, 'base_form.html', data)
    else:
        return redirect('/index/')


def get_all_no_consult():
    """获取全部未咨询表单"""
    user = User.objects.filter(user_limit=1).values()
    user = {i['id']: i['user_name'] for i in user}
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    form = Form.objects.filter(active=None).values('channel', 'title', 'active', 'id',
                                                   'phone', 'consult', 'distribute_time')
    data = {'form': []}
    for i in form:
        try:
            i['name'] = user[i['consult']]
        except KeyError:
            i['name'] = '未分配'
        i['channel'] = channel[i['channel']]
        i['active'] = '未咨询'
        data['form'].append(i)
    return data


def all_no_line(request):
    """全部未联系"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 9:
        data, sale_no_line_num = get_all_no_line()
        sale_no_line_num = sorted(sale_no_line_num.items(), key=lambda x: x[1], reverse=True)
        sale_no_line_num = collections.OrderedDict(sale_no_line_num)
        return render(request, 'base_form.html', {'form': data['form'], 'sale_no_line_num': sale_no_line_num})
    else:
        return redirect('/index/')


def get_all_no_line():
    """获取全部未联系表单"""
    user = User.objects.filter(user_limit=1).values()
    user = {i['id']: i['user_name'] for i in user}
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    form = Form.objects.filter(active=16).values('channel', 'id',
                                                 'phone', 'consult', 'distribute_time')
    sale_no_line_num = {}
    data = {'form': []}
    for i in form:
        i['name'] = user[i['consult']]
        i['channel'] = channel[i['channel']]
        i['active'] = '未联系上'
        data['form'].append(i)
        if i['name'] in sale_no_line_num.keys():
            sale_no_line_num[i['name']] += 1
        else:
            sale_no_line_num[i['name']] = 1
    return data, sale_no_line_num


def sale_week_rate():
    """个人周转化率"""
    t = datetime.date.today()
    start = t - datetime.timedelta(days=t.weekday() + 7)
    end = t - datetime.timedelta(days=t.weekday() + 1)
    # start = '2020-10-26'
    # end = '2020-11-01'
    users = User.objects.filter(user_limit=1, status=1).values()
    users = {i['id']: i['user_name'] for i in users}
    channel = Channel.objects.filter(channel_main=7).values('id')
    channel = [i['id'] for i in channel]
    data = {}
    for k, v in users.items():
        data[v] = [0, 0, 0, 0]
        form = Form.objects.filter(consult=k, distribute_time__range=[start, end]).values('channel', 'active')
        for i in form:
            if i['channel'] in channel:
                pass
            else:
                data[v][0] += 1
            if i['active'] == 1:
                data[v][1] += 1
            else:
                pass
        swt_form = SwtWork.objects.filter(sale=k, time__range=[start, end], swt_xm__gte=3).aggregate(
            nums=Sum('swt_phone_or_tm'))['nums']
        if not swt_form:
            swt_form = 0
        data[v][0] += swt_form
        swt_active_form = SwtWork.objects.filter(sale=k, time__range=[start, end], swt_xm__gte=3).aggregate(
            nums=Sum('swt_active_phone_or_xxm'))['nums']
        if not swt_active_form:
            swt_active_form = 0
        data[v][1] += swt_active_form
        '''
        info_arrive = InfoWork.objects.filter(sale=k, time__range=[start, end]).aggregate(
            nums=Sum('arrive'))['nums']
        '''
        info_arrive = ArriveData.objects.filter(consult=k, time__range=[start, end]).count()
        if not info_arrive:
            info_arrive = 0
        data[v][2] = info_arrive
        '''
        swt_work = SwtWork.objects.filter(sale=k, time__range=[start, end], swt_xm=2).aggregate(
            zz=Sum('swt_form_or_zz'), jz=Sum('swt_active_form_or_jz'),
            tm=Sum('swt_phone_or_tm'), xxm=Sum('swt_active_phone_or_xxm')
        )
        for m, n in swt_work.items():
            if not n:
                data[v][2] += 0
            else:
                data[v][2] += n
        '''
    for k, v in data.items():
        if v[0] == 0:
            pass
        else:
            v[3] = '{:.2%}'.format(v[2]/v[0])
    re_data = {}
    # for k in sorted(data_arrive, key=lambda i: i, reverse=False):
    for k in sorted(data, key=lambda i: float(str(data[i][-1]).strip('%')), reverse=True):
        re_data[k] = data[k]
    return re_data


def show_today_form(request):
    """展示当日分配表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 9:
        t = today()
        consult = User.objects.filter(user_limit=1).values()
        consult = {i['id']: i['user_name'] for i in consult}
        active = Active.objects.all().values('title', 'active')
        active = {i['title']: i['active'] for i in active}
        channel = Channel.objects.all().values('id', 'name')
        channel = {i['id']: i['name'] for i in channel}
        form = Form.objects.filter(distribute_time=t).values('phone', 'active', 'consult', 'title', 'channel')
        for i in form:
            i['channel'] = channel[i['channel']]
            if i['consult']:
                i['name'] = consult[i['consult']]
            else:
                i['name'] = '未分配'
            if i['active']:
                i['active'] = active[i['active']]
        return render(request, 'base_form.html', {'form': form})
    else:
        return redirect('/index/')


def show_sale_form(request):
    """按咨询人展示表单"""
    pass
