import random
from datetime import datetime, timedelta

import pytest

from core.models.objectives import PROGRESS_TYPE_BOOLEAN, Frequency, \
    FREQUENCY_DAILY, FREQUENCY_WEEKLY
from core.models.specs import group_daily, group_monthly, group_weekly, \
    count_progress


@pytest.fixture(scope='module')
def dates():
    return [(datetime(2019, 1, 1) + timedelta(days=i)) for i in range(370)]


@pytest.fixture
def date_by_boolean(dates):
    return {
        u: True if random.randint(0, 2) >= 1 else False
        for u in dates
    }


@pytest.fixture
def date_by_value(dates):
    return {
        u: random.randint(1, 20) if random.random() > 0.5 else 0
        for u in dates
    }


def test_count_progress(date_by_boolean):
    val = count_progress(date_by_boolean, PROGRESS_TYPE_BOOLEAN,
                   Frequency(
                           FREQUENCY_DAILY, 1))
    assert  val > count_progress(
            date_by_boolean, PROGRESS_TYPE_BOOLEAN, Frequency(FREQUENCY_DAILY, 2))

    val = count_progress(date_by_boolean, PROGRESS_TYPE_BOOLEAN,
                         Frequency(
                                 FREQUENCY_WEEKLY, 3))
    assert val > 1


def test_boolean_daily_grouping(date_by_boolean):
    assert len(date_by_boolean) == len(group_daily(date_by_boolean))


def test_value_daily_grouping(date_by_value):
    assert len(date_by_value) == len(group_daily(date_by_value))


def test_boolean_weekly_grouping(date_by_boolean):
    assert len(group_weekly(date_by_boolean)) == 53


def test_value_weekly_grouping(date_by_value):
    assert len(group_weekly(date_by_value)) == 53


def test_boolean_monthly_grouping(date_by_boolean):
    assert len(group_monthly(date_by_boolean)) == 13


def test_value_monthly_grouping(date_by_value):
    assert len(group_monthly(date_by_value)) == 13

