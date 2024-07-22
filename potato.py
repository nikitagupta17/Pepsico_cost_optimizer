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
df.rename(columns=lambda x: x.replace('_Price', ' Plant'), inplace=True)

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


flow_labels = ['Consumption Cost', 'Channo Plant', 'Pune Plant', 'Kolkata Plant', 'UP Plant']
flow_values = [filtered_df['Channo'].values[0], filtered_df['Pune'].values[0], 
               filtered_df['Kolkata'].values[0], filtered_df['UP'].values[0]]

flow_sources = [0, 0, 0, 0]
flow_targets = [1, 2, 3, 4]

colors = ['#A3C2E2', '#7EB0E8', '#4A90E2', '#0033A0']

flow_sankey = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=flow_labels,
        color="blue"
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


regions = filtered_df_by_bu['Region'].unique()
avg_costs = [filtered_df_by_bu[filtered_df_by_bu['Region'] == region][cost_columns].mean().mean() for region in regions]

similar_fig = go.Figure(data=[
    go.Bar(name='Selected Region', x=regions, y=avg_costs)
])

similar_fig.update_layout(barmode='group', title_text="Average Cost per Ton in Different Regions", 
                          xaxis_title="Region", yaxis_title="Average Cost per Ton")
st.plotly_chart(similar_fig)
