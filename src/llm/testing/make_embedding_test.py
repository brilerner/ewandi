import sys
from pathlib import Path

src_dir = Path(__file__).resolve()
while src_dir.name != "src": src_dir = src_dir.parent
sys.path.append(str(src_dir))

from openai import OpenAI

from sim import construct
from server.transfer import insert_profile_data
from llm.embeddings import request_embedding, get_distance
from llm.chat import json_request
import copy
from collections import defaultdict
import random
import pandas as pd

# MODEL = 'gpt-4-1106-preview'
from utils.sampling import select_random_members_as_dict
import prompts as pr
from llm.generate import (
    generate_groups,
    classify_name,
    generate_nonexisting_keystrings,
    generate_variations,
)

client = OpenAI()


# Main functions for each step
def generate_cat_groups(names_by_cat, do_not_group_cats=None):
    for cat_name, cat in names_by_cat.items():
        if cat_name in do_not_group_cats:
            cat["groups"] = {}
        else:
            names = list(cat["names"].keys())
            descriptions = [d.get("description", None) for d in cat["names"].values()]
            groups = generate_groups(names, descriptions=descriptions)
            for group in groups:
                cat["groups"][group] = defaultdict(list)


def assign_groups_to_names(names_by_cat):
    for cat_name, cat in names_by_cat.items():
        print(f"\ncat: {cat_name}")
        for name, name_dict in cat["names"].items():
            cat["names"][name]["groups"] = []
            for group in cat["groups"]:
                description = name_dict.get("description", None)
                group_decision = classify_name(name, group, description=description)
                if group_decision:
                    cat["names"][name]["groups"].append(group)
                    print(f"\n{name} is in {group}")
                else:
                    print(f"\n{name} is not in {group}")


def generate_nonexisting_entities(names_by_cat, n=5):
    for cat_name, cat in names_by_cat.items():
        cat["nonexisting"] = {}

        # names
        names = list(cat["names"].keys())
        nonexisting = generate_nonexisting_keystrings(names, n=n)
        names_by_cat[cat_name]["nonexisting"]["names"] = {
            name: {} for name in nonexisting
        }

        # groups
        groups = list(cat["groups"].keys())
        if groups:
            nonexisting = generate_nonexisting_keystrings(groups, n=n)
            names_by_cat[cat_name]["nonexisting"]["groups"] = {
                group: {} for group in nonexisting
            }
        else:
            names_by_cat[cat_name]["nonexisting"]["groups"] = {}


def generate_keystring_variations(names_by_cat, n=5):
    print("\nGenerating variations")
    for cat_name, cat in names_by_cat.items():
        print(f"\ncat: {cat_name}")
        for name, name_dict in cat["names"].items():
            description = name_dict.get("description", None)
            variations = generate_variations(name, description=description, n=n)
            names_by_cat[cat_name]["names"][name]["variations"] = {
                v: {} for v in variations
            }

        for group in cat["groups"]:
            variations = generate_variations(name, n=n)
            names_by_cat[cat_name]["groups"][group]["variations"] = {
                v: {} for v in variations
            }

        for ne in cat["nonexisting"]["names"]:
            variations = generate_variations(name, n=n)
            names_by_cat[cat_name]["nonexisting"]["names"][ne]["variations"] = {
                v: {} for v in variations
            }

        for ne in cat["nonexisting"]["groups"]:
            variations = generate_variations(name, n=n)
            names_by_cat[cat_name]["nonexisting"]["groups"][ne]["variations"] = {
                v: {} for v in variations
            }


