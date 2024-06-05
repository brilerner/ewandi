# ewandi

In order to run the project, use the `environment.yml` file to install the required packages (`requirements.txt` should work too).

Then, open a terminal in src/gui and run the following command:
streamlit run app.py

This will allow you to run the app in your browser. You will get bugs, but see `example_streamlit_interaction_060424`.png for a sense of how things should work. To get a sense of what data is available, see `notebooks/data_tour.ipynb`.

The data that I'm using is stored in a cloud mongodb server. The `data/sim` contains the metadata used to construct the simulation.

The scripts that power everything are in `src`. 

- `analysis`: correlation of data; this is mainly still being workshopped
- `gui`: the streamlit application
- `llm`: all code related to chatbot functionality
- `server`: mongodb related functions
- `utils`: self-explanatory
- `viz`: visualization functions

My recommendation would be to start from app.py and work your way through the code. There's not a ton of documentation, but I'm happy to answer any questions you might have. There are no correlation functions implemented now, but it won't take much to do so (that's the last ~10% remaining to a MVP that's worth a damn).