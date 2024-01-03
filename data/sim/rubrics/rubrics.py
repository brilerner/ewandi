
def sleep_quality(event):

    from datetime import timedelta
    duration = event['end_time'] - event['start_time']

    if duration >= timedelta(hours=7):
        label = True
    else:
        label = False

    event['rubric_value'] = label

