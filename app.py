# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from tweetaio import TweetAIO

import json
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

pd.set_option('display.max_colwidth', None)

# dataframe 
# 68 MB
dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/covid19_tweets.csv')

# 90 MB
# dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/vaccination_all_tweets.csv')

# 13 MB
# dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/consolidado.tsv', sep='\t')

## 
## Apr 2014 May 2014 Jun 2014 Jul 2014 Aug 2014 Sep 2014 Oct 2014 Nov 2014 Dec 2014 Jan 2015 Feb 2015 Mar 2015 Apr 2015 
##        7       64      100      226      528     1070     1112      763      562      431      306      277      186

objectMonth = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
    
}
def text_preprocessing(s):
    # val = 'string'
    # if type(s) != type(val) :
    #     s = ''
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
    'backDashboard': '#B7CADB',
    'text': '#251D3A',
    'backConfig': '#E8E9ED',
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
    'padding': '15px'  
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
        
        
        html.Br(),
        html.Label('Inicio - fin de fechas'),
        dcc.DatePickerRange(
            id='my-date-picker-range',
            min_date_allowed=datetime(1995, 8, 5),
            max_date_allowed=datetime(2022, 12, 12),
            initial_visible_month=datetime(2022, 5, 7),
            start_date=datetime(2021, 1, 1),
            end_date=datetime(2022, 5, 7)
        ),
        
 

    ], style={'padding': 10, 'flex': 25, 'background-color':colors['backConfig']}),

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
        html.Div(children=[
            dcc.Graph(
            id='output-pie',
            # figure=figpie
        ),
            dcc.Graph(
                id='output-pie-subjetivity',
                # figure=figpie
            ),
        ]),
        html.Hr(),
        # html.Pre(id='click-data'),  
        html.Div(id='output-tweet'), 
        html.Button(id='submit-button-state', n_clicks=0, children='Calcular'),
    ], style={'padding': 10, 'flex': 75, 'background':colors['backDashboard']})
], style={'display': 'flex', 'flex-direction': 'row'})


def castToDateI(strDate):
    values = strDate.split()
    day = int(values[2])
    month = objectMonth[values[1]]     
    year = int(values[5])
    val = values[3].split(':')
    hour = int(val[0])
    minute = int(val[1])
    second = int(val[2])     
    return datetime(year, month, day, hour, minute, second, microsecond=0)
def castToDateII(strDate):
    textfecha = strDate.replace("-", "/")
    return datetime.strptime(textfecha, '%Y/%m/%d %H:%M:%S')

@app.callback(
              Output('output-pie-subjetivity', 'figure'),
              Output('output-pie', 'figure'),
              Output('output-timeline', 'figure'),
              Output('output-tweets', component_property='children'),
              Output('output-users', component_property='children'),
              Input('submit-button-state', 'n_clicks'))
