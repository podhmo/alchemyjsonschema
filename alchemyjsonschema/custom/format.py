# -*- coding:utf-8 -*-
import re
from jsonschema._format import _checks_drafts, FormatChecker, _draft_checkers
import calendar
from datetime import date, time
from ..compat import string_types

"""
this is custom format
"""
time_rx = re.compile("(\d{2}):(\d{2}):(\d{2})(\.\d+)?(Z|([+\-])(\d{2}):(\d{2}))?")
date_rx = re.compile("(\d{4})\-(\d{2})\-(\d{2})")


def parse_date(date_string):
    m = date_rx.match(date_string)
    if m is None:
        return None

    groups = m.groups()

    year, month, day = [int(x) for x in groups[:3]]
    return date(year, month, day)


def validate_date(date_string):
    m = date_rx.match(date_string)
    if m is None:
        return False

    groups = m.groups()

    year, month, day = [int(x) for x in groups[:3]]

    if not 1 <= year <= 9999:
        # Have to reject this, unfortunately (despite it being OK by rfc3339):
        # calendar.timegm/calendar.monthrange can't cope (since datetime can't)
        return False

    if not 1 <= month <= 12:
        return False

    (_, max_day) = calendar.monthrange(year, month)
    if not 1 <= day <= max_day:
        return False

    # all OK
    return True


def parse_time(time_string):
    m = time_rx.match(time_string)
    if m is None:
        return None

    groups = m.groups()

    hour, minute, second = [int(x) for x in groups[:3]]
    if groups[4] is not None and groups[4] != "Z":
        return time(hour, minute, second, int(groups(3)))
    return time(hour, minute, second)


def validate_time(time_string):
    m = time_rx.match(time_string)
    if m is None:
        return False

    groups = m.groups()

    hour, minute, second = [int(x) for x in groups[:3]]
    if not (0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59):
        # forbid leap seconds :-(. See README
        return False

    if groups[4] is not None and groups[4] != "Z":
        (offset_sign, offset_hours, offset_mins) = groups[5:]
        if not (0 <= int(offset_hours) <= 23 and 0 <= int(offset_mins) <= 59):
            return False

    # all OK
    return True


@_checks_drafts("date", raises=ValueError)
def is_date(instance):
    if not isinstance(instance, string_types):
        return True
    return validate_date(instance)


@_checks_drafts("time", raises=ValueError)
def is_time(instance):
    if not isinstance(instance, string_types):
        return True
    return validate_time(instance)


draft3_format_checker = FormatChecker(_draft_checkers["draft3"])
draft4_format_checker = FormatChecker(_draft_checkers["draft4"])
