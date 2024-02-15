from create_data import create_data
from generate_prompts import generate_prompts
from extract_args import extract_args
from analyze import analyze
from element_matching_perf import search_performance

# name = 'simple'
name = 'llm_v1'
n = 100
# step 1
create_data(name=name, n_input_trials=n)
# # step 2
generate_prompts(name=name)
# # step 3
extract_args(name=name)#, model='gpt-3.5-turbo-0125')#, n=100)
# step 4
analyze(name=name)
# step 5
search_performance(name=name)
# step 6
analyze(name=name, post_search=True)