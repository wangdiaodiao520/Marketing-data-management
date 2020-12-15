from django.shortcuts import render, redirect, render_to_response
from pyecharts.charts import Pie, Bar, Line
from decimal import Decimal
from pyecharts import options as opts
from handle.models import Turnover, ArriveData, OrderData
from distribute.views import get_dates
from up_load.models import Channel
from login.models import User
from login.views import is_login


def get_charts(request):
    """数据可视化"""
    if is_login(request):
        pass
    else:
        return redirect('/login/')
    # if request.session.get('user_limit') >= 9:
    channels_ = Channel.objects.all().values()
    channels = dict()
    for i in channels_:
        if i['channel_main'] in channels:
            pass
        else:
            channels[i['channel_main']] = i['name']
    consult = User.objects.filter(user_limit=1).values()
    consult = {i['id']: i['user_name'] for i in consult}
    dates, sale, channel = get_condition(request)
    # dates = ['2020-10-01', '2020-10-31']
    turnover, arrive, order = get_data(dates, sale, channel)
    chart = dict()
    chart['channels'] = channels
    chart['consult'] = consult
    try:
        chart['turnover_time_bar'] = get_turnover_time_bar(turnover).render_embed()
    except AttributeError:
        pass
    try:
        chart['arrive_order_time_line'] = get_arrive_order_time_line(arrive, order).render_embed()
    except AttributeError:
        pass
    if not channel:
        try:
            chart['turnover_channel_pie'] = get_turnover_channel_pie(turnover, channels).render_embed()
        except AttributeError:
            pass
    if not sale:
        try:
            chart['turnover_sale_pie'] = get_turnover_sale_pie(turnover, consult).render_embed()
        except AttributeError:
            pass
        try:
            chart['arrive_sale_pie'] = get_arrive_sale_pie(arrive, consult).render_embed()
        except AttributeError:
            pass
        try:
            chart['order_sale_pie'] = get_order_sale_pie(order, consult).render_embed()
        except AttributeError:
            pass
    return render(request, 'base_chart.html', chart)


def get_condition(request):
    """解析请求类型和条件"""
    if request.method == 'GET':
        dates = get_dates()
        dates = [dates[0], dates[-1]]
        limit = request.session.get('user_limit')
        if limit == 1:
            sale = request.session.get('user_id')
        else:
            sale = None
        channel = None
    else:
        data = request.POST.lists()
        data = dict((x, y) for x, y in data)
        start = data['start'][0]
        end = data['end'][0]
        if not start:
            start = end
        if not end:
            end = start
        if not start and not end:
            dates = get_dates()
            start = dates[0]
            end = dates[-1]
        dates = [start, end]
        sale = data['sale'][0]
        if not sale:
            sale = None
        if sale == '2':
            sale = None
        channel = data['channel'][0]
        if not channel:
            channel = None
    return dates, sale, channel


def get_data(dates, sale, channel):
    """提取数据库"""
    if sale is not None and channel is not None:
        turnover = Turnover.objects.filter(time__range=dates, consult=sale, channel_main=channel).values(
            'time', 'turnover', 'title')
        arrive = ArriveData.objects.filter(time__range=dates, consult=sale, channel_main=channel).values(
            'time', 'title')
        order = OrderData.objects.filter(time__range=dates, consult=sale, channel_main=channel).values(
            'time', 'title')
    elif sale is not None and channel is None:
        turnover = Turnover.objects.filter(time__range=dates, consult=sale).values(
            'time', 'turnover', 'title', 'channel_main')
        arrive = ArriveData.objects.filter(time__range=dates, consult=sale,).values(
            'time', 'title')
        order = OrderData.objects.filter(time__range=dates, consult=sale).values(
            'time', 'title')
    elif sale is None and channel is not None:
        turnover = Turnover.objects.filter(time__range=dates, channel_main=channel).values(
            'time', 'turnover', 'title', 'consult')
        arrive = ArriveData.objects.filter(time__range=dates, channel_main=channel).values(
            'time', 'title', 'consult')
        order = OrderData.objects.filter(time__range=dates, channel_main=channel).values(
            'time', 'title', 'consult')
    elif sale is None and channel is None:
        turnover = Turnover.objects.filter(time__range=dates).values(
            'time', 'turnover', 'title', 'consult', 'channel_main')
        arrive = ArriveData.objects.filter(time__range=dates).values(
            'time', 'title', 'consult')
        order = OrderData.objects.filter(time__range=dates).values(
            'time', 'title', 'consult')
    else:
        turnover = []
        arrive = []
        order = []
    return turnover, arrive, order


