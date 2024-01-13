def good_sleep(event):
    from datetime import timedelta

    duration = event["end_time"] - event["start_time"]

    if duration >= timedelta(hours=7):
        label = True
    else:
        label = False

    return label


def get_duration(event):
    """
    Get duration of event in hours
    """
    duration = event["end_time"] - event["start_time"]
    duration = duration.total_seconds() / 3600
    return duration
