import streamlit as st
from Overviewp import show_overviewp
from Visualizationp import show_visual
from uploadpage import show_uploadpage
from streamlit_option_menu import option_menu

# page configuration
st.set_page_config(page_title="Xploratica", layout="wide")

# Sidebar for navigation
with st.sidebar:
    page = option_menu("Navigate", ["Home", 'Upload', 'Overview', 'Visualization'],
                       icons=['house', 'upload', 'file-earmark-richtext', 'graph-down'], menu_icon="cast",
                       default_index=1)

if page == "Upload":
    # Import the upload page script
    show_uploadpage()

elif page == "Overview":
    # Import the overview page script
    show_overviewp()

elif page == "Visualization":
    show_visual()


if page == "Home":
    st.write("# Xploratica 🚀📈")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""user-friendly solution for exploring and analyzing datasets with ease. Designed with simplicity in 
    mind, it transforms complex datasets into clear, interactive visualizations, enabling users of any background to 
    swiftly interpret and derive valuable insights. With intuitive filtering and visualization options, 
    users can delve into their data effortlessly, without needing extensive technical knowledge. """)

    st.write("""1. Upload the Dataset 📤
     \nStart by uploading your data file directly into the app. This step sets up your 
    data for further analysis. 
    \n2. Overview 📊
     \nView an Overview Once the data is uploaded, you’ll get a summary overview 
    that includes key metrics and insights to help you quickly understand the structure and main features of your 
    dataset. 
    \n3. Visualise 📈
    \nFinally, use interactive charts to explore patterns 
    in your data, making it easier to derive meaningful insights visually.""")

