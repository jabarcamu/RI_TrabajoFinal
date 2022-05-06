# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd

from dash.dependencies import Input, Output, State

import plotly.graph_objects as go

# Create random data with numpy
import numpy as np

# herramienta para analisis de sentimientos
from textblob import TextBlob

# Expresiones regulares
import re


# Fechas
from datetime import datetime


# dataframe 
dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/covid19_tweets.csv')


totalPositive = None
totalNegative = None
totalNeutral = None


def text_preprocessing(s):
    """
    - Lowercase the sentence
    - Change "'t" to "not"
    - Remove "@name"
    - Isolate and remove punctuations except "?"
    - Remove other special characters
    - Remove stop words except "not" and "can"
    - Remove trailing whitespace
    """
    s = s.lower()
    # Change 't to 'not'
    s = re.sub(r"\'t", " not", s)
    # Remove @name
    s = re.sub(r'(@.*?)[\s]', ' ', s)
    # Isolate and remove punctuations except '?'
    s = re.sub(r'([\'\"\.\(\)\!\?\\\/\,])', r' \1 ', s)
    s = re.sub(r'[^\w\s\?]', ' ', s)
    # Remove some special characters
    s = re.sub(r'([\;\:\|•«\n])', ' ', s)
    # Remove trailing whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    
    return s

    
labels = ['Positivo','Negativo','Neutral']
values =[4120, 3600, 550]

# Use `hole` to create a donut-like pie chart
figpie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])




np.random.seed(1)
rng = np.random.default_rng()
N = 30
random_x = np.linspace(0, 1, N)
positive = 100 * rng.random((N)) + 100 # np.random.randn(N)
negative = 100 * rng.random((N)) + 100 # np.random.randn(N) - 1
neutral = 100 * rng.random((N)) + 100 # np.random.randn(N) - 1

figrandom = go.Figure()

# Add traces
figrandom.add_trace(go.Scatter(x=random_x, y=positive,
                    mode='lines',
                    name='Positivo'))
figrandom.add_trace(go.Scatter(x=random_x, y=negative,
                    mode='lines',
                    name='Negativo'))
figrandom.add_trace(go.Scatter(x=random_x, y=neutral,
                    mode='lines',
                    name='Neutral'))





app = Dash(__name__)

colors = {
    'background': '#987654',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

#dft = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')
dft = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

dfc = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

dfcountry = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

def generate_table(dataframe, max_rows=20):    
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])


figc = px.scatter(dfc, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)


fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)


dfstock = px.data.stocks()
figstock = px.line(dfstock, x='date', y="GOOG")




app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(
        children='Visual Analytics',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(children='Una aplicación web para el análisis de datos.', style={
        'textAlign': 'center',
        'color': colors['text']
    }),

    dcc.Graph(
        id='example-graph-2',
        figure=fig
    ),

    html.H4(children='US Agriculture Exports (2011)'),
    generate_table(dft),
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure=figc
    ),
    dcc.Graph(id='graph-with-slider'),
    dcc.Slider(
        dft['year'].min(),
        dft['year'].max(),
        step=None,
        value=dft['year'].min(),
        marks={str(year): str(year) for year in dft['year'].unique()},
        id='year-slider'
    ),
     html.Div([
            dcc.Dropdown(
                dfcountry['Indicator Name'].unique(),
                'Fertility rate, total (births per woman)',
                id='xaxis-column'
            )
        ], style={'width': '48%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                dfcountry['Indicator Name'].unique(),
                'Life expectancy at birth, total (years)',
                id='yaxis-column'
            )            
        ], style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
        dcc.Graph(id='indicator-graphic'),
        dcc.Slider(
        dfcountry['Year'].min(),
        dfcountry['Year'].max(),
        step=None,
        id='year--slider',
        value=dfcountry['Year'].max(),
        marks={str(year): str(year) for year in dfcountry['Year'].unique()},

    ),
    dcc.Graph(
        id='stock',
        figure=figstock
    ),
    dcc.Graph(
        id='output-timeline',
        # figure=figrandom
    ),
    dcc.Graph(
        id='output-pie',
        # figure=figpie
    ),
    html.I("TextBlob analisis sentimiento"),
    html.Br(),
    dcc.Input(id='input-1-state', type='text', value='Montréal'),    
    html.Button(id='submit-button-state', n_clicks=0, children='Calcular'),
    html.Div(id='output-state')


])


@app.callback(Output('output-state', 'children'),
              Output('output-pie', 'figure'),
              Output('output-timeline', 'figure'),
              Input('submit-button-state', 'n_clicks'),
              State('input-1-state', 'value'))
