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

# expresiones regulares
import re

# fechas
from datetime import datetime

# dataframe 
dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/covid19_tweets.csv')
 
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

totalPositive = None
totalNegative = None
totalNeutral = None

labels = ['Positivo','Negativo','Neutral']
values =[4120, 3600, 550]

# Use `hole` to create a donut-like pie chart
figpie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

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
# dft = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')

# dfc = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

# dfcountry = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

styleCard = {    
    'flex': 1, 
    'display': 'flex',
    # 'background-color':'green', 
    'align-items': 'center',
    'justify-content': 'center',        
    } 
styleButton = {
                'width': '50%',
                'height':'50px',
                'border-radius':'10px',                
            }
app.layout = html.Div([
html.Div(children=[
         html.H3(
            children='Configuraciones',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Label('Multi-Select Dropdown'),
        html.Br(),
        html.Label('Radio Items'),
    ], style={'padding': 10, 'flex': 25, 'background-color':'red'}),

    html.Div(children=[
        html.H1(
            children='Visual Analytics - Tweets Covid19',
            style={
                'textAlign': 'center',
                'color': colors['text']
            }
        ),
        html.Div(
        children=[
            html.Div(children=[
                html.Button(id="output-tweets", children='', style=styleButton)
            ],style=styleCard),
            html.Div(children=[
                html.Button(id="output-users",children='',style=styleButton)
            ],style=styleCard)
        ],
        style={'display': 'flex', 'flex-direction': 'row'}),

        dcc.Graph(
            id='output-timeline',
            # figure=figrandom
        ),
        dcc.Graph(
            id='output-pie',
            # figure=figpie
        ),
        html.Button(id='submit-button-state', n_clicks=0, children='Calcular'),
    ], style={'padding': 10, 'flex': 75})
], style={'display': 'flex', 'flex-direction': 'row'})



@app.callback(Output('output-pie', 'figure'),
              Output('output-timeline', 'figure'),
              Output('output-tweets', component_property='children'),
              Output('output-users', component_property='children'),
              Input('submit-button-state', 'n_clicks'))
def update_output(n_clicks):
    print('Ingresando al callback')

    global dfcovid
    global totalPositive
    global totalNegative
    global totalNeutral
    
    
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


    # numero de tweets
    tweets = str(len(dfcovid)) + ' tweets'

    # numero de usuarios
    users = str(len(dfcovid['user_name'].unique())) + ' usuarios'

    print(tweets)
    print(users)

    return  figpie, figtimeline, tweets, users




if __name__ == '__main__':
    app.run_server(debug=True)
