import streamlit as st
import pandas as pd


# UPLOAD/LOAD DATA PAGE
def show_uploadpage():
    global df
    if 'data' in st.session_state:
        if st.button("Remove Current File"):
            # Clear the existing data
            del st.session_state['data']
            st.success("Current file removed. You can upload a new file.")
    st.title("Upload dataset")
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        st.dataframe(df)

        # Save df to session state to use in other pages
        st.session_state['data'] = df
        st.info("Dataset has been saved to session state. Go to the 'overview page' for more")
    else:
        if 'data' in st.session_state:
            df = st.session_state['data']
            st.write("Existing dataset loaded.")
            st.dataframe(df)

        else:
            st.write("No dataset uploaded yet.")
