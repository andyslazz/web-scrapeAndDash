import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

# Initializing the Dash app
app = dash.Dash(__name__, external_stylesheets=['https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css'])

# Loading and cleaning the data from .xlsx file
df = pd.read_excel('cleaned-data.xlsx', engine='openpyxl')

# Ensuring tuition fees are numeric, handling any non-numeric values
df['ค่าใช้จ่ายต่อเทอม'] = pd.to_numeric(df['ค่าใช้จ่ายต่อเทอม'], errors='coerce')

# Calculating average tuition fees by university
avg_tuition = df.groupby('มหาวิทยาลัย')['ค่าใช้จ่ายต่อเทอม'].mean().reset_index()
avg_tuition = avg_tuition.sort_values('ค่าใช้จ่ายต่อเทอม', ascending=False)

# Creating a bar chart for average tuition fees
bar_fig = px.bar(
    avg_tuition,
    x='มหาวิทยาลัย',
    y='ค่าใช้จ่ายต่อเทอม',
    title='Average Tuition Fees per Semester by University',
    labels={'ค่าใช้จ่ายต่อเทอม': 'Average Tuition (THB)', 'มหาวิทยาลัย': 'University'},
    height=500
)
bar_fig.update_layout(xaxis_tickangle=45, font=dict(size=12))

# Creating a pie chart for program type distribution
program_type_counts = df['ประเภทหลักสูตร'].value_counts().reset_index()
program_type_counts.columns = ['ประเภทหลักสูตร', 'Count']
pie_fig = px.pie(
    program_type_counts,
    names='ประเภทหลักสูตร',
    values='Count',
    title='Distribution of Program Types',
    height=400
)
pie_fig.update_traces(textinfo='percent+label', textfont_size=12)

# Finding the most expensive program for the interesting fact
most_expensive = df.loc[df['ค่าใช้จ่ายต่อเทอม'].idxmax()]
interesting_fact = f"The most expensive program is {most_expensive['ชื่อหลักสูตร']} at {most_expensive['มหาวิทยาลัย']} ({most_expensive['วิทยาเขต']}), costing {most_expensive['ค่าใช้จ่ายต่อเทอม']:.2f} THB per semester."

# Defining the layout of the dashboard
app.layout = html.Div(className='container mx-auto p-4', children=[
    html.H1('Thai University Engineering Programs Dashboard', className='text-3xl font-bold text-center mb-6'),
    
    # Displaying the interesting fact
    html.Div([
        html.H2('Interesting Fact', className='text-xl font-semibold mb-2'),
        html.P(interesting_fact, className='text-gray-700')
    ], className='mb-6'),
    
    # Bar chart for average tuition fees
    html.Div([
        dcc.Graph(id='bar-chart', figure=bar_fig)
    ], className='mb-6'),
    
    # Pie chart for program type distribution
    html.Div([
        dcc.Graph(id='pie-chart', figure=pie_fig)
    ], className='mb-6'),
    
    # Data table
    html.Div([
        html.H2('Program Details', className='text-xl font-semibold mb-2'),
        dash.dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left', 'fontSize': 12},
            style_header={'backgroundColor': '#f1f5f9', 'fontWeight': 'bold'}
        )
    ])
])

# Running the server
if __name__ == '__main__':
    app.run(debug=True)