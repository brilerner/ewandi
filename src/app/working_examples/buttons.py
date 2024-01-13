import streamlit as st

# imgs_dir = Path(__file__).resolve().parent.parent / "imgs"


# def augment(new_project):
#     if "intro_index" not in st.session_state:


st.session_state.intro_index = 0

if "intro_index" in st.session_state:
    if st.session_state.intro_index == 0:
        st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
    if st.session_state.intro_index == 1:
        st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
    if st.session_state.intro_index == 2:
        st.markdown("# The end!")


if st.button(
    "# <",
    key="prev",
):
    st.session_state.intro_index -= 1

if st.button("# >", key="next"):
    st.session_state.intro_index += 1


# st.columns([1, 1, 1])
# st.session_state.intro_index = 0

# if "intro_index" in st.session_state:
#     if st.session_state.intro_index == 0:
#         st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
#     if st.session_state.intro_index == 1:
#         st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
#     if st.session_state.intro_index == 2:
#         st.markdown("# The end!")


# if st.button(
#     "# <",
#     key="prev",
# ):
#     st.session_state.intro_index -= 1

# if st.button("# >", key="next"):
#     st.session_state.intro_index += 1
