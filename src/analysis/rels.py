




def measure_relationship(events1, events2):

    df = pd.DataFrame(events1+events2)

    if df.name.nunique() != 2:
        print("ERROR: The two events must have different names.")
        
    # Step 1: Find the correlation between the two events