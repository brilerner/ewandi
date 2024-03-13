"""
To get done:
- set up corr_timescales (for survey, but what else?)

- make func names, i.e. relationship_single
"""

# set defaults
TIME_RANGE = START, END
MAXLAG_DAYS = 3
MAXLAG_HOURS = 12
ALPHA = 0.05

# based on the data for the target element(s) filter out any incompatible elements

def function_that_determines_relationship_operation():
    """
    What is relationship.... OR
    What's causing x .... OR
    What does x cause...
    THIS SHOULD PROBABLY CONSTRAIN THE TYPES OF RELATIONSHIPS TO LOOK FOR
    """

def check_typematch():
    pass

def resample_data(elem1, ):
    pass

def make_events_df(events1, events2):
    pass

def check_for_corr(elem1, elem2):
    """
    Comes before measure_corr
    """

    if elem1['dtype'] == elem2['dtype']:
        measure_corr(elem1, elem2)
    else:
        pass

def apply_correlation(events, method):
    # determine timescale (try to use the first two columns to guess)
    
    # loop over lags
    if timescale == 'D'
        maxlag = MAXLAG_DAYS
    elif timescale == 'H':
        maxlag = MAXLAG_HOURS

    lags = range(-maxlag,maxlag+1)

    # neg lags (checking if elem2 causes elem1), and then vice versa for pos lags
    corr_df = pd.DataFrame(columns=[e1_name, e2_name])
    for l in lags:

        # modify data with lag (see other script file)
        ...

        # get p-value
        ... 

        # check for corr with odds ratio

        corr_df[l, 'odds_cor'] = ...
        corr_df[l, 'p_value'] = ...
        

    # store in the database
    ...

def check_for_significiance_and_causality()
    # check for significance using ALPHA preset
        

    # determine MOST significant (or first...)


    # determine causality (are there significant findings for both pos/neg lags)
    causal_lag = True # HOW TO STORE FOR EACH ELEM 

def determine_causal_lag():
    """
    If multiple significant for pos lag, take lowest p-val or first..
    Do the same for neg lag
    If there is a only a value for lag in one direction, report causal_lag = True (or simialr)
    If in both, report that simply, there is a relationship
    """

def format_relationship():
    """
    If an element should be shown to the LLM, tell the following:
    - timescale
    - lag
    - how the specific categories correlate...
    Overall formatting to LLM, shoudl list in the following cats: caused by, causes, correlated with
    """
    corr_results = {
        "significant"

    }
    return corr_results
    

def measure_corr(elem1, elem2, time_range):
    """Determine the correlation.

    Arguments:
        elem1 -- _description_
        elem2 -- _description_
        time_range -- _description_
    """

    # get the events for events1
    events1 = ...
    events2 = ...

    # turn the events into a df 
    events_df = make_events_df(events1, events2)

    # set resampling timescale
    if (elem1['corr_timescale'] == 'H') and (elem2['corr_timescale'] == 'H'):
        resample_timescale = 'H'
    else:
        resample_timescale = 'D'
    # resample
    events_df = resample_func(events_df)

    # run correlation test

    corr_results = apply_correlation(events_df?, method)


    

    



    # get the correlat


def query_LLM_correlation_score(elem1, elem2):
    # ask the LLM what level of correlation exists
    # update the correlation info for both elements at the same time




def filter_incompatible_elements(elem1, elem2=None):

    dtype_elem1 = elem1['dtype']

    if