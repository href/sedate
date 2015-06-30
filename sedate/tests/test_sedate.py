import pytest
import sedate
import pytz

from datetime import datetime


def test_ensure_timezone():
    assert sedate.ensure_timezone('Europe/Zurich') \
        == pytz.timezone('Europe/Zurich')

    assert sedate.ensure_timezone(pytz.timezone('Europe/Zurich')) \
        == pytz.timezone('Europe/Zurich')


def test_utcnow():

    assert sedate.utcnow().replace(
        tzinfo=None, microsecond=0, second=0, minute=0) \
        == datetime.utcnow().replace(microsecond=0, second=0, minute=0)

    assert sedate.utcnow().tzinfo == pytz.timezone('UTC')


def test_standardize_naive_date():
    naive_date = datetime(2014, 10, 1, 13, 30)
    normalized = sedate.standardize_date(naive_date, 'Europe/Zurich')

    assert normalized.tzname() == 'UTC'
    assert normalized.replace(tzinfo=None) == datetime(2014, 10, 1, 11, 30)


def test_standardize_aware_date():
    aware_date = sedate.replace_timezone(
        datetime(2014, 10, 1, 13, 30), 'Europe/Zurich')

    normalized = sedate.standardize_date(aware_date, 'Europe/Zurich')

    assert normalized.tzname() == 'UTC'
    assert normalized.replace(tzinfo=None) == datetime(2014, 10, 1, 11, 30)


def test_is_whole_day():
    assert sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 7, 1), 'Europe/Zurich'),
        'Europe/Zurich'
    )

    assert sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 59), 'Europe/Zurich'),
        'Europe/Zurich'
    )

    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 1), 'Europe/Zurich'),
        'Europe/Zurich'
    )
    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 58), 'Europe/Zurich'),
        'Europe/Zurich'
    )
    assert not sedate.is_whole_day(
        sedate.replace_timezone(
            datetime(2015, 6, 30, 0, 0, 0, 999), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 6, 30, 23, 59, 59), 'Europe/Zurich'),
        'Europe/Zurich'
    )


def test_count_overlaps():
    assert sedate.count_overlaps([
        (datetime(2015, 1, 1, 10, 0), datetime(2015, 1, 1, 11, 0)),
        (datetime(2015, 1, 1, 12, 0), datetime(2015, 1, 1, 13, 0))
    ], datetime(2015, 1, 1, 10), datetime(2015, 1, 10, 13)) == 2


def test_align_range_to_day():
    assert sedate.align_range_to_day(
        start=sedate.replace_timezone(
            datetime(2015, 1, 1, 10, 0), 'Europe/Zurich'),
        end=sedate.replace_timezone(
            datetime(2015, 1, 1, 11, 0), 'Europe/Zurich'),
        timezone='Europe/Zurich'
    ) == (
        sedate.replace_timezone(
            datetime(2015, 1, 1), 'Europe/Zurich'),
        sedate.replace_timezone(
            datetime(2015, 1, 1, 23, 59, 59, 999999), 'Europe/Zurich')
    )


def test_get_date_range():
    assert sedate.get_date_range(
        sedate.replace_timezone(datetime(2015, 1, 1), 'Europe/Zurich'),
        datetime(2015, 1, 1, 12, 0).time(),
        datetime(2015, 1, 2, 11, 0).time(),
    ) == (
        sedate.replace_timezone(datetime(2015, 1, 1, 12, 0), 'Europe/Zurich'),
        sedate.replace_timezone(datetime(2015, 1, 2, 11, 0), 'Europe/Zurich'),
    )


def test_is_whole_day_summertime():

    start = sedate.standardize_date(
        datetime(2014, 10, 26, 0, 0, 0), 'Europe/Zurich')

    end = sedate.standardize_date(
        datetime(2014, 10, 26, 23, 59, 59), 'Europe/Zurich')

    assert sedate.is_whole_day(start, end, 'Europe/Zurich')
    assert not sedate.is_whole_day(start, end, 'Europe/Istanbul')


def test_is_whole_day_wintertime():

    start = sedate.standardize_date(
        datetime(2015, 3, 29, 0, 0, 0), 'Europe/Zurich')

    end = sedate.standardize_date(
        datetime(2015, 3, 29, 23, 59, 59), 'Europe/Zurich')

    assert sedate.is_whole_day(start, end, 'Europe/Zurich')
    assert not sedate.is_whole_day(start, end, 'Europe/Istanbul')


def test_require_timezone_awareness():

    naive = datetime(2014, 10, 26, 0, 0, 0)

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.to_timezone(naive, 'UTC')

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.is_whole_day(naive, naive, 'UTC')

    with pytest.raises(sedate.NotTimezoneAware):
        sedate.align_date_to_day(naive, 'UTC', 'up')


def test_overlaps():

    overlaps = [
        [
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ],
        [
            datetime(2013, 1, 1, 11, 0), datetime(2013, 1, 1, 12, 0),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ]
    ]

    doesnt = [
        [
            datetime(2013, 1, 1, 11, 0), datetime(2013, 1, 1, 11, 59, 59),
            datetime(2013, 1, 1, 12, 0), datetime(2013, 1, 1, 13, 0),
        ]
    ]

    tz = 'Europe/Zurich'

    for dates in overlaps:
        assert sedate.overlaps(*dates)

        timezone_aware = [sedate.standardize_date(d, tz) for d in dates]
        assert sedate.overlaps(*timezone_aware)

    for dates in doesnt:
        assert not sedate.overlaps(*dates)

        timezone_aware = [sedate.standardize_date(d, tz) for d in dates]
        assert not sedate.overlaps(*timezone_aware)


def test_align_date_to_day_down():

    unaligned = sedate.standardize_date(datetime(2012, 1, 24, 10), 'UTC')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'down')

    assert aligned.tzname() == 'UTC'
    assert aligned == sedate.standardize_date(
        datetime(2012, 1, 24, 0), 'Europe/Zurich')

    already_aligned = sedate.replace_timezone(
        datetime(2012, 1, 1), 'Europe/Zurich'
    )

    assert already_aligned == sedate.align_date_to_day(
        already_aligned, 'Europe/Zurich', 'down')


def test_align_date_to_day_up():
    unaligned = sedate.standardize_date(datetime(2012, 1, 24, 10), 'UTC')
    aligned = sedate.align_date_to_day(unaligned, 'Europe/Zurich', 'up')

    assert aligned.tzname() == 'UTC'
    assert aligned == sedate.standardize_date(
        datetime(2012, 1, 24, 23, 59, 59, 999999), 'Europe/Zurich')

    already_aligned = sedate.replace_timezone(
        datetime(2012, 1, 1, 23, 59, 59, 999999), 'Europe/Zurich'
    )

    assert already_aligned == sedate.align_date_to_day(
        already_aligned, 'Europe/Zurich', 'up')