def plot_analysis(df_analysis):
    """
    df_analysis is a DataFrame with the following columns: 'category', 'keystring', 'index', 'distance', 'group_percentage'
    The variables I want to plot are the index, distance, and group_percentage.
    This will create a single plot with six subplots.
    The first column will contain scatterplots and the second column will have bar charts.
    The first row will deal with index, the second row will deal with distance, and the third row will deal with group percentage.
    For the scatterplots:
        - sort the values from smallest to largest and assign an x-value based on the index of the value in the sorted list
        - the y-axis will be the value
        - The points in the scatterplot should be colored by category, with the color legend in the top right.
        - Only the topmost scatterplot needs a legend.
        - the legend should be ordered alphabetically
    For the bar charts
        - plot the average value for each category and overall
        - the color of the bars should match the colors used for the scatterplots
        - the overall average bar should be colored black
        - the value for each bar should be displayed above the bar
        - the overall average bar should be first and the other bars should then go in order alphabetically
    To summarize:
        - the first row will have a scatterplot of index and a bar chart of average index
        - the second row will have a scatterplot of distance and a bar chart of average distance
        - the third row will have a scatterplot of group percentage and a bar chart of average group percentage
    """
    import matplotlib.pyplot as plt
    import seaborn as sns

    # remove distance = 0
    df_analysis = df_analysis[df_analysis["distance"] != 0]

    fig, axes = plt.subplots(3, 2, figsize=(12, 12))

    scatterplot_categories = sorted(df_analysis["category"].unique())
    barplot_categories = ["overall"] + scatterplot_categories

    scatterplot_colors = sns.color_palette(
        "bright", len(df_analysis["category"].unique())
    )
    barplot_colors = ["black"] + scatterplot_colors
    scatterplot_legend = True
    scatterplot_title = True
    for i, col in enumerate(["index", "distance", "group_percentage"]):
        if col == "group_percentage":
            ascending = False
        else:
            ascending = True

        df_col = df_analysis.sort_values(col, ascending=ascending)
        df_col = df_col.reset_index(drop=True)

        # scatterplots
        ax = axes[i, 0]
        for category, color in zip(scatterplot_categories, scatterplot_colors):
            df_cat = df_col[df_col["category"] == category].copy()
            add_legend = True
            for mode in ["names", "groups"]:
                marker = {"names": "o", "groups": "s"}[mode]
                mdf = df_cat[df_cat["mode"] == mode]
                x = mdf.index
                y = mdf[col]
                # markers = list(mdf['mode'].apply(lambda x: 'o' if x == 'names' else 's'))
                # for x,y,m in zip(x_values, y_values, markers):
                if add_legend:
                    label = category
                    add_legend = False
                else:
                    label = None

                ax.scatter(x, y, color=color, label=label, marker=marker)
                # ax.scatter(x_values, y_values, color=color, label=category, marker = markers)

        if scatterplot_legend:
            ax.set_title("names: circles, groups: squares")
            ax.legend(loc="upper left")
            scatterplot_legend = False
            scatterplot_title = False
        ax.set_xlabel("Sort Position")
        ax.set_ylabel(col)

        # Bar charts
        ax = axes[i, 1]

        # # Bar settings
        # bar_width = 0.35
        # index = np.arange(len(categories))

        values = []
        # print('col:', col)
        for cat in barplot_categories:
            # print('cat:', cat)
            for mode in ["names", "groups"]:
                if cat == "overall":
                    df_cat = df_analysis.copy()
                else:
                    df_cat = df_analysis[df_analysis["category"] == cat].copy()

                df_avg = df_cat[df_cat["mode"] == mode]
                val = df_avg[col].mean()
                values.append(val)

        use_barplot_colors = [color for color in barplot_colors for _ in (0, 1)]
        use_barplot_categories = [
            f"{i}-{_}" for i, cat in enumerate(barplot_categories) for _ in ("n", "g")
        ]
        # print(barplot_categories)
        bars = ax.bar(use_barplot_categories, values, color=use_barplot_colors)
        for bar in bars:
            yval = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                yval,
                round(yval, 2),
                va="bottom",
                ha="center",
            )
        ax.set_xlabel("Category")
        ax.set_ylabel(col)
        ax.legend(loc="upper right")

    plt.tight_layout()
    plt.show()
    return fig


def determine_optimal_threshold(analysis_results):
    # Implementation for Step 8
    pass


def convert_to_df(names_by_cat):
    import pandas as pd

    rows = []
    for cat_name, main_cat in names_by_cat.items():
        for existence in [True, False]:
            if existence:
                cat = main_cat
            else:
                cat = main_cat["nonexisting"]

            for mode in ["names", "groups"]:
                for ks, ks_dict in cat[mode].items():
                    entry = {
                        "category": cat_name,
                        "base": ks,
                        "keystring": ks,
                        "mode": mode,
                        "variation": False,
                        "existing": existence,
                        "groups": ks_dict.get("groups", None),
                        "description": ks_dict.get("description", None),
                    }
                    rows.append(entry)
                    if variations := ks_dict.get("variations", None):
                        for v_ks in variations:
                            v_entry = copy.deepcopy(entry)
                            v_entry.update(
                                {
                                    "keystring": v_ks,
                                    "variation": True,
                                }
                            )
                            rows.append(v_entry)

    df = pd.DataFrame(rows)
    return df


