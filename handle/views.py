from django.shortcuts import render, redirect
from up_load.views import today, get_form_quality_data, calculate_form_quality_rate, request_class
from up_load.models import Form, Channel
from login.views import is_login
from charts.views import form_quality_bar


def handle(request):
    """管理详情页"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    if request.session.get('user_limit') >= 2:
        pass
    else:
        return redirect('/index/')
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
    return render(request, 'handle/form_quality.html', {'form_quality_data': form_quality_data,
                                                        'no_distribute': no_distribute,
                                                        'no_consult': no_consult,
                                                        'up_num_today': up_num_today,
                                                        'form_quality_rate': form_quality_rate,
                                                        'channel': channel,
                                                        't': str(start) + '至' + str(end),
                                                        't_': str(start) + '&' + str(end) + '&' + str(time_class) + '&',
                                                        'form_quality_bar_': form_quality_bar_
                                                        })