def get_turnover_time_bar(turnover):
    """营业额-日期-柱形图"""
    data = {}
    atr = []
    val = []
    for i in turnover:
        i_time = i['time'].strftime("%m-%d")
        if i_time in data:
            pass
        else:
            data[i_time] = 0
        data[i_time] += Decimal(i['turnover']).quantize(Decimal('0.00'))
    if not data:
        return
    for k in sorted(data, key=lambda i: i, reverse=False):
        atr.append(k)
        val.append(data[k])
    bar = (
        Bar(init_opts=opts.InitOpts(height='300px', width='100%'))
        .add_xaxis(atr)
        .add_yaxis('营业额', val)
        .set_global_opts(title_opts=opts.TitleOpts(title='营业额-日期-柱形图', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                                                                                  'background_color': '#fff'},
                                                                              "dataZoom": {"yAxisIndex": "none"},
                                                                              "restore": {},
                                                                              "magicType": {
                                                                                  "show": True, "type": ["line", "bar"]},
                                                                              "dataView": {}}),
                         # datazoom_opts=opts.DataZoomOpts(is_show=True),
                         legend_opts=opts.LegendOpts(is_show=False, pos_top='30px', pos_bottom='100px')
                         # visualmap_opts=opts.VisualMapOpts(is_show=True)
                         )
    )
    return bar


def get_arrive_order_time_line(arrive, order):
    """到院-日期-折线图"""
    data_arrive = {}
    atr_arrive = []
    val_arrive = []
    for i in arrive:
        i_time = i['time'].strftime("%m-%d")
        if i_time in data_arrive:
            pass
        else:
            data_arrive[i_time] = 0
        data_arrive[i_time] += 1
    for k in sorted(data_arrive, key=lambda i: i, reverse=False):
        atr_arrive.append(k)
        val_arrive.append(data_arrive[k])
    data_order = {}
    val_order = []
    for i in order:
        i_time = i['time'].strftime("%m-%d")
        if i_time in data_order:
            pass
        else:
            data_order[i_time] = 0
        data_order[i_time] += 1
    for k in sorted(data_order, key=lambda i: i, reverse=False):
        val_order.append(data_order[k])
    line_arrive_order = (
        Line(init_opts=opts.InitOpts(height='300px', width='100%'))
        .add_xaxis(atr_arrive)
        .add_yaxis('到院量', val_arrive)
        .add_yaxis('预约量', val_order)
        .set_global_opts(title_opts=opts.TitleOpts(title='到院&预约-日期-折线图', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                             'background_color': '#fff'},
                             "dataZoom": {"yAxisIndex": "none"},
                             "restore": {},
                             "magicType": {
                                 "show": True, "type": ["line", "bar"]},
                             "dataView": {}}),
                         # datazoom_opts=opts.DataZoomOpts(is_show=True),
                         legend_opts=opts.LegendOpts(pos_top='30px', pos_bottom='100px')
                         )
    )
    return line_arrive_order


def get_turnover_channel_pie(turnover, channels):
    """营业额-渠道-饼图"""
    data = {}
    data_ = []
    atr = []
    for i in turnover:
        if i['channel_main'] in data:
            pass
        else:
            data[i['channel_main']] = 0
        data[i['channel_main']] += Decimal(i['turnover']).quantize(Decimal('0.00'))
    if not data:
        return
    for k in sorted(data, key=lambda i: data[i], reverse=True):
        if k == 999:
            atr.append('易聊')
            data_.append(('易聊', data[k]))
        else:
            atr.append(channels[k])
            data_.append((channels[k], data[k]))
    pie = (
        Pie(init_opts=opts.InitOpts(height='500px', width='100%'))
        .add(series_name=str(atr), data_pair=data_)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_global_opts(title_opts=opts.TitleOpts(title='营业额-渠道-饼图\n', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                             'background_color': '#fff'},
                             "dataZoom": {"yAxisIndex": "none"},
                             "restore": {},
                             "magicType": {
                                 "show": True, "type": ["line", "bar"]},
                             "dataView": {}}),
                         legend_opts=opts.LegendOpts(pos_top='25%', pos_right='20%', orient='vertical')
                         )
    )
    return pie


