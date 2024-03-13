def good_sleep(event):
    from datetime import timedelta

    duration = event["end_time"] - event["start_time"]

    if duration >= timedelta(hours=7):
        label = True
    else:
        label = False

    return label

def good_mood(event):
    from datetime import timedelta

    # score cutoffs
    good_mood = 6
    neutral_mood = 4

    mood = event["value"]

    if mood >= good_mood:
        label = "good"

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