def get_all_distances(df_keystrings):
    distances = []

    # Iterate over each row in the DataFrame
    for i, row_i in df_keystrings.iterrows():
        current_distances = {}
        for j, row_j in df_keystrings.iterrows():
            if i != j:  # Skip calculating distance with itself
                dist = get_distance(row_i["embedding"], row_j["embedding"])
                current_distances[df_keystrings.at[j, "keystring"]] = dist
            elif i == j:
                current_distances[df_keystrings.at[j, "keystring"]] = 0
        distances.append(current_distances)

    # Create a new DataFrame from the distances
    df_distances = pd.DataFrame(distances, index=df_keystrings["keystring"])

    return df_distances


# Function to sort options by distance, calculate group percentage, index, and distance

"""
Options should never include variants
Just the existing names and groups
Should not include current name
So, I don't care about getting index/distance for bases but I should do it anyway as a sanity cgeck
"""


def get_shared_membership_df(df_keystrings):
    df = df_keystrings[(df_keystrings["existing"]) & (df_keystrings["mode"] == "names")]

    membership = []

    # Iterate over each row in the DataFrame
    for i, row_i in df.iterrows():
        current_membership = {}
        for j, row_j in df.iterrows():
            if i != j:  # Skip comparing with itself
                if (
                    row_i["groups"] and row_j["groups"]
                ):  # Check if both keystrings have groups
                    shared_membership = bool(
                        set(row_i["groups"]) & set(row_j["groups"])
                    )  # Check if there is shared membership
                    current_membership[df.at[j, "keystring"]] = shared_membership
                else:
                    current_membership[df.at[j, "keystring"]] = False
            elif i == j:
                current_membership[df.at[j, "keystring"]] = True
        membership.append(current_membership)

    # Create a new DataFrame for shared membership
    df_membership = pd.DataFrame(membership, index=df["keystring"])

    return df_membership


def get_analysis_df(dfk, dfd):
    # Make a dataframe for all exisiting names that tracks whethery they share a group membership with any other existing names
    # make copy and remove 'embedding' column
    dfk = dfk.copy()
    dfk.drop(columns=["embedding"], inplace=True)
    df_analysis = dfk.copy()

    df_membership = get_shared_membership_df(dfk)

    results = []
    for i, r in dfk.iterrows():
        if r["existing"] == False:
            continue

        mode = r["mode"]
        keystring = r["keystring"]
        base = r["base"]

        # if base == 'personal relationships':
        #     pass
        # get options
        options = dfk[
            (~dfk["variation"]) & (dfk["existing"]) & (dfk["mode"] == "names")
        ].copy()

        # sort by distance
        options["distance"] = (
            dfd.loc[keystring, options["keystring"]].fillna(0).values
        )  # hopefully theres not nas besides original keystring
        options = options.sort_values(by=["distance"], ascending=True)
        print("\n", mode, base, keystring)
        print(options[["category", "base", "keystring", "distance"]].iloc[:10])
        print()
        options.set_index("keystring", drop=False, inplace=True)

        if mode == "names":
            # check membership
            options["shared_membership"] = df_membership.loc[
                keystring, options["keystring"]
            ]

            # find index and distance of base
            index = options.index.get_loc(base)
            distance = dfd.loc[keystring, base]

        if mode == "groups":
            # check membership
            options["shared_membership"] = options["groups"].apply(
                lambda x: True if base in x else False
            )

            # find index and distance of furthest group member

            furthest_keystring = options[options["shared_membership"]].index[-1]
            index = options.index.get_loc(furthest_keystring)
            distance = dfd.loc[furthest_keystring, base]

        # calculate group percentage
        group_percentage = options.iloc[: index + 1]["shared_membership"].mean()

        result = {
            "group_percentage": group_percentage,
            "index": index,
            "distance": distance,
            "keystring": keystring,
            "mode": mode,
        }
        results.append(result)
        # keystring'mode': mode, 'keystring': keystring, 'base': base}

    # add the results to df_analysis; use the keystring in each results dict to determine the row to update
    for result in results:
        print(result["mode"])
        keystring = result["keystring"]
        index = df_analysis[df_analysis["keystring"] == keystring].index[0]
        df_analysis.at[index, "group_percentage"] = result["group_percentage"]
        df_analysis.at[index, "index"] = result["index"]
        df_analysis.at[index, "distance"] = result["distance"]
        # if result['mode'] == 'groups':
        #     pass

    ncols = 5
    # get the 5 nearest neighbors for each keystring
    for i, r in df_analysis.iterrows():
        if r["existing"] == False:
            continue
        keystring = r["keystring"]
        options = dfk[
            (~dfk["variation"]) & (dfk["existing"]) & (dfk["mode"] == "names")
        ].copy()
        options["distance"] = dfd.loc[keystring, options["keystring"]].fillna(0).values
    # remove rows where no analysis was performed
    # df_analysis = df_analysis[df_analysis['group_percentage'].notna()]
    return df_analysis


