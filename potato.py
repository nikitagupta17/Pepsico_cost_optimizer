import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Load dataset
data = pd.read_csv('potato_sales.csv')

# Set page configuration for wide mode
st.set_page_config(layout="wide")

col1, col2 = st.columns([7,1])  # Adjust the width ratio to control spacing
with col2:
    st.image('ibm_logo.png', width=80)  # Adjust width as needed

with col1:
    st.image('pep_logo.jpg', width=100)  # Adjust width as needed

# Initialize session state for node selections
if 'selected_bu' not in st.session_state:
    st.session_state.selected_bu = 'India'  # Default selection
if 'selected_season' not in st.session_state:
    st.session_state.selected_season = None
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None
if 'selected_potato' not in st.session_state:
    st.session_state.selected_potato = None

# Check column names and adjust if necessary
def get_adjusted_column_name(df, name):
    # Find closest match for column names
    matches = [col for col in df.columns if name in col]
    return matches[0] if matches else None

# Function to generate nodes and links for the Sankey diagram
def generate_sankey_data(filtered_data):
    nodes = []
    links = []

    # Initial BU nodes
    if not st.session_state.selected_bu:
        bu_nodes = filtered_data['BU'].unique()
        nodes.extend(bu_nodes)
        return nodes, links

    # BU selected, show Seasons
    if st.session_state.selected_bu:
        bu_nodes = [st.session_state.selected_bu]
        nodes.extend(bu_nodes)
        bu_node_index = 0
        
        seasons = filtered_data['Season'].unique()
        season_node_indices = {season: i + 1 for i, season in enumerate(seasons)}
        nodes.extend(seasons)
        
        for season in seasons:
            links.append(dict(source=bu_node_index, target=season_node_indices[season], value=1))
        
        if st.session_state.selected_season:
            regions = filtered_data[filtered_data['Season'] == st.session_state.selected_season]['Region'].unique()
            region_node_indices = {region: i + 1 + len(seasons) for i, region in enumerate(regions)}
            nodes.extend(regions)
            
            for region in regions:
                links.append(dict(source=season_node_indices[st.session_state.selected_season], target=region_node_indices[region], value=1))
            
            if st.session_state.selected_region:
                potatoes = filtered_data[filtered_data['Region'] == st.session_state.selected_region]['Potato'].unique()
                potato_node_indices = {potato: i + 1 + len(seasons) + len(regions) for i, potato in enumerate(potatoes)}
                nodes.extend(potatoes)
                
                for potato in potatoes:
                    links.append(dict(source=region_node_indices[st.session_state.selected_region], target=potato_node_indices[potato], value=1))
                
                if st.session_state.selected_potato:
                    plants = ['Pune Plant', 'Channo Plant', 'Kolkata Plant', 'UP Plant']
                    plant_node_indices = {plant: i + 1 + len(seasons) + len(regions) + len(potatoes) for i, plant in enumerate(plants)}
                    nodes.extend(plants)
                    
                    for plant in plants:
                        plant_name = plant.split()[0]  # Extract the plant name (e.g., 'Pune')
                        consumption_column = f'Consumption_Cost_{plant_name}'
                        if consumption_column in filtered_data.columns:
                            avg_cost = filtered_data[filtered_data['Potato'] == st.session_state.selected_potato][consumption_column].mean()
                            links.append(dict(source=potato_node_indices[st.session_state.selected_potato], target=plant_node_indices[plant], value=avg_cost))
    
    return nodes, links

# Function to render the Sankey diagram
def render_sankey(nodes, links):
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=nodes
        ),
        link=dict(
            source=[link['source'] for link in links],
            target=[link['target'] for link in links],
            value=[link['value'] for link in links],
            color='rgba(0, 128, 255, 0.4)'
        )
    )])
    
    fig.update_layout(title_text="Consumption Cost Flow ", font_size=10)
    return fig

# Streamlit app layout
st.title("Agro Dashboard")

# Define tabs with increased font size
tab1, tab2, tab3, tab4, tab5 = st.tabs(["**Consumption Cost**", "**Buying Rate**", "**Plant Loss**", "**Cold Store Loss**", "**Leno Bag & Others**"])

