If a quant value, then only need to return one label! Doesn't make sense to compare otherwise
what if someone says, how did my stress and mood behave over a time period? Then we'll break the problem down into chunks and apply the algorithm.
Handle properly when the request is for the presence and for the lack of presence

Thresholding
- if the distance is close to the threshold, consider asking user for new input


Keywords
I am making the following assumptions for the demo
1. The model is aware of the nature of the type of relationship that the user has with each person


This demo is capable of

Next steps include
- breaking down a query into component queries
- enabling tools to output a response as well as information that can be fed into the next step
- live label extraction
- using context, intelligently generate descriptions with LLM 
    - determine upon extraction
Demo assumptions
- that later, I will intelligently generate descriptions with LLM 
    -

Improving method extractin
    Agents
    - The next version of Cerebra-A will have an agent that access a small finetuned model that can rapidly create code/output that can be used to construct flexible querying.

    grouping
    - agent approach is better but either through embedding hacks or extraction I could group together variables (i.e.  "do x and y happen on the same time as...)
    - embedding hack could be: getting embedding for all pairs of names
    - potential flow: breakdown ---> regroup vars --> feed into tools

    Breaking down query (not doing)
    - use quick gpt 3.5 call
    - this can still work with agents
    - example:
        func1(x, final=False, feed=None, feed_next_reqs=['min_date'])
            return response, min_date
        func2(x, final=True, feed=feed_next)
    - when feeding, also determine how the part responses should be incorporated into the final response

### To add to prompt

to tell user (not in prompt)
- in contrast to other LLM systems, Cerebra has been designed to be fast and to answer concisely
- while ot can find complex relationships, it can not handle overly complex questions or demands
- so, keep these limitatios in mind (tell limits)

Limitations
- no control over plotting
    - might change in future
- input limits
    - variables: 3
    - operations:
        counts
        averages
        resampling

prompt directives
- use plot as needed (or just regardless?)
- answer concisely

correlation
- "If you typically experience event first...""
# Approach

Embedding 
(note: values dont need groups)
- padded strategy
- describe use case in prompt; i.e. we want phrases that correspond to user input
- for each element/person: 
    - use stored_name/desc to generate variants
    - ask one at a time?
- group creation
groups = []
for c in cat:
    unique_pairs = get()
    sample = unique_pairs[:N]
    for pair in sample:
        group = get_shared_group(pair) # generate; include stored_name/desc
        groups.append(group)
Then, weeding out similar groups   
    - use embedding threshold
    - llm test
        - for each member in group, if similar to any others, note

Figures
- since the tool is handling the data, it is in a good position to make fig
- the tool will save the plot specs/data to a tmp file
- it will produce a placeholder token that gets outputted
- the LLM can then decide on whether to plot it
- if it does the placeholder token can retrieve the data

Query handling
- extract
    - vars
    - timing
    - op?
        - this could work, but if not using tools directly, then it will be harder to respond to input query if it beckons an adjustment

Correlation (user input)
1. validate kw
2. typematch
3. event nan/missingness threshold
4. determine what comes first
    - for days where events co-occur, find
       % of days where day1 comes first
    - i.e. S = T_first/T_occur
    - BUT WHAT IF ITS IN THE MIDDLE --> then check both
    - figure out how to combine LLM causality score for middle cases
5. check LLM causality score
6. return results

Correlation (automated)
2. typematch
3. event nan/missingness threshold (i.e. how many events needed)
4. determine what comes first
    - for days where events co-occur, find
       % of days where day1 comes first
    - i.e. S = T_first/T_occur
    - BUT WHAT IF ITS IN THE MIDDLE --> then check both
    - figure out how to combine LLM causality score for middle cases
5. check LLM causality score
6. determine if interesting to user?

Tools
- find interesting correlations
    - tell user interesting correlations
- correlate
    - input: x_info (keyword, min/max time/dates)
- to do later
    - RAG


date handling
- try with prompting
    - "convert to isoformat..
    - "breakfast should be considered this and lunch...
- if this doesnt work, then try to use quick call


Cat breakdown
- source: sleep tracker, cat: activity
- source: schedule, cat: activity
- source: survey, cat: score (or rating)
- source: extracted, cat: [activity, sensation]
- source: food tracker, cat: [meal, dietary intake]

Overall to-do
- embedding padding
    - if needed, I can just write in the groups myself
    - will almost definitely be quicker for now

To-do
- prioritize wants
- efficently run tests
    - see gpt3.5 vs gpt4 perf and time
SEE tests
- incorporate people descriptions
- update descriptions for ingredients
    "An ingredient for dietary consumption."
- sim dataset
- test simple keyword matching
- set up logging/ make streaming work
- test simple tool usage
ONCE working
- make cat a group
- make duration a value for all events
- pad embedding space
- write correlation framework
- write tools
- implement plotting


Potential later
- change score to rating

Tests
LLM
- how well can it convert input to formatted dates
- similarity between generated embedding groups
- test effect of temperature on generating variants
- Can LLM recognize input restrictions and reject?
- Can plotting be accomplished usign placeholder tokens
- How do Spearman/Pearson do with lots of missing in data
    - try to determine non-event threshold

