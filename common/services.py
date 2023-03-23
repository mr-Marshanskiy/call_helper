import datetime


def get_schedule_time_title(start, end, first_col='', interval=15):
    now = datetime.datetime.now().date()
    start_datetime = datetime.datetime.combine(now, start)
    end_datetime = datetime.datetime.combine(now, end)

    result = [
        {'value': first_col, 'color': '#fff'},
        {'value': '', 'color': '#fff'}
    ]
    while start_datetime < end_datetime:
        result.append(
            {'value': start_datetime.strftime('%H:%M'), 'color': '#fff'}
        )
        start_datetime += datetime.timedelta(minutes=interval)

    return result


def convert_timedelta_to_str_time(delta):
    hours = delta.seconds // 3600
    minutes = delta.seconds // 60 % 60
    return f'{hours} ч. {minutes // 10}{minutes % 10} мин.'
