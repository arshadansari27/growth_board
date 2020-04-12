from collections import defaultdict
from datetime import datetime
from typing import Callable, Any, Dict, Union, List
import pandas as pd
import numpy as np
from core.models.objectives import Frequency, FREQUENCY_DAILY, FREQUENCY_WEEKLY, \
    FREQUENCY_MONTHLY, PROGRESS_TYPE_VALUE, PROGRESS_TYPE_BOOLEAN


def count_progress(done_dates, progress_type: str, freqency: Frequency):

    if freqency.type == FREQUENCY_DAILY:
        grouped = group_daily(done_dates)
    elif freqency.type == FREQUENCY_WEEKLY:
        grouped = group_weekly(done_dates)
    elif freqency.type == FREQUENCY_MONTHLY:
        grouped = group_monthly(done_dates)
    else:
        raise NotImplementedError
    return average_out(grouped, progress_type, freqency.max_count)


def count_boolean(value, count):
    return float(sum(1 if i else 0 for i in value)) / count


def count_value(value, count):
    return float(sum(v for v in value)) / count


def group_daily(done_dates):
    return {u.strftime('%Y%m%d'): [v] for u, v in done_dates.items()}


def group_weekly(done_dates):
    df = pd.DataFrame({'dates': list(done_dates.keys()), 'count': list(
            done_dates.values())})
    df['weeks'] = df['dates'].dt.year.astype(str) + "-" + df[
        'dates'].dt.week.astype(str)
    by_weekly = defaultdict(list)
    for i, row in df.iterrows():
        r = row.to_dict()
        by_weekly[r['weeks']].append(r['count'])
    return by_weekly


def group_monthly(done_dates):
    def monthly_hash(d):
        return f"{d.year}-{d.month}"
    by_monthly = defaultdict(list)
    for d, v in done_dates.items():
        by_monthly[monthly_hash(d)].append(v)
    return by_monthly


def average_out(grouped: Dict[str, List[Union[bool, int]]],
                progress_type: str, count: int):
    if progress_type == PROGRESS_TYPE_VALUE:
        count_func = count_value
    elif progress_type == PROGRESS_TYPE_BOOLEAN:
        count_func = count_boolean
    else:
        raise NotImplementedError
    return sum([
        count_func(v, count) for _, v in grouped.items()
    ]) / float(len(grouped))


