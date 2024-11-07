import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from st_keyup import st_keyup
import plotly.express as px


# rows, columns, missing values count.
def summary_statistics(df):
    """Display summary statistics in structured columns using st.metric."""

    # Calculate summary statistics
    num_rows = df.shape[0]
    num_cols = df.shape[1]
    missing_values = df.isnull().sum().sum()
    memory_usage = df.memory_usage(deep=True).sum() / 1024 ** 2  # Convert to MB

    # Create columns for summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Number of Rows", num_rows)

    with col2:
        st.metric("Number of Columns", num_cols)

    with col3:
        st.metric("Number of Missing Values", missing_values)

    with col4:
        st.metric("Memory Usage (MB)", round(memory_usage, 2))


# sidebar data filtering
def filter_dataframe(df):
    """Function to filter the DataFrame based on user input."""

    # Allow the user to select columns to filter
    selected_columns = st.multiselect("Select columns:", df.columns)

    # Dictionary to hold user input for filtering
    filter_values = {}

    for col in selected_columns:
        # Use st_keyup to get input for each selected column, maintaining state
        filter_value = st_keyup(f"Enter value for {col}:", key=col)

        if filter_value:
            filter_values[col] = filter_value

    # Initialize filtered DataFrame as the original DataFrame
    filtered_df = df

    # Filtering the DataFrame based on user-selected columns and their values
    for col, value in filter_values.items():
        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(value, case=False, na=False)]

    # Handle scenarios where no columns are selected
    if not selected_columns:
        st.warning("Please select at least one column to filter.")
    elif filtered_df.empty:
        st.warning("No matching rows found based on the provided filter values.")
    else:
        # Display the filtered DataFrame with only the selected columns
        st.write(filtered_df[selected_columns])


# top,the least category
def category_dist():
    global df
    if 'data' in st.session_state:
        df = st.session_state['data']
    # Category Distribution
    st.markdown("<h3 style='font-size: 18px;'>1. Quantitative data distribution</h3>", unsafe_allow_html=True)
    st.write("It represents continuous or discrete numerical data. Click the button below to view a summary.")
    # Button to toggle DataFrame description
    if 'show_description' not in st.session_state:
        st.session_state.show_description = False

    def toggle_description():
        st.session_state.show_description = not st.session_state.show_description

    st.button('Show' if not st.session_state.show_description else 'Hide', on_click=toggle_description)

    if st.session_state.show_description:
        histogram_numerical_data(df)
        numerical_stats(df)

    # Add "None" option to the select box
    st.write("")
    st.markdown("<h3 style='font-size: 18px;'>2. Categorical data distribution</h3>", unsafe_allow_html=True)
    st.write("It represents labels or names that classify data into different categories.")
    columns_with_none_option = ["None"] + df.columns.tolist()
    selected_column = st.selectbox("Select a column to view the top and least common categories",
                                   columns_with_none_option)

    if selected_column != "None":
        # TOP AND LEAST CATEGORIES
        if pd.api.types.is_categorical_dtype(df[selected_column]) or df[selected_column].dtype == object:
            top_categories = df[selected_column].value_counts().nlargest(5)
            least_categories = df[selected_column].value_counts().nsmallest(5)

            col7, col8 = st.columns(2)

            with col7:
                st.markdown(f"<h3 style='font-size: 18px;'>Top Categories</h3>", unsafe_allow_html=True)
                st.table(top_categories)

            with col8:
                st.markdown(f"<h3 style='font-size: 18px;'>Least Common Categories</h3>", unsafe_allow_html=True)
                st.table(least_categories)
            # Create a new section for categorical columns
            categorical_stats()
        else:
            st.write("Selected column is not categorical.")


# histogram after clicking show button


def histogram_numerical_data(df):
    """Display an interactive histogram for a selected column using Plotly with additional features."""
    numeric_columns = df.select_dtypes(include='number').columns.tolist()

    # Select a numeric column for the histogram
    selected_column = st.selectbox("Select a numeric column:", numeric_columns)

    if selected_column:
        # User input for the number of bins
        num_bins = st.slider("Select the number of bins:", min_value=5, max_value=100, value=35)

        # User input for bar color
        bar_color = st.color_picker("Pick a bar color:", "#636EFA")

        # Create an interactive histogram using Plotly
        fig = px.histogram(
            df,
            x=selected_column,
            nbins=num_bins,
            title=f'Histogram of {selected_column}',
            color_discrete_sequence=[bar_color],
            histnorm='probability'  # Optional: Normalize to show probability
        )

        # Update layout with more customization
        fig.update_traces(
            marker=dict(line=dict(width=1, color='black'))  # Add a black outline to the bars
        )

        # Optional: Add cumulative frequency line
        if st.checkbox("Show cumulative frequency"):
            fig.add_trace(
                px.histogram(df, x=selected_column, cumulative=True, nbins=num_bins).data[0]
            )

        # Update layout
        fig.update_layout(
            xaxis_title=selected_column,
            yaxis_title='Frequency',
            template='plotly_white',
            hovermode="x unified",
            bargap=0.1  # Gap between bars
        )

        # Display the Plotly chart in Streamlit
        st.plotly_chart(fig)


