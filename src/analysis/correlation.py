import sys
from pathlib import Path
p = Path(__file__).resolve()
while p.name != 'src':
    p = p.parent
sys.path.append(str(p))

import pandas as pd
from server.retrieve import get_events
from scipy.stats import chi2_contingency, fisher_exact
"""
The correlation routine does the following:
1. for two variables, it checks if they have a matching data type for correlation
2. uses LLM to assess causality
3. applies correlation function to the data
"""

def lag_data(x1, x2, lag):
    if lag:
        # print('fff')
        # print(x1[:2])
        x1 = x1[:-lag]
        x2 = x2[lag:]
    return x1, x2

def cut_df(df):
    """Remove any events before the first occurrence for any variable and after the last occurrence for any variable."""
    first_occurrences = df.idxmax()
    last_occurrences = df.iloc[::-1].idxmax()
    first = first_occurrences.max()
    last = last_occurrences.min()
    return df[first:last]


def check_for_correlation(x1, x2, func='fisher_exact', alpha=0.05, lag=0):
    x1 = list(x1)
    x2 = list(x2)
    if lag:
        x1, x2 = lag_data(x1, x2, lag)
    x1 = pd.Categorical(x1, categories=[0, 1])
    x2 = pd.Categorical(x2, categories=[0, 1])
    table = pd.crosstab(x1, x2, dropna=False)
    print(table)
    sig_stat, p_value = fisher_exact(table, alternative='two-sided')
    print(f'p-value: {p_value}')
    # print(x1)
    # print(pd.DataFrame([x1, x2]).T)
    return p_value

    if p_value < alpha:
        return True
    else:
        return False

def filter_events(name, col='name', events=None):
    """
    Get the events from the data
    """

    if events is None:
        events = get_events()

    return [event for event in events if event[col] == name]


def make_cts_df(all_events, cut=True, cap=False):

    min_start_datetime = min([event['start_datetime'] for event in all_events])
    max_start_datetime = max([event['start_datetime'] for event in all_events])
        
    df = pd.DataFrame(all_events)

    # make new column for the day
    df['day'] = df['start_datetime'].dt.date

    # make a new df where each row is a day and the columns are the counts of v1 and v2
    # each row is a day from min day to max day
    days = pd.date_range(min_start_datetime.date(), max_start_datetime.date(), freq='D')

    names = df['name'].unique()



    days = [day.date() for day in days]
    day_counts = pd.DataFrame(index=days, columns=names)


    # names of the variables
    
    # fill in the counts
    for day in days:
        # print(day)
        # print(df['day'])
        # print(df['day'] == day)
        for name in names:
            count = len(df[(df['name'] == name) & (df['day'] == day)])
            day_counts.loc[day, name] = count

    # fill in any missing values with 0
    day_counts.fillna(0, inplace=True)

    if cut:
        day_counts = cut_df(day_counts)

    if cap:
        day_counts = day_counts.clip(upper=1)

    return day_counts