def update_output(n_clicks, input1):
    print('Ingresando al callback')

    global dfcovid
    global totalPositive
    global totalNegative
    global totalNeutral
    
    blob = TextBlob(input1)
    print(blob.sentiment)
    
    # obtener el dataset de covid19
   
    
        
    if n_clicks == 0:          
        print('No existe el dataframe') 

        # truncate los elementos del dataframe solo para pruebas
        # dfcovid =  dfcovid.truncate(before=0, after=100)
        rows = len(dfcovid.axes[0])
        print('rowssssssssssssss')
        print(rows)
        polarity = []
        subjectivity = []
        sentiment = []
        textprocessing = []
        fecha = []
        for index in range(rows):
            textfecha = dfcovid.loc[index, 'date']
            textfecha = textfecha.replace("-", "/")
            fechaval = datetime.strptime(textfecha, '%Y/%m/%d %H:%M:%S')
            fecha.append(fechaval)
            textproc = text_preprocessing(dfcovid.loc[index, 'text'])   
            textprocessing.append(textproc)   
            sentimental = TextBlob(textproc)
            pol = sentimental.sentiment.polarity
            polarity.append(pol) 
            subjectivity.append(sentimental.sentiment.subjectivity)
            val = 0 if (pol >= -0.25 and pol <= 0.25) else 1 if pol > 0.25 else -1
            sentiment.append(val)
              
            
            
        # adicionando nueva columna 
        dfcovid['polarity'] = polarity
        dfcovid['subjectivity'] = subjectivity
        dfcovid['sentiment'] = sentiment
        dfcovid['textprocessing'] = textprocessing
        dfcovid['fecha'] = fecha
        print('date')
        print(dfcovid.head(5)['date'])    
        print('fecha')
        print(dfcovid.head(5)['fecha'])                
        dfcovid = (dfcovid.sort_values(by=['fecha']))

        # dictionarios para los totales de las fechas
        if(totalPositive is None):
            print('None Positive')
            totalPositive = dict()
            print(totalPositive)
        if(totalNegative is None):
            print('None negative')
            totalNegative = dict()                
            print(totalNegative)
        if(totalNeutral is None):
            print('None Neutral')
            totalNeutral = dict()
            print(totalNeutral)

        print('Iingresando a los acumnuladores')
        for index in dfcovid.index:
            textfecha = dfcovid.loc[index, 'fecha']
            key = str(textfecha.year) + str(textfecha.month) + str(textfecha.day)            
            
            # positivo
            if dfcovid.loc[index, 'sentiment'] == 1:
                if not key in totalPositive:                
                    totalPositive[key] = {'date':dfcovid.loc[index, 'fecha'],'count': 0}
                totalPositive[key]['count'] = totalPositive.get(key).get('count') + 1  
            # negativo
            if dfcovid.loc[index, 'sentiment'] == -1:
                if not key in totalNegative:                
                    totalNegative[key] = {'date':dfcovid.loc[index, 'fecha'],'count': 0}
                totalNegative[key]['count'] = totalNegative.get(key).get('count') + 1  
            # neutro
            if dfcovid.loc[index, 'sentiment'] == 0:
                if not key in totalNeutral:                
                    totalNeutral[key] = {'date':dfcovid.loc[index, 'fecha'],'count': 0}
                totalNeutral[key]['count'] = totalNeutral.get(key).get('count') + 1  

        print('Imprimir acumulado ..')
        print('Positivo ..')
        print(totalPositive)
        print('negativo ..')
        print(totalNegative)
        print('Neutral ..')
        print(totalNeutral)
    

    # Grafica la linea de tiempo
    figtimeline = go.Figure()

    x_fecha_positive = []
    y_sentiment_positive = []
    for obj in totalPositive:        
        val = totalPositive[obj]
        x_fecha_positive.append(val['date'])
        y_sentiment_positive.append(val['count'])                
    
    x_fecha_negative = []
    y_sentiment_negative = []
    for obj in totalNegative:
        print(totalNegative[obj])
        val = totalNegative[obj]
        x_fecha_negative.append(val['date'])
        y_sentiment_negative.append(val['count'])  

    x_fecha_neutral = []
    y_sentiment_neutral = []
    for obj in totalNeutral:
        print(totalNeutral[obj])
        val = totalNeutral[obj]
        x_fecha_neutral.append(val['date'])
        y_sentiment_neutral.append(val['count'])  

    print('Listas de graficas...........')
    print(x_fecha_positive)
    print(y_sentiment_positive)
    print(x_fecha_negative)
    print(y_sentiment_negative)
    print(x_fecha_neutral)
    print(y_sentiment_neutral)
    # Add traces
    figtimeline.add_trace(go.Scatter(x=x_fecha_positive, y=y_sentiment_positive,
                        mode='lines',
                        name='Positivo'))
    figtimeline.add_trace(go.Scatter(x=x_fecha_negative, y=y_sentiment_negative,
                        mode='lines',
                        name='Negativo'))
    figtimeline.add_trace(go.Scatter(x=x_fecha_neutral, y=y_sentiment_neutral,
                        mode='lines',
                        name='Neutral'))


    print('sort date')
    print(dfcovid.head(5)['date'])    
    print('sort fecha')
    print(dfcovid.head(5)['fecha'])

    letter = '''I really enjoy programming in Python. It is a very approachable
    language with a plethora of valuable, high quality, libraries in
    both the standard library and as third party package from the
    community'''


    # calculando la suma de los sentimientos
    labels = ['Positivo','Negativo','Neutral']
    values =[0, 0, 0]
    for sentiment in dfcovid['sentiment']:
        if sentiment == 1 :
            values[0] += 1
        if sentiment ==  -1:
            values[1] += 1
        if sentiment == 0 :
            values[2] += 1


    # Use `hole` to create a donut-like pie chart
    figpie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])



    return  u'''
        The Button has been pressed {} times,
        Input 1 is "{}"        
    '''.format(n_clicks, input1) , figpie, figtimeline


@app.callback(
    Output('graph-with-slider', 'figure'),
    Input('year-slider', 'value'))
def update_figure(selected_year):
    filtered_df = dft[dft.year == selected_year]

    fig = px.scatter(filtered_df, x="gdpPercap", y="lifeExp",
                     size="pop", color="continent", hover_name="country",
                     log_x=True, size_max=55)

    fig.update_layout(transition_duration=100)

    return fig



@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),    
    Input('year--slider', 'value'))
def update_graph(xaxis_column_name, yaxis_column_name,year_value):
    dff = dfcountry[dfcountry['Year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
