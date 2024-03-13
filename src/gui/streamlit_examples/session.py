import streamlit as st

st.session_state["messages"] = []

msgs = st.session_state["messages"]

msgs.append("hello")

st.write(st.session_state)
