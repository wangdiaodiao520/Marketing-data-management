from django.shortcuts import render, redirect, render_to_response, HttpResponse
from django.db.models import Q
from .models import *
import datetime
import chardet
from login.views import is_login
from consult.models import Active
from login.models import User
from django.contrib import messages
from charts.views import form_quality_bar


def today():
    return datetime.date.today()


def up_load(request):
    """渠道主页入口"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') in [2, 10, 11]:
        return render(request, 'up_load/up_load.html')
    else:
        return redirect('/index/')


def up_data(request):
    """上传数据"""
    # 状态判断
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.method == "POST":
        # 渠道集合,上传人id，当日日期
        t = today()
        user_id = request.session['user_id']
        channel = Channel.objects.all().values()
        channel = {i['name']: i['id'] for i in channel}
        # 处理数据
        for file in get_up_data(request.FILES):
            data = handle_up_data(file)
            res = check_up_data(data, channel)
            if res:
                return HttpResponse(res)
            else:
                pass
            data = reload_up_data(data, channel)
            insert_up_data(data, user_id, t)
        return HttpResponse('success')
    return render_to_response('up_load/up_load.html')


def get_up_data(files):
    """获取上传文件，逐个取出,并判定编码"""
    for file in files:
        data = files.get(file).read()
        char = chardet.detect(data)['encoding']
        data = data.decode(char, 'ignore')
        yield data


def handle_up_data(file):
    """处理上传数据，列表化，去除空值"""
    if '\r\n' in file:
        data = file.split('\r\n')
    elif '\n' in file:
        data = file.split('\n')
    else:
        # 无换行符号匹配，主动清空数据。抛出错误
        data = ''
    if '姓名' == data[0]:
        data = data[1:]
    else:
        pass
    data = map(lambda i: i.split('\t'), data)
    data = list(data)
    data = [i for i in data if i != ['']]
    data = [i for i in data if i[1] != '']
    data = [i if len(i) == 6 else i + [''] for i in data]
    return data


def check_up_data(data, channel):
    """检查渠道，时间格式"""
    for i in data:
        if i[2] in channel:
            pass
        else:
            return i[1]
        if '/' in i[4] or '年' in i[4] or '-' in i[4]:
            pass
        else:
            return i[1]
        try:
            int(i[1])
        except ValueError:
            return i[1]
    return False


def reload_up_data(data, channel):
    """重构上传数据"""
    # 更换渠道name为id，构造时间格式
    for i in data:
        i[2] = channel[i[2]]
        i[4] = i[4].replace('/', '-').replace('年', '-').replace('月', '-').replace('日', '')
    # 判断种植/矫正
    for i in data:
        if '种' in i[3]:
            i[3] = 1
        else:
            i[3] = 2
    return data


def insert_up_data(data, user_id, t):
    """插入数据库"""
    up_data_insert = []
    for i in data:
        up_data_insert.append(
            Form(name=i[0],
                 phone=i[1],
                 channel=i[2],
                 title=i[3],
                 submit_time=i[4],
                 mark=i[5],
                 promoter=user_id,
                 up_time=t))
    Form.objects.bulk_create(up_data_insert)


def form_quality(request):
    """表单统计详情页"""
    # 状态判断
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 2:
        pass
    else:
        return redirect('/index/')
    # 根据请求类型，构造返回数据类型,post有开始时间、结束时间、时间类型、查询人
    time_class, start, end = request_class(request)
    user_limit = request.session.get('user_limit')
    if user_limit != 2:
        sale = None
        no_distribute = Form.objects.filter(consult=None).count()  # 未分配
        no_consult = Form.objects.filter(active=None).count()  # 未咨询
        up_num_today = Form.objects.filter(up_time=today()).count()  # 当日上传
    else:
        sale = request.session.get('user_id')
        no_distribute = Form.objects.filter(promoter=sale, consult=None).count()  # 未分配
        no_consult = Form.objects.filter(promoter=sale, active=None).count()  # 未咨询
        up_num_today = Form.objects.filter(promoter=sale, up_time=today()).count()  # 当日上传
    # 渠道集合
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    # 表单详情
    form_quality_data = get_form_quality_data(channel, start, end, sale, time_class)
    # 有效率
    form_quality_rate = calculate_form_quality_rate(form_quality_data)
    # 堆叠图
    form_quality_bar_ = form_quality_bar(form_quality_data).render_embed()
    return render(request, 'up_load/form_quality.html', {'form_quality_data': form_quality_data,
                                                         'no_distribute': no_distribute,
                                                         'no_consult': no_consult,
                                                         'up_num_today': up_num_today,
                                                         'form_quality_rate': form_quality_rate,
                                                         'channel': channel,
                                                         't': str(start) + '至' + str(end) + '&' + str(time_class),
                                                         't_': str(start) + '&' + str(end) + '&' + str(time_class) + '&',
                                                         'form_quality_bar_': form_quality_bar_
                                                         })


def get_form_quality_data(channel, start, end, sale, time_class):
    """获取查询数据"""
    re_data = {}
    # 判断时间类型
    if time_class:
        submit_time = [start, end]
        up_time = [datetime.date(2020, 1, 1), datetime.date(2099, 12, 31)]
    else:
        submit_time = [datetime.date(2020, 1, 1), datetime.date(2099, 12, 31)]
        up_time = [start, end]
    # 根据用户类型查询数据
    if sale:
        for k, v in channel.items():
            form_all = Form.objects.filter(promoter=sale, submit_time__range=submit_time, up_time__range=up_time,
                                           channel=k).count()
            if form_all:
                form_distribute = Form.objects.filter(~Q(consult=None), promoter=sale, channel=k,
                                                      submit_time__range=submit_time, up_time__range=up_time).count()
                form_consult = Form.objects.filter(~Q(active=None), promoter=sale, channel=k,
                                                   submit_time__range=submit_time, up_time__range=up_time).count()
                form_active = Form.objects.filter(promoter=sale, submit_time__range=submit_time, up_time__range=up_time,
                                                  channel=k, active=1).count()
                form_error = Form.objects.filter(promoter=sale, submit_time__range=submit_time, up_time__range=up_time,
                                                 channel=k, active=2).count()
                form_field = Form.objects.filter(promoter=sale, submit_time__range=submit_time, up_time__range=up_time,
                                                 channel=k, active=3).count()
                form_customer = Form.objects.filter(promoter=sale, submit_time__range=submit_time,
                                                    up_time__range=up_time, channel=k, active=4).count()
                form_re_we = Form.objects.filter(promoter=sale, submit_time__range=submit_time,
                                                 up_time__range=up_time, channel=k, active=10).count()
                form_re_other = Form.objects.filter(promoter=sale, submit_time__range=submit_time,
                                                    up_time__range=up_time, channel=k, active=11).count()
                form_no_line = Form.objects.filter(promoter=sale, submit_time__range=submit_time,
                                                   up_time__range=up_time, channel=k, active=16).count()
                re_data[v] = [
                        form_all, form_distribute, form_consult, form_active,
                        form_error, form_field, form_customer, form_re_we,
                        form_re_other, form_no_line
                        ]
    else:
        for k, v in channel.items():
            form_all = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                           channel=k).count()
            if form_all:
                form_distribute = Form.objects.filter(~Q(consult=None), channel=k,
                                                      submit_time__range=submit_time, up_time__range=up_time).count()
                form_consult = Form.objects.filter(~Q(active=None), channel=k,
                                                   submit_time__range=submit_time, up_time__range=up_time).count()
                form_active = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                  channel=k, active=1).count()
                form_error = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                 channel=k, active=2).count()
                form_field = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                 channel=k, active=3).count()
                form_customer = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                    channel=k, active=4).count()
                form_re_we = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                 channel=k, active=10).count()
                form_re_other = Form.objects.filter(submit_time__range=submit_time, up_time__range=up_time,
                                                    channel=k, active=11).count()
                form_no_line = Form.objects.filter(submit_time__range=submit_time,
                                                   up_time__range=up_time, channel=k, active=16).count()
                re_data[v] = [
                    form_all, form_distribute, form_consult, form_active,
                    form_error, form_field, form_customer, form_re_we,
                    form_re_other, form_no_line
                    ]
    if re_data:
        hz = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for k, v in re_data.items():
            if '支付宝' in k:
                pass
            else:
                hz = [i + j for i, j in zip(hz, v)]
        re_data['汇总(无支付宝)'] = hz
    return re_data


def calculate_form_quality_rate(data):
    """渠道有效率计算"""
    rate = {}
    for k, v in data.items():
        if v[3] != 0:
            rate[k] = '{:.2%}'.format(v[3]/v[2])
        else:
            rate[k] = 0
    return rate


def request_class(request):
    # 根据请求类型，构造返回数据类型,post有开始时间、结束时间、时间类型
    if request.method == "POST":
        post_data = request.POST.lists()
        post_data = dict((x, y) for x, y in post_data)
        time_class = int(post_data['time_class'][0])
        start = post_data['start'][0]
        end = post_data['end'][0]
        if not start:
            start = end
        if not end:
            end = start
    else:
        start = end = today()
        time_class = 1
    return time_class, start, end


def get_today_form(request):
    """展示当日上传表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 2:
        t = today()
        channel = Channel.objects.all().values('id', 'name')
        channel = {i['id']: i['name'] for i in channel}
        active = Active.objects.all().values('title', 'active')
        active = {i['title']: i['active'] for i in active}
        form = Form.objects.filter(up_time=t).values('id', 'phone', 'active', 'title', 'channel', 'submit_time')
        for i in form:
            i['channel'] = channel[i['channel']]
            if i['active']:
                i['active'] = active[i['active']]
            else:
                i['active'] = '未咨询'
        return render(request, 'base_form.html', {'form': form})
    else:
        return redirect('/index/')