def get_turnover_sale_pie(turnover, consult):
    """营业额-人员-饼图"""
    data = {}
    data_ = []
    atr = []
    for i in turnover:
        if i['consult'] in data:
            pass
        else:
            data[i['consult']] = 0
        data[i['consult']] += Decimal(i['turnover']).quantize(Decimal('0.00'))
    if not data:
        return
    for k in sorted(data, key=lambda i: data[i], reverse=True):
        if int(data[k]) == 0:
            pass
        else:
            atr.append(consult[k])
            data_.append((consult[k], data[k]))
    pie = (
        Pie(init_opts=opts.InitOpts(height='500px', width='100%'))
        .add(series_name=str(atr), data_pair=data_)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_global_opts(title_opts=opts.TitleOpts(title='营业额-人员-饼图\n', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                             'background_color': '#fff'},
                             "dataZoom": {"yAxisIndex": "none"},
                             "restore": {},
                             "magicType": {
                                 "show": True, "type": ["line", "bar"]},
                             "dataView": {}}),
                         legend_opts=opts.LegendOpts(pos_top='25%', pos_right='20%', orient='vertical')
                         )
    )
    return pie


def get_arrive_sale_pie(arrive, consult):
    """到院-人员-饼图"""
    data = {}
    data_ = []
    atr = []
    for i in arrive:
        if i['consult'] in data:
            pass
        else:
            data[i['consult']] = 0
        data[i['consult']] += 1
    if not data:
        return
    for k in sorted(data, key=lambda i: data[i], reverse=True):
        atr.append(consult[k])
        data_.append((consult[k], data[k]))
    pie = (
        Pie(init_opts=opts.InitOpts(height='500px', width='100%'))
        .add(series_name=str(atr), data_pair=data_)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_global_opts(title_opts=opts.TitleOpts(title='到院-人员-饼图\n', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                             'background_color': '#fff'},
                             "dataZoom": {"yAxisIndex": "none"},
                             "restore": {},
                             "magicType": {
                                 "show": True, "type": ["line", "bar"]},
                             "dataView": {}}),
                         legend_opts=opts.LegendOpts(pos_top='25%', pos_right='20%', orient='vertical')
                         )
    )
    return pie


def get_order_sale_pie(order, consult):
    """预约-人员-饼图"""
    data = {}
    data_ = []
    atr = []
    for i in order:
        if i['consult'] in data:
            pass
        else:
            data[i['consult']] = 0
        data[i['consult']] += 1
    if not data:
        return
    for k in sorted(data, key=lambda i: data[i], reverse=True):
        atr.append(consult[k])
        data_.append((consult[k], data[k]))
    pie = (
        Pie(init_opts=opts.InitOpts(height='500px', width='100%'))
        .add(series_name=str(atr), data_pair=data_)
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
        .set_global_opts(title_opts=opts.TitleOpts(title='预约-人员-饼图\n', pos_left='center'),
                         toolbox_opts=opts.ToolboxOpts(is_show=True, feature={"saveAsImage": {
                             'background_color': '#fff'},
                             "dataZoom": {"yAxisIndex": "none"},
                             "restore": {},
                             "magicType": {
                                 "show": True, "type": ["line", "bar"]},
                             "dataView": {}}),
                         legend_opts=opts.LegendOpts(pos_top='25%', pos_right='20%', orient='vertical')
                         )
    )
    return pie


def form_quality_bar(form_quality_data):
    """表单质量堆叠图"""
    channels = []
    data_1 = []
    data_2 = []
    data_3 = []
    data_4 = []
    data_5 = []
    for k, v in form_quality_data.items():
        channels.append(k)
        data_1.append(v[3])
        data_2.append(v[4]+v[5]+v[6])
        data_3.append(v[7]+v[8])
        data_4.append(v[9])
        data_5.append(v[0]-v[2])
    bar = (
        Bar(init_opts=opts.InitOpts(height='1000px', width='100%'))
        .add_xaxis(channels)
        .add_yaxis('有效', data_1, stack='stack1', category_gap='50%')
        .add_yaxis('无效', data_2, stack='stack1', category_gap='50%')
        .add_yaxis('重复', data_3, stack='stack1', category_gap='50%')
        .add_yaxis('未联系上', data_4, stack='stack1', category_gap='50%')
        .add_yaxis('未咨询', data_5, stack='stack1', category_gap='50%')
        .set_series_opts(label_opts=opts.LabelOpts(is_show=True, position='right', formatter='{a}-{c}'))
        .set_global_opts(title_opts=opts.TitleOpts(title='表单质量堆叠图'),
                         xaxis_opts=opts.AxisOpts(name='渠道', axislabel_opts={"rotate": 45}),
                         yaxis_opts=opts.AxisOpts(name='表单个数'),
                         # datazoom_opts=opts.DataZoomOpts(orient="vertical", range_start=0, range_end=100),
                         datazoom_opts=opts.DataZoomOpts(orient="vertical", range_start=0, range_end=100),
                         # visualmap_opts=opts.VisualMapOpts(is_show=True)
                         )
    )
    return bar




































