import requests
import json
import redis
from .models import DoctorType
from django.shortcuts import render, redirect, render_to_response, HttpResponse
from up_load.models import Channel, Form
from login.models import User
from consult.models import Active
from consult.views import get_consult_form
from distribute.views import distribute_data, get_form, complete_rate, active_rate, get_sale_turnover
from up_load.views import get_up_data
from handle.models import Turnover, ArriveData, OrderData
from login.views import is_login


def longqi(request):
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') == 11:
        pass
    else:
        return redirect('/index/')
    re_data = distribute_data()
    re_data['form_data'] = get_form()
    re_data['complete_rate'] = complete_rate(re_data)
    re_data['active_rate'] = active_rate(re_data)
    re_data['turnover'] = get_sale_turnover(request)
    return render(request, 'longqi/longqi.html', re_data)


def get_yky_cookie():
    r = redis.Redis(host='192.168.0.214',
                    port=6379,
                    db=0,
                    decode_responses=True)
    return r.get('yky_cookie')


def search_phone(request):
    if is_login(request):
        return render(request, 'search_phone.html')


def get_phone_result(request):
    """通过手机号查询咨询就诊记录"""
    # 获取手机号
    phone = request.POST.lists()
    phone = dict((x, y) for x, y in phone)
    phone = phone['phone'][0]
    # 构造请求headers
    cookie = get_yky_cookie()
    headers = {
        'authorization': cookie,
        'authority': 'api.linkedcare.cn:9001',
        'origin': 'https://bjygjkq.linkedcare.cn',
        'host': 'prd9.easyliao.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'referer': 'https://bjygjkq.linkedcare.cn/ares3/'
    }
    phone_id = get_phone_id(phone, headers)
    jz = get_end_jz(phone_id, headers)
    zx = get_end_zx(phone_id, headers)
    return render(request, 'search_phone.html', {'jz': jz, 'zx': zx})


def get_phone_id(phone, headers):
    """通过手机号查询此患者id"""
    url = 'https://api.linkedcare.cn:9001/api/v1' \
          '/patients?isBusyRequest=false&isExactMatchSelected=false&pageIndex=1&pageSize=10' \
          '&searchString={}'.format(phone)
    rep = requests.get(url, headers=headers)
    rep = json.loads(rep.text)
    try:
        # phone_id = rep['items'][0]['id']
        count = int(rep['totalCount'])
        if count >= 1:
            return True
        else:
            return False
    except IndexError:
        return False


def get_end_jz(phone_id, headers):
    url = 'https://api.linkedcare.cn:9001/api/v1/appointment-record/patient/{}'.format(phone_id)
    rep = requests.get(url, headers=headers)
    rep = json.loads(rep.text)
    if not rep:
        return {'就诊查询结果': '无就诊记录'}
    else:
        end_time = rep[0]['endTime'].split('T')[0]
        in_type = rep[0]['checkInType']
        xm = rep[0]['procedures'][0]['transaction']['name']
        sale = rep[0]['recordCreatedUserName']
        return {'最后就诊日期': end_time, '就诊类型': in_type, '就诊项目': xm, '咨询人': sale}


def get_end_zx(phone_id, headers):
    url = 'https://api.linkedcare.cn:9001/api/v1/online-consult/patient/{}' \
          '?canShowOfflineConsultData=true'.format(phone_id)
    rep = requests.get(url, headers=headers)
    rep = json.loads(rep.text)
    if not rep:
        return {'咨询查询结果': '无咨询记录'}
    else:
        end_time = rep[0]['recordCreatedTime'].split('T')[0]
        xm = rep[0]['consultItems']
        sale = rep[0]['recordCreatedUserName']
        return {'最后咨询日期': end_time, '咨询项目': xm, '咨询人': sale}


def search_phone_local(request):
    """手机号查询"""
    # 状态判断
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 2:
        pass
    else:
        return redirect('/index/')
    data = request.POST.lists()
    data = dict((x, y) for x, y in data)
    phone = data['phone'][0]
    # 渠道集合
    channel = Channel.objects.all().values()
    channel = {i['id']: i['name'] for i in channel}
    # 咨询人集合
    consultant = User.objects.filter(user_limit=1).values()
    consultant = {i['id']: i['user_name'] for i in consultant}
    # 有效集合
    active = Active.objects.all().values()
    active = {i['title']: i['active'] for i in active}
    # 查询
    form = Form.objects.filter(phone=phone).values('channel', 'id',
                                                   'consult',
                                                   'phone',
                                                   'active',
                                                   'distribute_time')
    for i in form:
        i['channel'] = channel[i['channel']]
        try:
            i['name'] = consultant[i['consult']]
        except:
            i['name'] = None
        if i['active']:
            i['active'] = active[i['active']]
    return render(request, 'base_form.html', {'form': form})