# statistics summary of numeric columns


def numerical_stats(df):
    """Display summary statistics for the selected numeric column."""
    # Select a numeric column from the dataframe
    numeric_columns = df.select_dtypes(include='number').columns.tolist()

    # Let the user select a column from numeric columns
    selected_column = st.selectbox("Select a numeric column for statistics:", numeric_columns)

    if selected_column:
        # Summary statistics for the selected column
        numeric_summary = df[selected_column].describe()

        # Display mean, median, standard deviation, minimum, and maximum for the selected column
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Mean", round(numeric_summary['mean'], 2))
        col2.metric(f"Median", round(numeric_summary['50%'], 2))
        col3.metric(f"Standard Deviation", round(numeric_summary['std'], 2))

        col1, col2, col3 = st.columns(3)
        col1.metric(f"Minimum", round(numeric_summary['min'], 2))
        col2.metric(f"Maximum", round(numeric_summary['max'], 2))
        col3.metric(f"Count", df[selected_column].count())  # Non-null count for the selected column


# statistics summary of category columns
def categorical_stats():
    if 'data' in st.session_state:
        df = st.session_state['data']

        # Toggle button for showing/hiding categorical statistics
        if 'show_categorical_stats' not in st.session_state:
            st.session_state.show_categorical_stats = False

        def toggle_categorical_stats():
            st.session_state.show_categorical_stats = not st.session_state.show_categorical_stats

        # Button to toggle visibility
        st.button('Show Categorical Stats' if not st.session_state.show_categorical_stats else 'Hide Categorical Stats',
                  on_click=toggle_categorical_stats)

        # Display the statistics if toggled on
        if st.session_state.show_categorical_stats:
            for col in df.select_dtypes(include=['object', 'category']):
                col1, col2, col3 = st.columns(3)
                mode_value = df[col].mode()[0]
                non_null_count = df[col].notnull().sum()
                col1.metric(f"Mode of '{col}'", mode_value)
                col2.metric(f"Non-Null Count of '{col}'", non_null_count)
                col3.metric(f"Unique Count of '{col}'", df[col].nunique())


# upload any dataset through online database reorientation
def database_interaction():

    db_url = st.text_input("Enter your database URL (e.g., sqlite:///my database.db):", "")
    if db_url:
        try:
            # Create a database engine
            engine = create_engine(db_url)
            connection = engine.connect()
            st.write("Database connection successful!")

            # Fetch and display table names
            query = "SELECT name FROM sqlite_master WHERE type='table';"  # Modify this query based on your database
            # type
            tables = pd.read_sql(query, connection)
            st.markdown("**Tables in the database:**")
            st.write(tables)

            # Close the connection
            connection.close()
        except Exception as e:
            st.error(f"Error connecting to database: {e}")


def show_overviewp():
    if 'data' in st.session_state:
        df = st.session_state['data']
        tab1, tab2, tab3, tab4 = st.tabs(["basic information", "data Distributions",
                                         "dataframe filtering", "database interaction"])
        with tab1:
            summary_statistics(df)
            st.markdown("<hr>", unsafe_allow_html=True)
            col9, col10 = st.columns(2)
            with col9:
                st.markdown("<h3 style='font-size: 18px;'>Columns: </h3>", unsafe_allow_html=True)
                st.write(df.columns.tolist())
            with col10:
                st.markdown("<h3 style='font-size: 18px;'>Column types: </h3>", unsafe_allow_html=True)
                st.write(df.dtypes.tolist())
        with tab2:
            category_dist()
        with tab3:
            filter_dataframe(df)
        with tab4:
            database_interaction()

        # st.info("Dataset loaded successfully")

    else:
        st.write("Please upload a dataset on the 'Upload page'.")