def construct_strategy(profile="llm_v1"):
    import pickle
    from collections import defaultdict

    def start_step(step, steps_completed):
        if steps_completed == step - 1:
            if steps_completed == steps_completed:
                print(f"\nStarting Step {step}")
                return True

    override_steps_completed = 7

    do_not_group_cats = ["values"]
    true_event_cat_names = ["scheduled", "unscheduled", "meals", "sleep"]
    num_nonexisting_per_cat = 5

    files_dir = Path(__file__).resolve().parent / "embedding_files"
    save_state_path = files_dir / "strategy_state.pkl"

    def save_and_augment(names_by_cat_with_steps):
        if "steps_completed" not in names_by_cat_with_steps:
            names_by_cat_with_steps["steps_completed"] = 0
        names_by_cat_with_steps["steps_completed"] += 1
        pickle.dump(names_by_cat_with_steps, open(save_state_path, "wb"))

    # check to see if strategy_state.pkl exists
    if save_state_path.exists():
        print("strategy_state.pkl exists")
        names_by_cat_with_steps = pickle.load(open(save_state_path, "rb"))
        names_by_cat = names_by_cat_with_steps["data"]
        steps_completed = copy.deepcopy(names_by_cat_with_steps["steps_completed"])
        if "df_keystrings" in names_by_cat_with_steps:
            df_keystrings = names_by_cat_with_steps["df_keystrings"]
        if "df_distances" in names_by_cat_with_steps:
            df_distances = names_by_cat_with_steps["df_distances"]
        if "df_analysis" in names_by_cat_with_steps:
            df_analysis = names_by_cat_with_steps["df_analysis"]

        if override_steps_completed:
            names_by_cat_with_steps["steps_completed"] = override_steps_completed
    else:
        # transfer from the database
        events_by_cat = get_all_events_by_cat(profile=profile)
        names_by_cat = get_names_by_cat(events_by_cat, name_limit=3)
        names_by_cat_with_steps = {"data": names_by_cat}
        steps_completed = 0

    # Step 1
    if steps_completed == 0:
        print("\nStarting Step 1")

        # Step 1a
        # combine cats
        names_by_cat["true_events"] = {}
        for cat_name, name_dicts in names_by_cat.items():
            if cat_name in true_event_cat_names:
                names_by_cat["true_events"].update(copy.deepcopy(name_dicts))
        for cat_name in true_event_cat_names:
            names_by_cat.pop(cat_name)

        # remove categories
        skip_cats = ["scores"]  # not needed, since not really an event
        for cat_name in skip_cats:
            names_by_cat.pop(cat_name)

        # refine before continuing
        for cat_name, cat in names_by_cat.items():
            names_by_cat[cat_name] = {"names": copy.deepcopy(cat)}
            names_by_cat[cat_name]["groups"] = defaultdict(list)

        # Step 1b
        generate_cat_groups(names_by_cat, do_not_group_cats)
        for cat_name, cat in names_by_cat.items():
            print()
            print(cat_name)
            print("groups:", list(cat["groups"].keys()))
        save_and_augment(names_by_cat_with_steps)

    if start_step(2, names_by_cat_with_steps["steps_completed"]):
        assign_groups_to_names(names_by_cat)
        for cat_name, cat in names_by_cat.items():
            print()
            print(cat_name)
            print("groups:", cat["groups"])
        save_and_augment(names_by_cat_with_steps)

    if start_step(3, names_by_cat_with_steps["steps_completed"]):
        generate_nonexisting_entities(names_by_cat, num_nonexisting_per_cat)
        for cat_name, cat in names_by_cat.items():
            print()
            print(cat_name)
            print("nonexisting:", cat["nonexisting"])
            print()

        save_and_augment(names_by_cat_with_steps)

    if start_step(4, names_by_cat_with_steps["steps_completed"]):
        generate_keystring_variations(names_by_cat, n=3)
        for cat_name, cat in names_by_cat.items():
            print()
            print(cat_name)
            print("nonexisting:", cat["nonexisting"])
            print()

        save_and_augment(names_by_cat_with_steps)

    # Step 5- convert to dataframe
    if start_step(5, names_by_cat_with_steps["steps_completed"]):
        df_keystrings = convert_to_df(names_by_cat)

        df_save_path = files_dir / "keystrings.csv"
        df_keystrings.to_csv(df_save_path, index=False)
        print(f"Saved dataframe to {df_save_path}")
        names_by_cat_with_steps["df_keystrings"] = df_keystrings
        save_and_augment(names_by_cat_with_steps)

    # Step 6- get embeddings
    if start_step(6, names_by_cat_with_steps["steps_completed"]):
        keystrings = list(df_keystrings["keystring"].values[0:])
        embeddings = request_embedding(keystrings, model="text-embedding-ada-002")
        df_keystrings["embedding"] = embeddings

        df_save_path = files_dir / "keystrings.csv"
        df_keystrings.to_csv(df_save_path, index=False)
        print(f"Saved dataframe to {df_save_path}")
        names_by_cat_with_steps["df_keystrings"] = df_keystrings
        save_and_augment(names_by_cat_with_steps)

    # Step 7- get distances
    if start_step(7, names_by_cat_with_steps["steps_completed"]):
        df_distances = get_all_distances(df_keystrings)

        df_save_path = files_dir / "distances.csv"
        df_distances.to_csv(df_save_path)
        print(f"Saved dataframe to {df_save_path}")
        names_by_cat_with_steps["df_distances"] = df_distances
        save_and_augment(names_by_cat_with_steps)

    # Step 8- analyze distances
    if start_step(8, names_by_cat_with_steps["steps_completed"]):
        df_analysis = get_analysis_df(df_keystrings, df_distances)

        df_save_path = files_dir / "analysis.csv"
        df_analysis.to_csv(df_save_path)
        print(f"Saved dataframe to {df_save_path}")
        names_by_cat_with_steps["df_analysis"] = df_analysis
        save_and_augment(names_by_cat_with_steps)

    # Step 9- plot analysis
    if start_step(9, names_by_cat_with_steps["steps_completed"]):
        fig = plot_analysis(df_analysis)

        fig_save_path = files_dir / "analysis.png"
        fig.savefig(fig_save_path)
        print(f"Saved figure to {fig_save_path}")
        names_by_cat_with_steps["fig_analysis"] = fig
        save_and_augment(names_by_cat_with_steps)

    # # Step 7
    # plot_analysis(analysis_results)
    # Step 8
    # optimal_threshold = determine_optimal_threshold(analysis_results)