def check_phone_reload(request):
    sale = request.session.get('user_id')
    data = get_consult_form(sale)
    cookie = get_yky_cookie()
    headers = {
        'authorization': cookie,
        'authority': 'api.linkedcare.cn:9001',
        'origin': 'https://bjygjkq.linkedcare.cn',
        'host': 'prd9.easyliao.com',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/'
                      '537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        'referer': 'https://bjygjkq.linkedcare.cn/ares3/'
    }
    for i in data['form']:
        phone = i['phone']
        if get_phone_id(phone, headers):
            i['check'] = '已录'
        else:
            i['check'] = '未录'
    return render(request, 'consult/consult.html', data)


def up_turnover_page(request):
    return render(request, 'longqi/up_turnover.html')


def up_arrive_page(request):
    return render(request, 'longqi/up_arrive.html')


def up_order_page(request):
    return render(request, 'longqi/up_order.html')


def up_turnover_data(request):
    """上传数据"""
    # 状态判断
    if request.session.get('is_login', None):
        pass
    else:
        raise ValueError
    if request.method == "POST":
        # 渠道集合
        channel = Channel.objects.all().values()
        channel = {i['name']: i['id'] for i in channel}
        # 收费项目判定依据
        doctor_type = DoctorType.objects.all().values()
        doctor_type = {i['id']: i['doctor_type'].split(',') for i in doctor_type}
        # 人员
        consult = User.objects.filter(user_limit=1).values()
        consult = {i['user_name']: i['id'] for i in consult}
        # 处理数据
        for file in get_up_data(request.FILES):
            data = handle_up_turnover(file)
            data = reload_up_turnover(data, channel, doctor_type, consult)
            insert_up_turnover(data)
        return HttpResponse(1)
    return render_to_response('longqi/up_turnover.html')


def up_arrive_data(request):
    """上传数据"""
    # 状态判断
    if request.session.get('is_login', None):
        pass
    else:
        raise ValueError
    if request.method == "POST":
        # 渠道集合
        channel = Channel.objects.all().values()
        channel = {i['name']: i['id'] for i in channel}
        # 人员
        consult = User.objects.filter(user_limit=1).values()
        consult = {i['user_name']: i['id'] for i in consult}
        # 处理数据
        for file in get_up_data(request.FILES):
            data = handle_up_arrive(file)
            data = reload_up_arrive(data, channel, consult)
            insert_up_arrive(data)
        return HttpResponse(1)
    return render_to_response('longqi/up_arrive.html')


def up_order_data(request):
    """上传数据"""
    # 状态判断
    if request.session.get('is_login', None):
        pass
    else:
        raise ValueError
    if request.method == "POST":
        # 渠道集合
        channel = Channel.objects.all().values()
        channel = {i['name']: i['id'] for i in channel}
        # 人员
        consult = User.objects.filter(user_limit=1).values()
        consult = {i['user_name']: i['id'] for i in consult}
        # 处理数据
        for file in get_up_data(request.FILES):
            data = handle_up_order(file)
            data = reload_up_order(data, channel, consult)
            insert_up_order(data)
        return HttpResponse(1)
    return render_to_response('longqi/up_order.html')


def handle_up_turnover(file):
    """处理上传数据，列表化，去除空值"""
    if '\r\n' in file:
        data = file.split('\r\n')
    elif '\n' in file:
        data = file.split('\n')
    else:
        # 无换行符号匹配，主动清空数据。抛出错误
        data = ''
    if '手机' in data[0]:
        data = data[1:]
    else:
        pass
    data = map(lambda i: i.split('\t'), data)
    data = list(data)
    data = [i for i in data if i != ['']]
    data = [i for i in data if i[0] != '']
    data = [i for i in data if '废' not in i[6]]
    data = [i for i in data if 0 != float(i[-1])]
    # data = [i[2].replace('【广告1部】', '').replace('（表单）', '') for i in data]
    # data = map(lambda i: i[2].replace('【广告1部】', '').replace('（表单）', ''), data)
    for i in data:
        i[3] = i[3].replace('【广告1部】', '')\
            .replace('（表单）', '')\
            .replace('来电', '')
        i[9] = i[9].replace(',', '').replace('，', '')
        i[10] = i[10].replace(',', '').replace('，', '')
        if 'uc' in i[3] or 'UC' in i[3]:
            i[3] = '视频转诊'
        if '支付宝' in i[3]:
            i[3] = '支付宝'
    return data


def handle_up_arrive(file):
    """处理上传数据，列表化，去除空值"""
    if '\r\n' in file:
        data = file.split('\r\n')
    elif '\n' in file:
        data = file.split('\n')
    else:
        # 无换行符号匹配，主动清空数据。抛出错误
        data = ''
    if '手机' in data[0]:
        data = data[1:]
    else:
        pass
    data = map(lambda i: i.split('\t'), data)
    data = list(data)
    data = [i for i in data if i != ['']]
    data = [i for i in data if i[0] != '']
    for i in data:
        i[1] = i[1].replace('【广告1部】', '')\
            .replace('（表单）', '')\
            .replace('来电', '')
        if 'uc' in i[1] or 'UC' in i[1]:
            i[1] = '视频转诊'
        if '支付宝' in i[1]:
            i[1] = '支付宝'
    return data


