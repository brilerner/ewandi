import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

import pandas as pd


def analyze(name="simple", post_search=False):

    print(f"Analyzing results for {name}")
    # load in the results
    if not post_search:
        filename = f"extracted_args_{name}.csv"
    else:
        filename = f"extracted_args_post-search_{name}.csv"
    df = pd.read_csv(Path(__file__).parent / filename)
    # fill in any NaNs with empty strings
    df = df.fillna("")

    col_mapping = {k: f"{k}_i" for k in ["v", "p", "dr", "tr", "d"]}

    # make a blank df with no cols/rows
    analysis_df = pd.DataFrame()
    arg_types = ["v", "p", "dr", "tr", "d"]
    for arg_type in arg_types:
        arg_inp = df[f"{arg_type}_i"]
        if arg_type in ['v', 'p'] and post_search:
            suffix = "n"
        else:
            suffix = "e"
        arg_out = df[f"{arg_type}_{suffix}"]
        # calculate accuracy
        acc = (arg_inp == arg_out).mean()
        # print(f"Accuracy for {arg_type}: {acc:.2%}")
        # get incorrect indices
        incorrect = arg_inp != arg_out
        incorrect_indices = df[incorrect].index
        # print the incorrect indices
        # print(f"Incorrect indices for {arg_type}: {list(incorrect_indices)}")
        analysis_df.loc[arg_type, "n"] = int(len(df))
        analysis_df.loc[arg_type, "accuracy"] = round(acc, 2)
        analysis_df.loc[arg_type, "incorrect_indices"] = str(list(incorrect_indices))  # Convert to string

    print(analysis_df)
    if not post_search:
        analysis_filename = f"results_{name}.csv"
    else:
        analysis_filename = f"results_post-search_{name}.csv"
    analysis_df.to_csv(Path(__file__).parent / analysis_filename)

    # now go through the incorrect indices and print the input and output
    print()
    for arg_type in arg_types:
        incorrect_indices = eval(analysis_df.loc[arg_type, "incorrect_indices"])
        print(f"Incorrect indices for {arg_type}: {incorrect_indices}")
        for i in incorrect_indices:
            input = df.loc[i, f"{arg_type}_i"]
            if arg_type in ['v', 'p'] and post_search:
                suffix = "n"
            else:
                suffix = "e"
            output = df.loc[i, f"{arg_type}_{suffix}"]
            # if input or output is a string, print it with quotes
            if isinstance(input, str):
                input = f'"{input}"'
            if isinstance(output, str):
                output = f'"{output}"'
            print(f"Input: {input}")
            print(f"Output: {output}")
            # print(f"Prompt: {df.loc[i, 'prompt']}")
            # print(f"User Query: {df.loc[i, 'user_query']}")
            # print(f"Args JSON: {df.loc[i, 'args_json']}")
            # print(f"Args: {df.loc[i, 'args']}")
            # print(f"Request Time: {df.loc[i, 'request_time_s']}")
            print("\n")

if __name__ == "__main__":
    analyze()