def update_output(n_clicks):
    

    global dfcovid
    global totalPositive
    global totalNegative
    global totalNeutral
    
    
    # obtener el dataset de covid19
           
    if n_clicks == 0:          
        print('No existe el dataframe') 

        # truncate los elementos del dataframe solo para pruebas
        # dfcovid =  dfcovid.truncate(before=0, after=30000)
        # dfcovid =  dfcovid.truncate(before=0, after=100)
        rows = len(dfcovid.axes[0])                
        polarity = []
        subjectivity = []
        sentiment = []
        textprocessing = []
        fecha = []
        for index in range(rows):
            # print(dfcovid.loc[index, 'date'])
            textfecha = dfcovid.loc[index, 'date']
            # textfecha = dfcovid.loc[index, 'created_at']
            # textfecha = textfecha.replace("-", "/")
            # fechaval = datetime.strptime(textfecha, '%Y/%m/%d %H:%M:%S')
            fechaval = castToDateII(textfecha)                   
            fecha.append(fechaval)
            textproc = text_preprocessing(dfcovid.loc[index, 'text'])               
            textprocessing.append(textproc)   
            sentimental = TextBlob(textproc)
            pol = sentimental.sentiment.polarity
            polarity.append(pol) 
            subjectivity.append(sentimental.sentiment.subjectivity)
            # val = 0 if (pol >= -0.25 and pol <= 0.25) else 1 if pol > 0.25 else -1            
            val = 0 if pol == 0 else (-1 if pol < 0 else 1)            
            sentiment.append(val)
              
            
            
        # adicionando nueva columna 
        dfcovid['polarity'] = polarity
        dfcovid['subjectivity'] = subjectivity
        dfcovid['sentiment'] = sentiment
        dfcovid['textprocessing'] = textprocessing
        dfcovid['fecha'] = fecha
        
        print('***************************')
        print(dfcovid.head(1)['text'])
        


        print('date')
        print(dfcovid.head(5)['date'])    
        print('fecha')
        print(dfcovid.head(5)['fecha'])                
        dfcovid = (dfcovid.sort_values(by=['fecha']))

        # dictionarios para los totales de las fechas
        if(totalPositive is None):            
            totalPositive = dict()
            
        if(totalNegative is None):            
            totalNegative = dict()                

        if(totalNeutral is None):
            totalNeutral = dict()            

        
        for index in dfcovid.index:
            textfecha = dfcovid.loc[index, 'fecha']   
            textfecha = textfecha.replace(hour=0, minute=0, second=0, microsecond=0)          
            key = str(textfecha.year) + str(textfecha.month) + str(textfecha.day)                        
            # positivo
            if dfcovid.loc[index, 'sentiment'] == 1:
                if not key in totalPositive:                
                    totalPositive[key] = {'date':textfecha,'obj': []}
                totalPositive.get(key).get('obj').append(index)
                 
            # negativo
            if dfcovid.loc[index, 'sentiment'] == -1:
                if not key in totalNegative:                
                    totalNegative[key] = {'date':textfecha,'obj': []}
                totalNegative.get(key).get('obj').append(index)
                
            # neutro
            if dfcovid.loc[index, 'sentiment'] == 0:
                if not key in totalNeutral:                
                    totalNeutral[key] = {'date':textfecha,'obj': []}
                totalNeutral.get(key).get('obj').append(index)

    print('Imprimiendo los totales agrupados')    

    # Grafica la linea de tiempo
    figtimeline = go.Figure()

    print('Positivo')
    x_fecha_positive = []
    y_sentiment_positive = []
    for obj in totalPositive:                
        val = totalPositive[obj]        
        x_fecha_positive.append(val['date'])
        y_sentiment_positive.append(len(val['obj']))                
    
    print('Negativo')
    x_fecha_negative = []
    y_sentiment_negative = []
    for obj in totalNegative:        
        val = totalNegative[obj]        
        x_fecha_negative.append(val['date'])
        y_sentiment_negative.append(len(val['obj']))  

    print('Neutral')
    x_fecha_neutral = []
    y_sentiment_neutral = []
    for obj in totalNeutral:        
        val = totalNeutral[obj]        
        x_fecha_neutral.append(val['date'])
        y_sentiment_neutral.append(len(val['obj']))  

    print('Listas de graficas...........')
    # print(x_fecha_positive)
    # print(y_sentiment_positive)
    # print(x_fecha_negative)
    # print(y_sentiment_negative)
    # print(x_fecha_neutral)
    # print(y_sentiment_neutral)
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
    print('sort subjetividad')
    print(dfcovid.head(5)['subjectivity'])
    letter = '''I really enjoy programming in Python. It is a very approachable
    language with a plethora of valuable, high quality, libraries in
    both the standard library and as third party package from the
    community'''


    # calculando la suma de los sentimientos
    labels = ['Positivo','Negativo','Neutral']
    values =[0, 0, 0]
    labelsSubjectivity = ['Objetivo','Subjetivo']
    valuesSubjectivity = [0, 0]
    # for sentiment in dfcovid['sentiment']:
    #     if sentiment == 1 :
    #         values[0] += 1
    #     if sentiment ==  -1:
    #         values[1] += 1
    #     if sentiment == 0 :
    #         values[2] += 1

    # for i in range(len(dfcovid)) :
    for index, row in dfcovid.iterrows():
        # print (row["Name"], row["Age"])
        # Polarity
        if row['sentiment'] == 1 :
            values[0] += 1
        if row['sentiment'] ==  -1:
            values[1] += 1
        if row['sentiment'] == 0 :
            values[2] += 1
        # subjectivity
        if row['subjectivity'] == 0 :
            valuesSubjectivity[0] += 1
        if row['subjectivity'] > 0 :
            valuesSubjectivity[1] += 1
                        
        

    # Use `hole` to create a donut-like pie chart
    figpie = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

    # Use `hole` to create a donut-like pie chart
    figpiesubjetivity = go.Figure(data=[go.Pie(labels=labelsSubjectivity, values=valuesSubjectivity, hole=.3)])



    # numero de tweets
    tweets = str(len(dfcovid)) + ' tweets'

    # numero de usuarios
    users = str(len(dfcovid['user_name'].unique())) + ' usuarios'
    
    print(tweets)
    print(users)

    return  figpiesubjetivity, figpie, figtimeline, tweets, users


