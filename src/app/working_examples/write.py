# import streamlit as st
import time
# st.write('Hello, *World!* :sunglasses:')
# st.write("example")

import streamlit as st

placeholder = st.empty()

# Try 4
time.sleep(1)
# Replace the chart with several elements:
with placeholder.container():
    st.write("This is one element")
    time.sleep(1)
    st.write("This is another")

time.sleep(0.01)
# adding small sleep seems to be nec: see https://discuss.streamlit.io/t/using-st-empty/29509
placeholder.empty()
time.sleep(1)
with placeholder.container():
    st.write("#2: This is one element")
    time.sleep(1)
    st.write("#2: This is another")

# # Replace the placeholder with some text:
# placeholder.text("Hello")

# time.sleep(1)
# # Replace the text with a chart:
# placeholder.line_chart({"data": [1, 5, 2, 6]})

# time.sleep(1)

# a = placeholder.markdown
# a("This is a test!!!!")
# time.sleep(1)

# Try 3
# current = st.container()
# current.write("This is one element")
# current.write("This is another")


# placeholder.write(current)
# time.sleep(1)

# current = st.container()
# current.write("2: This is one element")
# current.write("2: This is another")

# placeholder.write(current)

# Try 1
# # Replace the chart with several elements:
# with placeholder.container():
#     st.write("This is one element")
#     time.sleep(1)
#     st.write("This is another")
#     time.sleep(1)


# with placeholder.container():
#     st.write("#2: This is one element")
#     time.sleep(1)
#     st.write("#2: This is another")
#     time.sleep(1)

# Try 2
# placeholder.container(
#     st.write("This is one element"),
#     st.write("This is another")
# )

# time.sleep(1)


# placeholder.container(
#     st.write("2: This is one element"),
#     st.write("2: This is another")
# )


# Clear all those elements:
# placeholder.empty()
