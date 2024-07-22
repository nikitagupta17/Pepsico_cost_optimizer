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
    'Business Unit': [selected_bu],
    'Current Plant': [selected_plant],
    'Optimal Plant': [destination_plant],
    'Cost Savings': [cost_difference]
})

st.subheader("Optimization Results")
st.write(result_table.to_html(index=False, border=0, classes='table table-striped'), unsafe_allow_html=True)

st.write(f"By relocating production from {selected_plant} to the {destination_plant}, the estimated cost savings are ${cost_difference}/ton.")

# Improved flow diagram with a professional color scheme and filter nodes
flow_labels = [
    'Business Unit: ' + selected_bu, 
    'Season: ' + selected_season, 
    'Region: ' + selected_region, 
    'Potato Type: ' + selected_potato, 
    'Channo Cost', 
    'Pune Cost', 
    'Kolkata Cost', 
    'UP Cost'
]

# Creating a node mapping for easier reference
node_mapping = {label: index for index, label in enumerate(flow_labels)}

flow_sources = [
    node_mapping['Business Unit: ' + selected_bu],
    node_mapping['Season: ' + selected_season],
    node_mapping['Region: ' + selected_region],
    node_mapping['Potato Type: ' + selected_potato],
    node_mapping['Potato Type: ' + selected_potato],
    node_mapping['Channo Cost'],
    node_mapping['Pune Cost'],
    node_mapping['Kolkata Cost'],
    node_mapping['UP Cost'],
]

flow_targets = [
    node_mapping['Season: ' + selected_season],
    node_mapping['Region: ' + selected_region],
    node_mapping['Potato Type: ' + selected_potato],
    node_mapping['Channo Cost'],
    node_mapping['Pune Cost'],
    node_mapping['Kolkata Cost'],
    node_mapping['UP Cost']
]

flow_values = [
    1, 1, 1, 1, # Filter to next filter nodes
    filtered_df['Channo'].values[0],
    filtered_df['Pune'].values[0],
    filtered_df['Kolkata'].values[0],
    filtered_df['UP'].values[0],
]

colors = ['#0044cc', '#0033aa', '#002a80', '#001f66', '#001a52', '#001442', '#000d33', '#000820']

flow_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=flow_labels,
        color="royalblue"
    ),
    link=dict(
        source=flow_sources,
        target=flow_targets,
        value=flow_values,
        color=colors
    )
)])

flow_sankey.update_layout(title_text="Potato Cost Flow Analysis", font_size=10)
st.plotly_chart(flow_sankey)

# Additional visualizations filtered by BU
st.subheader("Cost Breakdown")

# Bar chart for potato prices
bar_fig = go.Figure()
for plant in cost_columns:
    bar_fig.add_trace(go.Bar(
        x=[plant],
        y=[filtered_df[plant].values[0]],
        name=plant,
        marker_color='royalblue'  # Using a consistent color tone
    ))

bar_fig.update_layout(title_text="Potato Prices per Plant", xaxis_title="Plant", yaxis_title="Price")
st.plotly_chart(bar_fig)

# Similar visualization to the provided image
regions = filtered_df_by_bu['Region'].unique()
avg_costs = [filtered_df_by_bu[filtered_df_by_bu['Region'] == region][cost_columns].mean().mean() for region in regions]

similar_fig = go.Figure(data=[
    go.Bar(name='Selected Region', x=regions, y=avg_costs, marker_color='royalblue')  # Consistent color tone
])

similar_fig.update_layout(barmode='group', title_text="Average Cost per Ton in Different Regions", 
                          xaxis_title="Region", yaxis_title="Average Cost per Ton")
st.plotly_chart(similar_fig)
