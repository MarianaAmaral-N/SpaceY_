import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

print(spacex_df.head())
print(spacex_df.columns)
print(spacex_df['class'].value_counts())
print(spacex_df['Launch Site'].unique())



# Create a Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(id='site-dropdown',
                 options=[
                     {'label': 'All Sites', 'value': 'ALL'},
                     {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                     {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                     {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                     {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                 ],
                 value='ALL',
                 placeholder='Select a Launch Site',
                 searchable=True),
    
    html.Br(),

    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                    value=[min_payload, max_payload]),

    html.Br(),

    # Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    # Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# Pie chart callback
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        success_counts = (
            spacex_df[spacex_df['class'] == 1]['Launch Site']
            .value_counts()
            .reset_index()
        )
        success_counts.columns = ['Launch Site', 'Success Count']

        fig = px.pie(
            success_counts,
            values='Success Count',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
        return fig

    else:
        # Filtrar por site específico
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        outcome_counts = (
            filtered_df['class']
            .value_counts()
            .reset_index()
        )
        outcome_counts.columns = ['Outcome', 'Count']
        outcome_counts['Outcome'] = outcome_counts['Outcome'].replace({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            outcome_counts,
            names='Outcome',
            values='Count',
            title=f'Success vs Failure for site {entered_site}'
        )
        return fig




# Scatter chart callback
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              [Input('site-dropdown', 'value'),
               Input('payload-slider', 'value')])
def update_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) &
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch_Site'] == entered_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title=f'Payload vs. Outcome for {"all sites" if entered_site == "ALL" else entered_site}',
                     labels={'class': 'Launch Outcome'})
    return fig

# Run app
if __name__ == '__main__':
    app.run()
