from django import template


register = template.Library()


@register.filter()
def get_date_info(data, date):
    return data[date]


@register.filter()
def get_channel_info(channel, data):
    return data[channel]


@register.filter()
def get_date_swt(data, date):
    return data[date]


@register.filter()
def get_xm_swt(xm, data):
    return data[xm]