def handle_up_order(file):
    """处理上传数据，列表化，去除空值"""
    if '\r\n' in file:
        data = file.split('\r\n')
    elif '\n' in file:
        data = file.split('\n')
    else:
        # 无换行符号匹配，主动清空数据。抛出错误
        data = ''
    if '手机' in data[0]:
        data = data[1:]
    else:
        pass
    data = map(lambda i: i.split('\t'), data)
    data = list(data)
    data = [i for i in data if i != ['']]
    data = [i for i in data if i[0] != '']
    for i in data:
        i[1] = i[1].replace('【广告1部】', '')\
            .replace('（表单）', '')\
            .replace('来电', '')
        if 'uc' in i[1] or 'UC' in i[1]:
            i[1] = '视频转诊'
        if '支付宝' in i[1]:
            i[1] = '支付宝'
    return data


def reload_up_turnover(data, channel, doctor_type, consult):
    """重构上传数据"""
    # 更换渠道name为id，构造时间格式
    for i in data:
        if i[3] in channel:
            i[3] = channel[i[3]]
        else:
            i[3] = 999
        i[7] = i[7].replace('/', '-').replace('年', '-').replace('月', '-').replace('日', '').split(' ')[0]
        if i[2] in consult:
            i[2] = consult[i[2]]
        else:
            i[2] = consult['无名']
    # 判断种植/矫正
    for i in data:
        data_class = i[8] + i[9] + i[10]
        i[10] = check_doctor_type(i, data_class, doctor_type)
    data = [[i[1], i[2], i[3], i[7], i[10], i[11]] for i in data]
    return data


def reload_up_arrive(data, channel, consult):
    """重构上传数据"""
    # 更换渠道name为id，构造时间格式
    for i in data:
        if i[1] in channel:
            i[1] = channel[i[1]]
        else:
            i[1] = 999
        if i[8] in consult:
            i[8] = consult[i[8]]
        else:
            i[8] = consult['无名']
        i[0] = i[0].replace('/', '-').replace('年', '-').replace('月', '-').replace('日', '')
    # 判断种植/矫正
    for i in data:
        if '全科' in i[3]:
            i[3] = 4
        elif '正畸' in i[3]:
            i[3] = 2
        elif '洁牙' in i[3]:
            i[3] = 3
        else:
            i[3] = 1
    data = [[i[0], i[1], i[3], i[6], i[8]] for i in data]
    return data


def reload_up_order(data, channel, consult):
    """重构上传数据"""
    # 更换渠道name为id，构造时间格式
    for i in data:
        if i[1] in channel:
            i[1] = channel[i[1]]
        else:
            i[1] = 999
        if i[6] in consult:
            i[6] = consult[i[6]]
        else:
            i[6] = consult['无名']
        i[0] = i[0].replace('/', '-').replace('年', '-').replace('月', '-').replace('日', '')
    # 判断种植/矫正
    for i in data:
        if '种植' in i[3]:
            i[3] = 1
        elif '矫正' in i[3]:
            i[3] = 2
        elif '洗牙' in i[3] or '洁牙' in i[3]:
            i[3] = 3
        else:
            i[3] = 4
    data = [[i[0], i[1], i[3], i[5], i[6]] for i in data]
    return data


def check_doctor_type(i, data_class, doctor_type):
    """判断就医项目"""
    for x in doctor_type[1]:
        if x in data_class:
            return 1
    for x in doctor_type[2]:
        if x in data_class:
            return 2
    for x in doctor_type[3]:
        if x in data_class and float(i[-1]) <= 200:
            return 3
    return 4


def insert_up_turnover(data):
    """插入数据库"""
    up_data_insert = []
    for i in data:
        up_data_insert.append(
            Turnover(phone=int(i[0]),
                     turnover=str(i[5]),
                     channel_main=i[2],
                     consult=i[1],
                     title=i[4],
                     time=i[3],
                     ))
    Turnover.objects.bulk_create(up_data_insert)


def insert_up_arrive(data):
    """插入数据库"""
    up_data_insert = []
    for i in data:
        up_data_insert.append(
            ArriveData(phone=int(i[3]),
                       channel_main=i[1],
                       consult=i[4],
                       title=i[2],
                       time=i[0],
                       ))
    ArriveData.objects.bulk_create(up_data_insert)


def insert_up_order(data):
    """插入数据库"""
    up_data_insert = []
    for i in data:
        up_data_insert.append(
            OrderData(phone=int(i[3]),
                      channel_main=i[1],
                      consult=i[4],
                      title=i[2],
                      time=i[0],
                      ))
    OrderData.objects.bulk_create(up_data_insert)