if __name__ == "__main__":
    construct_strategy(profile="llm_v1")


# """
# If the name is followed by a phrase in parentheses, this phrase adds context to the name. For example, if the name is "John (brother)", then the context is "my brother".
# This context should be used to relevant variations of the name.
# """


#                 df.append(
#                 {
#                 'category': cat_name,
#                 'base': name,
#                 'keystring': name,
#                 'type': mode,
#                 'variation': False,
#                 'existing': True,
#                 'groups': name_dict['groups'],
#                 'description': name_dict.get('description', None),
#                 },
#                 ignore_index=True)
#                 for v_name in name_dict['variations']:
#                     df.append(
#                         {
#                         'category': cat_name,
#                         'base': name,
#                         'keystring': v_name,
#                         'type': mode,
#                         'variation': True,
#                         'existing': True,
#                         'groups': name_dict['groups'],
#                         'description': name_dict.get('description', None),
#                         },
#                         ignore_index=True)


# for cat_name, cat in names_by_cat.items():
#     for name, name_dict in cat['names'].items():
#         df.append(
#         {
#         'category': cat_name,
#         'base': name,
#         'keystring': name,
#         'type': 'name',
#         'variation': False,
#         'existing': True,
#         'groups': name_dict['groups'],
#         'description': name_dict.get('description', None),
#         },
#         ignore_index=True)
#         for v_name in name_dict['variations']:
#             df.append(
#                 {
#                 'category': cat_name,
#                 'base': name,
#                 'keystring': v_name,
#                 'type': 'name',
#                 'variation': True,
#                 'existing': True,
#                 'groups': name_dict['groups'],
#                 'description': name_dict.get('description', None),
#                 },
#                 ignore_index=True)

#     for group, group_dict in cat['groups'].items():
#         df.append(
#         {
#         'category': cat_name,
#         'base': group,
#         'keystring': group,
#         'type': 'group',
#         'variation': False,
#         'existing': True,
#         'groups': group_dict['groups'],
#         },
#         ignore_index=True)
#         for v_group in group_dict['variations']:
#             df.append(
#                 {
#                 'category': cat_name,
#                 'base': group,
#                 'keystring': v_group,
#                 'type': 'group',
#                 'variation': True,
#                 'existing': True,
#                 'names': group_dict['names'],
#                 },
#                 ignore_index=True)
