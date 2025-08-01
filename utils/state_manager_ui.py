import streamlit as st
from state_manager import initialize_db, get_all_states, get_state, set_state, clear_state

# Initialize the database
initialize_db()

# Streamlit UI
st.title("State Manager UI")
st.sidebar.header("Actions")

# Sidebar options
action = st.sidebar.selectbox(
    "Choose an action:",
    ["View All States", "Get a Specific State", "Set a State", "Clear All States"]
)

if action == "View All States":
    st.header("View All States")
    states = get_all_states()
    if states:
        for key, value in states:
            st.write(f"**{key}**: {value}")
    else:
        st.write("No states found.")

elif action == "Get a Specific State":
    st.header("Get a Specific State")
    key = st.text_input("Enter the key:")
    if st.button("Get State"):
        value = get_state(key)
        if value:
            st.write(f"**Value for '{key}':** {value}")
        else:
            st.write(f"No value found for key '{key}'.")

elif action == "Set a State":
    st.header("Set a State")
    key = st.text_input("Enter the key:")
    value = st.text_input("Enter the value:")
    if st.button("Set State"):
        set_state(key, value)
        st.success(f"State '{key}' set to '{value}'.")

elif action == "Clear All States":
    st.header("Clear All States")
    if st.button("Clear States"):
        clear_state()
        st.success("All states cleared.")