with tab1:
    st.subheader("**Consumption Cost ($/Ton)**")

    # Define filter options
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        bu_options = data['BU'].unique()
        selected_bu = st.selectbox("**BU**", options=[''] + list(bu_options), index=bu_options.tolist().index('India') + 1)
    with col2:
        selected_season = st.selectbox("**Season**", options=[''] + list(data[data['BU'] == selected_bu]['Season'].unique()) if selected_bu else [])
    with col3:
        selected_region = st.selectbox("**Region**", options=[''] + list(data[data['Season'] == selected_season]['Region'].unique()) if selected_season else [])
    with col4:
        selected_potato = st.selectbox("**Potato**", options=[''] + list(data[data['Region'] == selected_region]['Potato'].unique()) if selected_region else [])

    # Update session state based on selections
    st.session_state.selected_bu = selected_bu
    st.session_state.selected_season = selected_season
    st.session_state.selected_region = selected_region
    st.session_state.selected_potato = selected_potato

    # Filter data based on selections
    filtered_data = data[
        (data['BU'] == st.session_state.selected_bu if st.session_state.selected_bu else data['BU'].notna()) &
        (data['Season'] == st.session_state.selected_season if st.session_state.selected_season else data['Season'].notna()) &
        (data['Region'] == st.session_state.selected_region if st.session_state.selected_region else data['Region'].notna()) &
        (data['Potato'] == st.session_state.selected_potato if st.session_state.selected_potato else data['Potato'].notna())
    ]

    # Generate Sankey data
    nodes, links = generate_sankey_data(filtered_data)

    # Layout for Sankey diagram and cost table
    col1, col2 = st.columns([2, 1])
    with col1:
        # Render Sankey diagram
        sankey_fig = render_sankey(nodes, links)
        st.plotly_chart(sankey_fig)

    with col2:
        if selected_potato:
            st.write("**Cost for Each Plant:**")
            plant_costs = []
            for plant in ['Pune Plant', 'Channo Plant', 'Kolkata Plant', 'UP Plant']:
                plant_name = plant.split()[0]
                consumption_column = f'Consumption_Cost_{plant_name}'
                if consumption_column in filtered_data.columns:
                    cost = filtered_data[filtered_data['Potato'] == selected_potato][consumption_column].mean()
                    plant_costs.append([plant, f"${cost:.2f} per ton"])
            
            #st.table(pd.DataFrame(plant_costs, columns=["Plant", "Cost"]).style.set_properties(**{'font-size': '12px'}).hide_index())
            df = pd.DataFrame(plant_costs, columns=["Plant", "Cost"])

            # Convert DataFrame to HTML and display using st.write()
            html_table = df.to_html(index=False, border=0, classes='table table-striped')
            st.write(html_table, unsafe_allow_html=True)

    if selected_potato:
        # Optimized result and insights
        st.subheader("**Optimized Result and Insight Generation**")
        selected_plant = st.selectbox("**Select Plant**", options=[''] + ['Pune Plant', 'Channo Plant', 'Kolkata Plant', 'UP Plant'])
        if selected_plant:
            selected_plant_name = selected_plant.split()[0]
            selected_plant_cost = filtered_data[f'Consumption_Cost_{selected_plant_name}'].mean()
            lowest_cost = min(filtered_data[f'Consumption_Cost_{plant.split()[0]}'].min() for plant in ['Pune Plant', 'Channo Plant', 'Kolkata Plant', 'UP Plant'])
            destination_plant = next(plant for plant in ['Pune Plant', 'Channo Plant', 'Kolkata Plant', 'UP Plant'] if filtered_data[f'Consumption_Cost_{plant.split()[0]}'].min() == lowest_cost)

            # Fetch transportation costs
            transportation_cost_selected = filtered_data[get_adjusted_column_name(filtered_data, f'Transportation cost {selected_plant_name}')].mean()
            transportation_cost_destination = filtered_data[get_adjusted_column_name(filtered_data, f'Transportation cost {destination_plant.split()[0]}')].mean()
            total_cost_selected = selected_plant_cost + transportation_cost_selected
            total_cost_destination = lowest_cost + transportation_cost_destination

            # Create insights DataFrame
            insights_df = pd.DataFrame({
                'BU': [st.session_state.selected_bu],
                'Plant to Move': [selected_plant],
                'Destination Plant': [destination_plant],
                'Difference ($/Ton)': [total_cost_selected - total_cost_destination]
            })

            st.write(insights_df.to_html(index=False, border=0, classes='table table-striped'), unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            if selected_plant == destination_plant:
                st.write("The selected plant is already the lowest-cost option. No further cost optimization is possible.")
            else:
                st.write(f"At **{destination_plant}**, the transportation cost is **${transportation_cost_destination:.2f}**/ton which is comparatively lower than the transportation cost of **{selected_plant}**.")
                st.write(f"This comprehensive cost analysis highlights the potential savings by considering all aspects of production and transportation costs. In the Business Unit (BU) of **{st.session_state.selected_bu}**, relocating operations from **{selected_plant}** to **{destination_plant}** could lead to significant savings. The savings in cost will amount to the difference between the total costs at these two plants, considering factors like buying rate, plant loss, cold store loss, leno bag and other costs, and transportation cost.")
                st.write(f"**Final Summary:** Based on the analysis, it is suggested to move the plant from **{selected_plant}** to **{destination_plant}** to achieve a cost savings of **${total_cost_selected - total_cost_destination:.2f}**/ton. This decision is derived from the detailed cost breakdown and comparison of total costs, ensuring a more cost-effective production process.")
                st.write("Please note that this analysis is based on the provided data and theoretical assumptions. In a real-world scenario, additional factors such as infrastructure, labor costs, regulations, and other variables need to be considered for a comprehensive analysis and accurate predictions regarding plant relocation.")

with tab2:
    st.subheader("Buying Rate ($/Ton)")
    st.dataframe(data[['Potato', 'Buying Rate $/Ton']])

with tab3:
    st.subheader("Plant Loss ($/Ton)")
    st.dataframe(data[['Potato', 'Plant Loss $/Ton']])

with tab4:
    st.subheader("Cold Store Loss ($/Ton)")
    st.dataframe(data[['Potato', 'Cold Store Loss $/Ton']])

with tab5:
    st.subheader("Leno Bag & Others ($/Ton)")
    st.dataframe(data[['Potato', 'Leno Bag and Others $/Ton']])
