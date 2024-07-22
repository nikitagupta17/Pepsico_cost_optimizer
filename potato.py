import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Load the dataset
file_path = 'potato_data.xlsx'
df = pd.read_excel(file_path)

# Clean the data
df.columns = df.columns.str.strip()
df.dropna(how='all', inplace=True)

# Rename columns to remove '_price'
df.rename(columns=lambda x: x.replace('_Price', ''), inplace=True)

# Streamlit dashboard
st.set_page_config(layout="wide")
st.title("Agro Dashboard")

# Sidebar filters
st.sidebar.header("Select filters")
selected_bu = st.sidebar.selectbox('Select Business Unit (BU)', df['BU'].unique())
filtered_df_by_bu = df[df['BU'] == selected_bu]
selected_season = st.sidebar.selectbox('Select Season', filtered_df_by_bu['Season'].unique())
selected_region = st.sidebar.selectbox('Select Region', filtered_df_by_bu['Region'].unique())
filtered_df_by_season_and_region = filtered_df_by_bu[(filtered_df_by_bu['Season'] == selected_season) & 
                                                     (filtered_df_by_bu['Region'] == selected_region)]
selected_potato = st.sidebar.selectbox('Select Potato', filtered_df_by_season_and_region['Potato'].unique())
selected_plant = st.sidebar.selectbox('Select Plant', ['Channo', 'Pune', 'Kolkata', 'UP'])

# Filter data based on selections
filtered_df = filtered_df_by_season_and_region[filtered_df_by_season_and_region['Potato'] == selected_potato]

# Determine the destination plant with the least cost
cost_columns = ['Channo', 'Pune', 'Kolkata', 'UP']
destination_plant = filtered_df[cost_columns].idxmin(axis=1).values[0]
selected_plant_cost = filtered_df[selected_plant].values[0]
destination_plant_cost = filtered_df[destination_plant].values[0]
cost_difference = int(round(selected_plant_cost - destination_plant_cost))

# Resultant output table
result_table = pd.DataFrame({
    'BU': [selected_bu],
    'Plant to move': [selected_plant],
    'Destination Plant': [destination_plant],
    'Difference in Cost': [cost_difference]
})

st.subheader("Optimization Results")
st.write(result_table.to_html(index=False, border=0, classes='table table-striped'), unsafe_allow_html=True)

st.write(f"By relocating production from {selected_plant} to the {destination_plant}, the estimated cost savings are ${cost_difference}/ton")

# Create layout with Sankey diagram on top and average cost graph below
col1, col2 = st.columns([2, 1])

with col1:
    # Improved Sankey Diagram
    flow_labels = ['Selected BU', 'Selected Season', 'Selected Region', 'Selected Potato', 'Channo Plant', 'Pune Plant', 'Kolkata Plant', 'UP Plant']
    flow_sources = [0, 1, 2, 3, 4, 4, 4, 4]  # Corrected source nodes
    flow_targets = [1, 2, 3, 4, 5, 6, 7, 8]  # Corrected target nodes
    flow_values = [1, 1, 1, 1, filtered_df['Channo'].values[0], filtered_df['Pune'].values[0],
                   filtered_df['Kolkata'].values[0], filtered_df['UP'].values[0]]  # Sample values

    colors = ['#004080', '#003366', '#00264d', '#001a33',  # Shades of blue for links
              '#004080', '#003366', '#00264d', '#001a33']  # Same shades for the nodes

    flow_sankey = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=flow_labels,
            color="#004080"  # Main color for the nodes
        ),
        link=dict(
            source=flow_sources,
            target=flow_targets,
            value=flow_values,
            color=colors
        )
    )])

    flow_sankey.update_layout(title_text="Potato Cost Flow Analysis", font_size=10, height=500)
    st.plotly_chart(flow_sankey, use_container_width=True)

with col2:
    # Remove second graph as per request
    pass

# Bar chart for potato prices
st.subheader("Cost Breakdown")

# Bar chart for potato prices
bar_fig = go.Figure()
for plant in cost_columns:
    bar_fig.add_trace(go.Bar(
        x=[plant],
        y=[filtered_df[plant].values[0]],
        name=plant
    ))

bar_fig.update_layout(title_text="Potato Prices per Plant", xaxis_title="Plant", yaxis_title="Price", height=400)
st.plotly_chart(bar_fig, use_container_width=True)
