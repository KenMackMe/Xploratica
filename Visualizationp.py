import streamlit as st
import altair as alt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import plotly.express as px


def multi_dimensional_data_explorer(df):
    """Tool to visualize high-dimensional data using PCA or t-SNE."""

    # Selecting the dimensionality reduction technique
    global reduced_df
    technique = st.selectbox("Select dimensionality reduction technique:", ["PCA", "t-SNE"])

    # Selecting features for analysis
    numeric_columns = df.select_dtypes(include='number').columns.tolist()

    if not numeric_columns:
        st.warning("No numeric columns available in the dataset. Please upload a dataset with numeric features.")
        return  # Exit the function if no numeric columns are found

    selected_features = st.multiselect("Select features for dimensionality reduction:", numeric_columns)

    # Optional: Selecting a target variable for coloring points
    target_variable = st.selectbox("Select a target variable for coloring (optional):",
                                   df.columns.tolist() + [None])

    if selected_features:
        # Prepare the data for PCA or t-SNE
        x = df[selected_features].dropna()

        # Check if we have enough samples and features
        if x.shape[0] < 2:
            st.warning("Not enough samples to perform dimensionality reduction.")
            return
        if x.shape[1] < 2:
            st.warning(
                "Not enough features to perform dimensionality reduction. Please select at least two features.")
            return

        if technique == "PCA":
            # Perform PCA
            pca = PCA(n_components=2)
            reduced_data = pca.fit_transform(x)
            reduced_df = pd.DataFrame(reduced_data, columns=['PC1', 'PC2'])

            # Display explained variance ratio in columns
            explained_variance = pca.explained_variance_ratio_
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="PC1 Explained Variance", value=f"{explained_variance[0]:.2%}")
            with col2:
                st.metric(label="PC2 Explained Variance", value=f"{explained_variance[1]:.2%}")

        elif technique == "t-SNE":
            # Perform t-SNE
            tsne = TSNE(n_components=2, random_state=42)
            reduced_data = tsne.fit_transform(x)
            reduced_df = pd.DataFrame(reduced_data, columns=['Dim1', 'Dim2'])

        # Add target variable for coloring if selected
        if target_variable:
            # Ensure the target variable aligns with the filtered data
            reduced_df['Target'] = df.loc[x.index, target_variable]

        # Create a scatter plot
        scatter_plot = alt.Chart(reduced_df).mark_circle(size=60).encode(
            x='PC1' if technique == "PCA" else 'Dim1',
            y='PC2' if technique == "PCA" else 'Dim2',
            color=alt.Color('Target:N', scale=alt.Scale(scheme='category10')) if target_variable else alt.value(
                "blue"),
            tooltip=['PC1', 'PC2'] if technique == "PCA" else ['Dim1', 'Dim2']
        ).properties(width=600, height=400)

        st.altair_chart(scatter_plot)

    pass