def delete_form(request):
    if request.method == 'POST':
        data = request.POST.lists()
        data = dict((x, y) for x, y in data)
        active = data['active'][0]
        form_id = data['form_id'][0]
        if request.session.get('user_limit') == 2:
            Form.objects.filter(id=form_id).delete()
            messages.success(request, '表单已删除')
            return redirect('/get_today_form/')
        else:
            pass
    return redirect('/index/')


def get_actives_form(request, a, b, c, d):
    """获取有效性的表单"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 2:
        pass
    else:
        return redirect('/index/')
    arg = a + b + c + d
    channels = Channel.objects.all().values('id', 'name')
    channels_ = {i['name']: i['id'] for i in channels}
    channels = {i['id']: i['name'] for i in channels}
    user = User.objects.filter(user_limit=1).values()
    user = {i['id']: i['user_name'] for i in user}
    actives = Active.objects.all().values('title', 'active')
    actives = {i['title']: i['active'] for i in actives}
    arg = arg.split('&')
    start = arg[0]
    end = arg[1]
    time_class = arg[2]
    active = arg[3]
    active_ = actives[int(active)]
    channel = arg[4]
    channel = channels_[channel]
    data = {'form': []}
    if int(time_class):
        form = Form.objects.filter(submit_time__range=[start, end], active=active, channel=channel).values(
            'consult', 'phone', 'channel', 'submit_time', 'distribute_time')
        for i in form:
            i['channel'] = channels[i['channel']]
            i['name'] = user[i['consult']]
            i['active'] = active_
            data['form'].append(i)
    else:
        form = Form.objects.filter(up_time__range=[start, end], active=active, channel=channel).values(
             'consult', 'phone', 'channel', 'submit_time', 'distribute_time')
        for i in form:
            i['channel'] = channels[i['channel']]
            i['name'] = user[i['consult']]
            i['active'] = active_
            data['form'].append(i)
    return render(request, 'base_form.html', data)






















