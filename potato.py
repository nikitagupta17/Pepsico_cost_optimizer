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
selected_plant = st.sidebar.selectbox('Select Plant', ['Pune', 'Channo', 'Kolkata', 'UP'], index=0)

# Filter data based on selections
filtered_df = filtered_df_by_season_and_region[filtered_df_by_season_and_region['Potato'] == selected_potato]

# Determine the destination plant with the least cost
cost_columns = ['Channo', 'Pune', 'Kolkata', 'UP']
destination_plant = filtered_df[cost_columns].idxmin(axis=1).values[0]
selected_plant_cost = round(filtered_df[selected_plant].values[0])
destination_plant_cost = round(filtered_df[destination_plant].values[0])
cost_difference = int(round(selected_plant_cost - destination_plant_cost))

# Breakdown costs
buying_rate = round(filtered_df['Buying Rate $/Ton'].values[0])
plant_loss = round(filtered_df['Plant Loss $/Ton'].values[0])
cold_store_loss = round(filtered_df['Cold Store Loss $/Ton'].values[0])
leno_bag_and_others = round(filtered_df['Leno Bag and Others $/Ton'].values[0])
transportation_cost_selected = round(filtered_df[f'Transportation cost {selected_plant}'].values[0])
transportation_cost_destination = round(filtered_df[f'Transportation cost {destination_plant}'].values[0])

# Resultant output table
result_table = pd.DataFrame({
    'BU': [selected_bu],
    'Plant to move': [selected_plant],
    'Destination Plant': [destination_plant],
    'Difference in Cost': [cost_difference]
})

st.subheader("Cost Analysis Summary")
st.write(result_table.to_html(index=False, border=0, classes='table table-striped'), unsafe_allow_html=True)

# Add space between the table and the insight text
st.markdown("<br>", unsafe_allow_html=True)

# Detailed text insight with markdown
if selected_plant == destination_plant:
    insight_text = f"""
    **Cost Analysis and Optimization Suggestion**
    
    You have selected **{selected_plant}**, which is currently the lowest-cost option among the available plants. 
    The total cost for **{selected_plant}** is **${selected_plant_cost}/ton**, which is lower compared to other plants.
    Therefore, no further cost optimization is possible with the given data.
    """
else:
    insight_text = f"""
    **Cost Analysis and Optimization Suggestion**

    By relocating production from **{selected_plant}** to **{destination_plant}**, the estimated cost savings are **${cost_difference}/ton**.

    The breakdown of costs at **{selected_plant}** includes:
    - Buying rate: **${buying_rate}**/ton
    - Plant loss: **${plant_loss}**/ton
    - Cold store loss: **${cold_store_loss}**/ton
    - Leno bag and others: **${leno_bag_and_others}**/ton
    - Transportation cost: **${transportation_cost_selected}**/ton
    - Total consumption cost at **{selected_plant}**: **${selected_plant_cost}/ton**
    
    Total consumption cost at **{destination_plant}**: **${destination_plant_cost}/ton**
    
    At **{destination_plant}**, the transportation cost is **${transportation_cost_destination}**/ton which is Comparatively lower than the transportation cost of **{selected_plant}**.
    
    This comprehensive cost analysis highlights the potential savings by considering all aspects of production and transportation costs. In the Business Unit (BU) of **{selected_bu}**, relocating operations from **{selected_plant}** to **{destination_plant}** could lead to significant savings. The savings in cost will amount to the difference between the total costs at these two plants, considering factors like buying rate, plant loss, cold store loss, leno bag and other costs, and transportation cost.

    **Final Summary:**
    Based on the analysis, it is suggested to move the plant from **{selected_plant}** to **{destination_plant}** to achieve a cost savings of **${cost_difference}**/ton. This decision is derived from the detailed cost breakdown and comparison of total costs, ensuring a more cost-effective production process.

    Please note that this analysis is based on the provided data and theoretical assumptions. In a real-world scenario, additional factors such as infrastructure, labor costs, regulations, and other variables need to be considered for a comprehensive analysis and accurate predictions regarding plant relocation.
    """

st.markdown(insight_text)

# Improved flow diagram with shades of blue
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

# Bar chart for potato prices
bar_fig = go.Figure()
for plant in cost_columns:
    bar_fig.add_trace(go.Bar(
        x=[plant],
        y=[filtered_df[plant].values[0]],
        name=plant
    ))

bar_fig.update_layout(title_text="Potato Prices per Plant", xaxis_title="Plant", yaxis_title="Price")
st.plotly_chart(bar_fig)

# Similar visualization to the provided image
regions = filtered_df_by_bu['Region'].unique()
avg_costs = [filtered_df_by_bu[filtered_df_by_bu['Region'] == region][cost_columns].mean().mean() for region in regions]

similar_fig = go.Figure(data=[
    go.Bar(name='Selected Region', x=regions, y=avg_costs)
])

similar_fig.update_layout(barmode='group', title_text="Average Cost per Ton in Different Regions", 
                          xaxis_title="Region", yaxis_title="Average Cost per Ton")
st.plotly_chart(similar_fig)