def customizable_aggregation_tool():
    if 'data' in st.session_state:
        df = st.session_state['data']
        # Step 1: Column Selection for Grouping
        group_by_columns = st.multiselect("Step 1: Select one or more columns to group by", df.columns.tolist())

        # Step 2: Column Selection for Aggregation
        numeric_columns = df.select_dtypes(include='number').columns.tolist()
        agg_columns = st.multiselect("Step 2: Select numeric columns to aggregate", numeric_columns)

        if not numeric_columns:
            st.warning("No numeric columns available in the dataset for aggregation. Please upload"
                       " a dataset with numeric features.")
            return  # Exit the function if no numeric columns are found

        # Step 3: Aggregation Function Selection
        agg_functions = st.multiselect("Step 3: Choose aggregation functions:",
                                       ["Sum", "Mean", "Count", "Min", "Max"])

        # Step 4: Grouping and Aggregation
        if group_by_columns and agg_columns and agg_functions:
            aggregated_results = []

            for func in agg_functions:
                if func == "Sum":
                    result = df.groupby(group_by_columns)[agg_columns].sum().reset_index()
                    result.columns = [*group_by_columns, *[f"{col}_sum" for col in agg_columns]]
                elif func == "Mean":
                    result = df.groupby(group_by_columns)[agg_columns].mean().reset_index()
                    result.columns = [*group_by_columns, *[f"{col}_mean" for col in agg_columns]]
                elif func == "Count":
                    result = df.groupby(group_by_columns)[agg_columns].count().reset_index()
                    result.columns = [*group_by_columns, *[f"{col}_count" for col in agg_columns]]
                elif func == "Min":
                    result = df.groupby(group_by_columns)[agg_columns].min().reset_index()
                    result.columns = [*group_by_columns, *[f"{col}_min" for col in agg_columns]]
                elif func == "Max":
                    result = df.groupby(group_by_columns)[agg_columns].max().reset_index()
                    result.columns = [*group_by_columns, *[f"{col}_max" for col in agg_columns]]

                aggregated_results.append(result)

            # Combine all aggregated results into one DataFrame
            aggregated_data = aggregated_results[0]
            for res in aggregated_results[1:]:
                aggregated_data = aggregated_data.merge(res, on=group_by_columns, how='outer')

            # Display aggregated data
            st.write("###### Aggregated Data (Pivot Table)")
            st.dataframe(aggregated_data)

            # Step 5: Visualization Options
            plot_type = st.selectbox("Step 4: Choose how to visualize the aggregated data:",
                                     ["None", "Bar Chart", "Line Chart"])

            # Bar Chart Visualization using Plotly
            if plot_type == "Bar Chart":
                st.write("#### Bar Chart Visualization")
                if group_by_columns and agg_columns:
                    # Automatically select the first available grouping and aggregation for the chart
                    bar_x = group_by_columns[0]
                    bar_y = [f"{agg}_sum" for agg in agg_columns]  # Adjust based on the aggregation type

                    # Generate Bar Chart Automatically
                    fig = px.bar(aggregated_data, x=bar_x, y=bar_y)
                    st.plotly_chart(fig)

            # Line Chart Visualization using Plotly
            elif plot_type == "Line Chart":
                st.write("#### Line Chart Visualization")
                if group_by_columns and agg_columns:
                    # Automatically select the first available grouping and aggregation for the chart
                    line_x = group_by_columns[0]
                    line_y = [f"{agg}_sum" for agg in agg_columns]  # Adjust based on the aggregation type

                    # Generate Line Chart Automatically
                    fig = px.line(aggregated_data, x=line_x, y=line_y, title=f"Line Chart of {line_y} by {line_x}")
                    st.plotly_chart(fig)

            # Download Option
            st.download_button("Download Aggregated Data", data=aggregated_data.to_csv(index=False),
                               mime='text/csv', file_name='aggregated_data.csv')

        else:
            st.write("Please select columns for grouping and aggregation.")


def box_plot(df):
    """Tool to visualize the distribution of a numeric feature using a box plot."""
    numeric_columns = df.select_dtypes(include='number').columns.tolist()
    if not numeric_columns:
        st.warning("No numeric columns available for box plot.")
        return

    st.subheader("Box Plot")
    feature = st.selectbox("Select a numeric feature for box plot:", numeric_columns)

    fig = px.box(df, y=feature, title=f'Box Plot of {feature}')
    st.plotly_chart(fig)


def density_plot(df):
    """Tool to visualize the density distribution of two numeric features."""
    numeric_columns = df.select_dtypes(include='number').columns.tolist()

    if len(numeric_columns) < 2:
        st.warning("Not enough numeric columns for density plot.")
        return

    st.subheader("Density Plot")

    # Allow user to select two numeric features for the density plot
    feature_x = st.selectbox("Select feature for X-axis:", numeric_columns)
    feature_y = st.selectbox("Select feature for Y-axis:", numeric_columns)

    # Create the density plot using density contour
    fig = px.density_contour(df, x=feature_x, y=feature_y, title=f'Density Plot of {feature_x} vs {feature_y}')

    # Display the plot in Streamlit
    st.plotly_chart(fig)


def additional_visualization_options(df):
    """Additional visualization options for the dataset."""
    if st.checkbox("Show Box Plot"):
        box_plot(df)
    elif st.checkbox("Show Density Plot"):
        density_plot(df)


def show_visual():
    if 'data' in st.session_state:
        df = st.session_state['data']

        tab1, tab2, tab3 = st.tabs(
            ["Multi-Dimensional Data Explorer", "Custom Aggregation Tool", "Additional Visualizations"])

        with tab1:
            multi_dimensional_data_explorer(df)

        with tab2:
            customizable_aggregation_tool()

        with tab3:
            additional_visualization_options(df)
    else:
        st.write("Please upload a dataset on the 'Upload' page.")