@app.callback(    
    Output('output-tweet', 'children'),
    Input('output-timeline', 'clickData'))
def display_click_data(clickData):
    print(clickData)
    resp = []
    if clickData is not None:        
        obj = clickData['points'][0]                
        numberTweets = 5
        listTweets = []
        textfecha = obj['x'].replace("-", "/")
        fechaval = datetime.strptime(textfecha, '%Y/%m/%d')
        key = str(fechaval.year) + str(fechaval.month) + str(fechaval.day)            
        # segun la grafica los indices de las graficas son:
        # 0 positivo    
        # 1 negativo
        # 2 neutral
        if obj['curveNumber'] == 0:                    
            objFecha = totalPositive[key]
            
            for i in range(numberTweets):
                # obteniendo el index
                index = objFecha['obj'][i]            
                listTweets.append({
                    'polarity':dfcovid.loc[index, 'polarity'],
                    'subjectivity':dfcovid.loc[index,'subjectivity'],
                    'sentiment':dfcovid.loc[index,'sentiment'],
                    'text':dfcovid.loc[index,'text'],
                    'fecha':dfcovid.loc[index,'fecha']
                    }                
                )
        if obj['curveNumber'] == 1:                    
            objFecha = totalNegative[key]
            
            for i in range(numberTweets):
                # obteniendo el index
                index = objFecha['obj'][i]            
                listTweets.append({
                    'polarity':dfcovid.loc[index, 'polarity'],
                    'subjectivity':dfcovid.loc[index,'subjectivity'],
                    'sentiment':dfcovid.loc[index,'sentiment'],
                    'text':dfcovid.loc[index,'text'],
                    'fecha':dfcovid.loc[index,'fecha']
                    }                
                )
        if obj['curveNumber'] == 2:                    
            objFecha = totalNeutral[key]
            
            for i in range(numberTweets):
                # obteniendo el index
                index = objFecha['obj'][i]            
                listTweets.append({
                    'polarity':dfcovid.loc[index, 'polarity'],
                    'subjectivity':dfcovid.loc[index,'subjectivity'],
                    'sentiment':dfcovid.loc[index,'sentiment'],
                    'text':dfcovid.loc[index,'text'],
                    'fecha':dfcovid.loc[index,'fecha']
                    }                
                )

        # return json.dumps(clickData, indent=1)                
        for j in listTweets:
            tweet = j                                                  
            resp.append(TweetAIO(tweet['text'],tweet['polarity'], tweet['subjectivity'], tweet['fecha']))
            resp.append(html.Hr())
    return html.Div(resp, style={'width':'80%'})




if __name__ == '__main__':
    app.run_server(debug=True)
