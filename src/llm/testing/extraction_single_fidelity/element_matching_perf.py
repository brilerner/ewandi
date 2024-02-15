import sys
from pathlib import Path
src_dir = Path(__file__).resolve()
while src_dir.name != 'src':
    src_dir = src_dir.parent
sys.path.append(str(src_dir))

from server.search import find_nearest
import pandas as pd
import time

def search_performance(name='llm_v1'):
    if name == 'simple':
        print("No performance data for simple")
        return
    
    search_kwargs = {
        # 'threshold': None
        'model' : "text-embedding-3-small"
    } 

    print(f"Analyzing search results for {name}")
    # load in the results
    df = pd.read_csv(Path(__file__).parent / f"extracted_args_{name}.csv")
    # fill in any NaNs with empty strings
    df = df.fillna("")

    col_mapping = {k: f"{k}_i" for k in ["v", "p", "dr", "tr", "d"]}

    arg_types = ["v", "p"]
    keep_cols = [f"{arg_type}_{i}" for arg_type in arg_types for i in ["i", "e"]]
    df = df[keep_cols]
    addl_suffixes = ["n", "d"]
    for arg_type in arg_types:
        for suffix in addl_suffixes:
            df[f"{arg_type}_{suffix}"] = ""


    # make a blank df with no cols/rows
    results = []
    for i, r in df.iterrows():
        print(f"Analyzing search results for row {i}")
        for arg_type in arg_types:
            arg_inp = r[f"{arg_type}_i"]
            arg_out = r[f"{arg_type}_e"]
            if not arg_out:
                # print(arg_type, i)
                continue
            
            if '[' in arg_out and ']' in arg_out:
                arg_out = eval(arg_out)
            else:
                arg_out = [arg_out]

            for ai, arg_out_single in enumerate(arg_out):

                start = time.time()
                elements, distances = find_nearest(
                    arg_out_single, 
                    element_type={'v':'events', 'p':'relations'}[arg_type], 
                    profile=name, 
                    threshold=None,
                    n=5,
                    return_distances=True,
                    **search_kwargs
                    )
                search_time = round((time.time() - start),2) 
                for j, (e, d) in enumerate(zip(elements, distances)):

                    results.append({
                        "trial": i, 
                        "arg_index": ai,
                        "nearest_index": j,
                        "arg_type": arg_type, 
                        "arg_inp": arg_inp, 
                        "arg_out": arg_out_single, 
                        "e_base": e['base'], 
                        "e_text": e['text'],
                        "distance": round(d, 3), 
                        "search_time": search_time})





        #     df.loc[i, "search_time_ms"] = round((time.time() - start) * 1000,2)  # convert to ms

        #     df.loc[i, f"{arg_type}_n"] = elements[0]['base']
        #     df.loc[i, f"{arg_type}_d"] = round(distances[0], 2)
        # # calculate accuracy
        #     {"trial": i, "arg_type": arg_type, "arg_inp": arg_inp, "arg_out": arg_out, "elements": elements, "distances": distances}

    df = pd.DataFrame(results)

    df = df.set_index(["trial", "arg_index", "nearest_index"])
    print(df)
    for k, v in search_kwargs.items():
        df[k] = v

    # cols = list(search_kwargs.keys())
    # cols += [f"{c}_{t}" for c in ["v", "p"] for t in ["i", "e"]+addl_suffixes]
    # cols += ["search_time_ms"]
    # df = df[cols]

    df.to_csv(Path(__file__).parent / f"search_results_{name}.csv")

def search_performance(name='llm_v1'):
    if name == 'simple':
        print("No performance data for simple")
        return
    
    search_kwargs = {
        # 'threshold': None
        'model' : "text-embedding-3-small"
    } 

    print(f"Analyzing search results for {name}")
    # load in the results
    ext_df = pd.read_csv(Path(__file__).parent / f"extracted_args_{name}.csv")
    # fill in any NaNs with empty strings
    ext_df = ext_df.fillna("")

    # col_mapping = {k: f"{k}_i" for k in ["v", "p", "dr", "tr", "d"]}

    arg_types = ["v", "p"]
    # keep_cols = [f"{arg_type}_{i}" for arg_type in arg_types for i in ["i", "e"]]
    # ext_df = ext_df[keep_cols]
    # addl_suffixes = ["n", "d"]
    # for arg_type in arg_types:
    #     for suffix in addl_suffixes:
    #         ext_df[f"{arg_type}_{suffix}"] = ""


    # make a blank df with no cols/rows
    results = []
    for i, r in ext_df.iterrows():
        print(f"Analyzing search results for row {i}")
        for arg_type in arg_types:
            arg_inp = r[f"{arg_type}_i"]
            arg_out = r[f"{arg_type}_e"]
            if arg_type == 'p':
                pass
            if not arg_out:
                # print(arg_type, i)
                continue
            
            if '[' in arg_out and ']' in arg_out:
                arg_out = eval(arg_out)
            else:
                arg_out = [arg_out]

            if '[' in arg_inp and ']' in arg_inp:
                arg_inp = eval(arg_inp)
            else:
                arg_inp = [arg_inp]


            for ai, arg_out_single in enumerate(arg_out):

                start = time.time()
                elements, distances = find_nearest(
                    arg_out_single, 
                    element_type={'v':'events', 'p':'relations'}[arg_type], 
                    profile=name, 
                    threshold=None,
                    n=5,
                    return_distances=True,
                    **search_kwargs
                    )
                search_time = round((time.time() - start),2) 
                for j, (e, d) in enumerate(zip(elements, distances)):

                    results.append({
                        "trial": i, 
                        "arg_index": ai,
                        "nearest_index": j,
                        "arg_type": arg_type, 
                        "arg_inp": arg_inp[ai], 
                        "arg_out": arg_out_single, 
                        "e_base": e['base'], 
                        "e_text": e['text'],
                        "distance": round(d, 3), 
                        "search_time": search_time})

    df = pd.DataFrame(results)
    df = df.set_index(["trial", "arg_index", "nearest_index"])
    print(df)
    for k, v in search_kwargs.items():
        df[k] = v
    df.to_csv(Path(__file__).parent / f"search_results_{name}.csv")

    df = df.reset_index()
    for t, tdf in df.groupby('trial'):
        for at, atdf in tdf.groupby('arg_type'):
            atdf = atdf[atdf['nearest_index'] == 0]
            if at == 'v':
                arg_out = atdf["e_base"].values[0]
            elif at == 'p':
                arg_out = list(atdf["e_base"].values)
                arg_out = [p.split(' (people)')[0] for p in arg_out]
            
            ext_df.loc[t, f"{at}_n"] = str(arg_out)
    
    cols = list(ext_df.columns)
    for at in arg_types:
        cols.insert(cols.index(f"{at}_e")+1, f"{at}_n")
    ext_df = ext_df[cols]
    ext_df.to_csv(Path(__file__).parent / f"extracted_args_post-search_{name}.csv") 



if __name__ == '__main__':
    search_performance()