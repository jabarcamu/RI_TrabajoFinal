# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import math
from xml.sax.handler import feature_validation
from tweet import TweetAIO

import json
from dash import Dash, dcc, html, dash_table
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

# columnas del datatable
columns = ['Nombre','Tipo Dato','Minigráfico','Rango valores']
properties_labels = ['ID', 'Tweet', 'Idioma','Creación','Procedencia','Hashtags','Favoritos', 'Retweet','Fuente', 'Es retweet', 'Respuesta','status']
properties_names = ['id_str', 'text', 'lang','created_at','place','label','favorite_count', 'retweet_count','source', 'is_retweet','in_reply_to_screen_name','in_reply_to_status_id_str']
properties_type = ['string', 'string', 'string','date','string','string','Integer', 'Integer','string', 'Boolean','string','string']
properties_value = ['string', 'string', 'string','date','string','string','Integer', 'Integer','string', 'Boolean','string','string']

object_names = {   
    'id_str':'',
    'text':'',
    'lang':{'name':'', 'freq':0, 'total':0},
    'created_at':{'min':0,'max':0},
    'place':{'name':'', 'freq':0, 'total':0},
    'label':{'name':'', 'freq':0, 'total':0},
    'favorite_count':{'min':0,'max':0, 'count':0, 'mean':0},
    'retweet_count':{'min':0,'max':0, 'count':0, 'mean':0}, 
    'source':{'name':'', 'freq':0, 'total':0},
    'is_retweet':{'true':0,'false':0},    
    'in_reply_to_screen_name':'',
    'in_reply_to_status_id_str':''
    }

# objeto para el rango de fechas
objectDateTimeRange = {
    'min_date_allowed': datetime(1995, 8, 5),
    'max_date_allowed': datetime(2022, 12, 12),
    'initial_visible_month': datetime(2022, 5, 7),
    'start_date': datetime(2021, 1, 1),
    'end_date': datetime(2022, 5, 7)
}

# almacena los valores de los filtros
# rango de fechas
objectFilter = {
    'rangeDate':{'min':datetime.now(), 'max':datetime.now()},
    'polarity':{'positivo': True, 'negativo':True, 'neutral': True},
    'subjectivity':{'objetivo': True, 'subjetivo':True}
}

# contador principal
count = 0

# almacena informacion para el datatable - resumen inicial de los datos
dfDatatable = {}

# copia del dataframe original, para mostrar al usuario al aplicar los filtros
dfcovidcopy = {}

# permite mostrar informacion del dataframe con la totalidad de la data(sin limites de caracteres)
pd.set_option('display.max_colwidth', None)

# dataframe 
# 68 MB
# dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/covid19_tweets.csv')

# 90 MB
# dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/vaccination_all_tweets.csv')

# 13 MB
# dataset de fakenews, dataframe original
dfcovid = pd.read_csv('/home/arttrak/Projects/PythonProjects/Flask/consolidado.tsv', sep='\t')

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

# retorna un dataframe para el datatable
def generateDataTable():    
    
    

    data = {}

    for col in columns:
        data[col] = []

    
    for row in properties_labels:                
        data.get('Nombre').append(row)

    for row in properties_type:
        data.get('Tipo Dato').append(row)
    
    for row in properties_value:
        data.get('Rango valores').append(row)

    for col in columns:
        for row in properties_type:
            if col != 'Tipo Dato' and col != 'Nombre' and col != 'Rango valores':        
                data.get(col).append('')
                
    # crear y retornar dataframe
    return pd.DataFrame(data)

# actualizar los valores del dataframe del datatable, principalmente rango de valores
def updateDatatable(proper, listValues, df):

    for index in range(len(listValues)):
        df.at[index, proper] = listValues[index]            

# preprocesamiento del texto
def text_preprocessing(s):
    val = 'string'
    if type(s) != type(val) :
        s = ''
    """
    - Lowercase the sentence
    - Change "'t" to "not"
    - Remove "@name"
    - Isolate and remove punctuations except "?"
    - Remove other special characters
    - Remove stop words except "not" and "can"
    - Remove trailing whitespace
    """

    # s = s.lower()
    # # Change 't to 'not'
    # s = re.sub(r"\'t", " not", s)
    # # Remove @name
    # s = re.sub(r'(@.*?)[\s]', ' ', s)
    # # Isolate and remove punctuations except '?'
    # s = re.sub(r'([\'\"\.\(\)\!\?\\\/\,])', r' \1 ', s)
    # s = re.sub(r'[^\w\s\?]', ' ', s)
    # # Remove some special characters
    # s = re.sub(r'([\;\:\|•«\n])', ' ', s)
    # # Remove trailing whitespace
    # s = re.sub(r'\s+', ' ', s).strip()
    
    return s

# sentimientos de los tweets agrupados
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
        html.Label('Filtro por rango de fechas'),
        dcc.DatePickerRange(
            id='my-date-picker-range',            
            min_date_allowed=objectDateTimeRange['min_date_allowed'],
            max_date_allowed=objectDateTimeRange['max_date_allowed'],
            initial_visible_month=objectDateTimeRange['initial_visible_month'],
            start_date=objectDateTimeRange['start_date'],
            end_date=objectDateTimeRange['end_date']
        ),
        html.Hr(),
        html.Label('Filtro por Sentimientos'),
        dcc.Dropdown(            
            [                
                {'label': 'Positivo', 'value': 0},
                {'label': 'Negativo', 'value':1},
                {'label': 'Neutral', 'value': 2}               
            ],  
            [0, 1, 2],                   
            multi=True,
            id='input-dropdown-sentiment'
        ),
        html.Hr(),
        html.Label('Filtro por Subjetividad'),
        dcc.Dropdown(            
            [                
                {'label': 'Objetivo', 'value': 0},
                {'label': 'Subjetivo', 'value':1},
            ],  
            [0, 1],                   
            multi=True,
            id='input-dropdown-subjetividad',
        )
 

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
        #html.Span(id='click-data'),  
        html.Div(id='output-tweet'), 

        html.Div(id='output-datatable'),

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

def setAcumInt(propertie, df):    

    object_names[propertie]['count'] = math.trunc(df[propertie].describe().at['count'])
    object_names[propertie]['min'] = math.trunc(df[propertie].describe().at['min'])
    object_names[propertie]['max'] = math.trunc(df[propertie].describe().at['max'])
    object_names[propertie]['mean'] = math.trunc(df[propertie].describe().at['mean'])

def setAcumBoolean(propertie, df):

    valTrue = df[propertie].sum()
    valFalse = (~df[propertie]).sum()
    valTotal = valTrue + valFalse
    valTrue = math.trunc((valTrue / valTotal) * 100)
    valFalse = 100 - valTrue

    
    object_names[propertie]['true'] = valTrue
    object_names[propertie]['false'] = valFalse    
    

def setAcumString(propertie, df):    

    object_names[propertie]['name'] = df[propertie].describe()['top']
    object_names[propertie]['freq'] = df[propertie].describe()['freq']
    object_names[propertie]['total'] = df[propertie].describe()['count']

def setAcumDate(propertie, df):
    object_names[propertie]['min'] = df[propertie].min()
    object_names[propertie]['max'] =  df[propertie].max()

def setObjectNames(object_names):

    
    countIndex = 0        
    for key in object_names.keys():                        
        if key == 'favorite_count' or key == 'retweet_count':
            properties_value[countIndex] = 'min: ' + str(object_names[key]['min'])+ ' , ' + 'max: '+str(object_names[key]['max']) + ' , '+ 'mean: '+ str(object_names[key]['mean'])
        elif key == 'created_at':
            properties_value[countIndex] = 'min: ' + str(object_names[key]['min'])+ ' , ' + 'max: '+str(object_names[key]['max'])        
        elif key == 'is_retweet':
            properties_value[countIndex] = 'Retuiteado: ' + str(object_names[key]['true'])+ '%'+' , ' + 'Sin retuitear: '+str(object_names[key]['false']) + '%'
        elif key == 'source':
            total = math.trunc((object_names[key]['freq'] / object_names[key]['total']) * 100)
            properties_value[countIndex] =  str(total) + '% provienen desde ' + object_names[key]['name']                
        elif key == 'place':            
            properties_value[countIndex] =  str(object_names[key]['freq']) + ' provienen desde ' + object_names[key]['name']
        elif key == 'lang':            
            properties_value[countIndex] =  str(object_names[key]['freq']) + ' provien desde el idioma ' + object_names[key]['name']
        elif key == 'label':     
            total = math.trunc((object_names[key]['freq'] / object_names[key]['total']) * 100)       
            properties_value[countIndex] =  str(total) + '%  de los hashtags son de ' + object_names[key]['name']
        else:
            properties_value[countIndex] = ''
        countIndex += 1     

    
# castear tipo de dato y aplicar textblob
def procesarTypeData(dfcovid):
    
    # cantidad de filas
    rows = len(dfcovid.axes[0])                
    
    polarity = []
    subjectivity = []
    sentiment = []
    fecha = []
    
    for index in range(rows):

        # castear string a datetime
        textfecha = dfcovid.loc[index, 'created_at']
        fechaval = castToDateI(textfecha)                           
        fecha.append(fechaval)
        # actualizando el campo date
        dfcovid.at[index, 'created_at'] = fechaval

        # castear texto vacio, para que textblob analice bien
        textproc = text_preprocessing(dfcovid.loc[index, 'text'])         
        dfcovid.at[index, 'text'] = textproc   

        # obteniendo el sentimiento por medio de la libreria textblob
        sentimental = TextBlob(textproc)
        pol = sentimental.sentiment.polarity
        polarity.append(pol) 
        val = 0 if pol == 0 else (-1 if pol < 0 else 1)            
        sentiment.append(val)

        # obteniendo la subjetividad
        subjectivity.append(sentimental.sentiment.subjectivity)        
        
    # adicionando nueva columna al dataframe
    dfcovid['polarity'] = polarity
    dfcovid['subjectivity'] = subjectivity
    dfcovid['sentiment'] = sentiment    
    dfcovid['fecha'] = fecha

    # ordenando el dataframe en base a la fecha(nuevo campo proveniente de created_at)    
    dfcovid = (dfcovid.sort_values(by=['fecha']))
    return dfcovid

# realizar una copia del dataframe original, para trabajar en la copia
def copyDataframe(dforiginal):
    # retorna copia en profundidad de dataframe 
    return dforiginal.copy()

# calcula los totales iniciales en base al dataframe
def calcTotalesSentimental(df, totalPositive, totalNegative, totalNeutral):
    for index in df.index:
        textfecha = df.loc[index, 'created_at']   
        textfecha = textfecha.replace(hour=0, minute=0, second=0, microsecond=0)          
        key = str(textfecha.year) + str(textfecha.month) + str(textfecha.day)                        
        # positivo
        if df.loc[index, 'sentiment'] == 1:
            if not key in totalPositive:                
                totalPositive[key] = {'date':textfecha,'obj': []}
            totalPositive.get(key).get('obj').append(index)
                
        # negativo
        if df.loc[index, 'sentiment'] == -1:
            if not key in totalNegative:                
                totalNegative[key] = {'date':textfecha,'obj': []}
            totalNegative.get(key).get('obj').append(index)
            
        # neutro
        if df.loc[index, 'sentiment'] == 0:
            if not key in totalNeutral:                
                totalNeutral[key] = {'date':textfecha,'obj': []}
            totalNeutral.get(key).get('obj').append(index)

# procesar para la grafica de la linea de tiempo
def processingTimeLine(totalPositive, totalNegative, totalNeutral):    
            

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


    return {'figtimeline':figtimeline}

# procesar para la grafica del piechart
def processingPieChart(df):

    # calculando la suma de los sentimientos
    labels = ['Positivo','Negativo','Neutral']
    values =[0, 0, 0]
    labelsSubjectivity = ['Objetivo','Subjetivo']
    valuesSubjectivity = [0, 0]
    
    # for i in range(len(dfcovid)) :
    for index, row in df.iterrows():
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

    return {'figpie':figpie, 'figpiesubjetivity':figpiesubjetivity}
    

# procesar para la grafica del resumen
def processingResum(df):                
    
    # procesar string
    setAcumString('lang', df)
    setAcumString('place', df)        
    setAcumString('label', df)        
    setAcumString('source', df)
    
    
    # procesar booleanos        
    setAcumBoolean('is_retweet', df)

    # procesar enteros
    setAcumInt('favorite_count', df)
    setAcumInt('retweet_count', df)
    
    # procesar fechas
    setAcumDate('created_at', df)
        
    # almacenando en una
    setObjectNames(object_names)
    dfDatatable = generateDataTable()
    
    return {'datatable': dash_table.DataTable(dfDatatable.to_dict('records'), [{"name": i, "id": i} for i in dfDatatable.columns])    }

# procesar para la grafica de los tweets
def processingTweets(df):
    
    # numero de tweets
    tweets = str(len(df)) + ' tweets'

    # numero de usuarios
    users = str(len(df['id_str'].unique())) + ' usuarios'
    
    print(tweets)
    print(users)
    
    return {'tweets':tweets, 'users':users}


# mostrar graficos en base a los filtros
def mostrarGraficasByFilter(dfcovidcopy, tpos, tneg, tneu):
    
    pieObj = processingPieChart(dfcovidcopy)
    timelineObj = processingTimeLine(tpos, tneg, tneu)
    dataObj = processingTweets(dfcovidcopy)
    datatableObj = processingResum(dfcovidcopy)

    figpie = pieObj['figpie']
    figpiesubjetivity = pieObj['figpiesubjetivity']        
    figtimeline = timelineObj['figtimeline']
    tweets = dataObj['tweets']
    users = dataObj['users']
    datatable = datatableObj['datatable']        

    return {'figpiesubjetivity':figpiesubjetivity, 'figpie':figpie, 'figtimeline':figtimeline, 'tweets':tweets, 'users':users, 'datatable':datatable}

# filtro por fecha
def filterByDateTime(dfcovid, objectFilter):
    dfcovidcopy = dfcovid[
    (dfcovid["created_at"] >= objectFilter['rangeDate']['min'])
        & (dfcovid["created_at"] <= objectFilter['rangeDate']['max'])
    ]
    return dfcovidcopy
# filtro por sentimiento
def filterBySentimental(dfcovid, objectFilter):
    print('objeft filter')
    print(objectFilter)
    if   objectFilter['polarity']['positivo'] == False and objectFilter['polarity']['negativo'] == False and objectFilter['polarity']['neutral'] == False :        
        dfcovidcopy = dfcovid[((dfcovid["sentiment"] != 1) | (dfcovid["sentiment"] != -1) | (dfcovid["sentiment"] != 0))]
    elif objectFilter['polarity']['positivo'] == False and objectFilter['polarity']['negativo'] == False and objectFilter['polarity']['neutral'] == True :
        dfcovidcopy = dfcovid[(dfcovid["sentiment"] == 0)]
    elif objectFilter['polarity']['positivo'] == False and objectFilter['polarity']['negativo'] == True and objectFilter['polarity']['neutral'] == False :
        dfcovidcopy = dfcovid[(dfcovid["sentiment"] == -1)]
    elif objectFilter['polarity']['positivo'] == False and objectFilter['polarity']['negativo'] == True and objectFilter['polarity']['neutral'] == True :
        dfcovidcopy = dfcovid[((dfcovid["sentiment"] == -1) | (dfcovid["sentiment"] == 0))]
    elif objectFilter['polarity']['positivo'] == True and objectFilter['polarity']['negativo'] == False and objectFilter['polarity']['neutral'] == False :
        dfcovidcopy = dfcovid[(dfcovid["sentiment"] == 1)]
    elif objectFilter['polarity']['positivo'] == True and objectFilter['polarity']['negativo'] == False and objectFilter['polarity']['neutral'] == True :
        dfcovidcopy = dfcovid[((dfcovid["sentiment"] == 1) | (dfcovid["sentiment"] == 0))]
    elif objectFilter['polarity']['positivo'] == True and objectFilter['polarity']['negativo'] == True and objectFilter['polarity']['neutral'] == False :    
        dfcovidcopy = dfcovid[((dfcovid["sentiment"] == 1) | (dfcovid["sentiment"] == -1))]
    else :# objectFilter['polarity']['positivo'] == True and objectFilter['polarity']['negativo'] == True and objectFilter['polarity']['neutral'] == True : 
        dfcovidcopy = dfcovid[((dfcovid["sentiment"] == 1) | (dfcovid["sentiment"] == -1) | (dfcovid["sentiment"] == 0))]
    
    return dfcovidcopy
# filtro por subjetividad
def filterBySubjectivity(dfcovid, objectFilter):

    if objectFilter['subjectivity']['objetivo'] == False and objectFilter['subjectivity']['subjetivo'] == False:
        dfcovidcopy = dfcovid[(dfcovid["subjectivity"] > 1)]
    elif objectFilter['subjectivity']['objetivo'] == False and objectFilter['subjectivity']['subjetivo'] == True:
        dfcovidcopy = dfcovid[(dfcovid["subjectivity"] > 0)]
    elif objectFilter['subjectivity']['objetivo'] == True and objectFilter['subjectivity']['subjetivo'] == False:
        dfcovidcopy = dfcovid[(dfcovid["subjectivity"] == 0)]
    else : # objectFilter['subjectivity']['objetivo'] == True and objectFilter['subjectivity']['subjetivo'] == True:
        dfcovidcopy = dfcovid[((dfcovid["subjectivity"] >= 0) | (dfcovid["subjectivity"] <= 1))]

    return dfcovidcopy

@app.callback(
              Output('my-date-picker-range', 'min_date_allowed'),
              Output('my-date-picker-range', 'max_date_allowed'),
              Output('my-date-picker-range', 'initial_visible_month'),
              Output('my-date-picker-range', 'start_date'),
              Output('my-date-picker-range', 'end_date'),
              Output('output-pie-subjetivity', 'figure'),
              Output('output-pie', 'figure'),
              Output('output-timeline', 'figure'),
              Output('output-tweets', component_property='children'),
              Output('output-users', component_property='children'),
              Output('output-datatable', component_property='children'),              
              Input('submit-button-state', 'n_clicks'),
              Input('my-date-picker-range', 'start_date'),
              Input('my-date-picker-range', 'end_date'),
              Input('input-dropdown-sentiment', 'value'),
              Input('input-dropdown-subjetividad', 'value')
              )
def update_output(n_clicks, start_date, end_date, valsentimental, valsubjectivity):
    
    

    global dfcovid
    global dfcovidcopy
    global objectFilter
    global totalPositive
    global totalNegative
    global totalNeutral
    global count
    global objectDateTimeRange

    print('**************************rrrrrrrrrrrrrrrrrrrrrrrrr************************')
    print(valsentimental)
    print(valsubjectivity)
    
    
    # obtener el dataset de covid19
           
    if count == 0:
        count += 1
        print('No existe el dataframe')                   
    
        # truncate los elementos del dataframe solo para pruebas
        # dfcovid =  dfcovid.truncate(before=0, after=30000)
        # dfcovid =  dfcovid.truncate(before=0, after=100)        

        # procesar tipo de datos y aplicar textblob
        dfcovid = procesarTypeData(dfcovid)

        
        # actualizar el objeto filtro, la primera vez
        objectFilter['rangeDate']['min'] =  dfcovid['created_at'].min()   
        objectFilter['rangeDate']['max'] = dfcovid['created_at'].max()

        objectDateTimeRange['min_date_allowed'] = dfcovid['created_at'].min() 
        objectDateTimeRange['max_date_allowed'] = dfcovid['created_at'].max()
        objectDateTimeRange['initial_visible_month'] = objectFilter['rangeDate']['min']
        objectDateTimeRange['start_date'] = objectFilter['rangeDate']['min']
        objectDateTimeRange['end_date'] = objectFilter['rangeDate']['max']
                   
    else :
        # aumentando el contador
        count += 1  
        start_date = start_date.replace("-", "/")  
        end_date = end_date.replace("-", "/")  
        # actualizar el objeto filtro
        try:                                
            min = datetime.strptime(start_date, '%Y/%m/%d')            
            print('************ año *******')
            print(min)
        except:
            print("ValueError Raised MIN DATE:")  
            try:                                            
                min = datetime.strptime(start_date, '%Y/%m/%dT%H:%M:%S')            
                print('************* hora ******')
                print(min)
            except:
                print("ValueError Raised MIN DATE:")  


        # actualizar el objeto filtro
        try:                                
            max = datetime.strptime(end_date, '%Y/%m/%d')            
            print('************ año *******')
            print(max)
        except:
            print("ValueError Raised Max DATE:")  
            try:                                            
                max = datetime.strptime(end_date, '%Y/%m/%dT%H:%M:%S')            
                print('************* hora ******')
                print(max)
            except:
                print("ValueError Raised Max DATE:") 


        objectFilter['rangeDate']['min'] =  min   
        objectFilter['rangeDate']['max'] = max

        objectDateTimeRange['start_date'] = objectFilter['rangeDate']['min']
        objectDateTimeRange['end_date'] = objectFilter['rangeDate']['max']

        objectFilter['polarity'] = {'positivo': False, 'negativo':False, 'neutral': False}
        
        if len(valsentimental) != 0 :
            
            for val in valsentimental:
                if val == 0:
                    objectFilter['polarity']['positivo'] = True
                if val == 1:
                    objectFilter['polarity']['negativo'] = True
                if val == 2:
                    objectFilter['polarity']['neutral'] = True

        objectFilter['subjectivity'] = {'objetivo': False, 'subjetivo':False}
        
        if len(valsubjectivity) != 0 :
            
            for val in valsubjectivity:
                if val == 0:
                    objectFilter['subjectivity']['objetivo'] = True
                if val == 1:
                    objectFilter['subjectivity']['subjetivo'] = True
                
                        
        # actualizando los filtros sentimiento y objetividad
        # objectFilter = {
        #     'rangeDate':{'min':datetime.now(), 'max':datetime.now()},
        #     'polarity':{'positivo': True, 'negativo':True, 'neutral': True},
        #     'subjectivity':{'objetivo': True, 'subjetivo':True}
        # }
    
    
    # calculando los valores en base al filtro
        
    # dictionarios para los totales de los sentimientos    
    totalPositive = dict()        
    totalNegative = dict()                
    totalNeutral = dict()         


    print('........................................Nuevo filtrado .............................')
    print(objectFilter)    
    # print(dfcovidcopy.describe()) 
    # Filtro por fecha

    dfcovidcopy = filterByDateTime(dfcovid, objectFilter)
    print(dfcovidcopy.info()) 
    dfcovidcopy = filterBySentimental(dfcovidcopy, objectFilter)
    print(dfcovidcopy.info()) 
    dfcovidcopy = filterBySubjectivity(dfcovidcopy, objectFilter)
    print(dfcovidcopy.info()) 

    # dfcovid[
    # (dfcovid["created_at"] >= objectFilter['rangeDate']['min'])
    #     & (dfcovid["created_at"] <= objectFilter['rangeDate']['max'])
    # ]





    # Fitro por sentimientos
    # dfcovidcopy = dfcovid[
    # (dfcovid["sentiment"] >= objectFilter['rangeDate']['min'])
    #     & (dfcovid["created_at"] <= objectFilter['rangeDate']['max'])
    # ]

    # Filtro por subjetividad


    

    # calculando los nuevos totales en base al nuevo dataframe
    calcTotalesSentimental(dfcovidcopy, totalPositive, totalNegative, totalNeutral)

        
    # # obtener la graficas    
    obj  = mostrarGraficasByFilter(dfcovidcopy, totalPositive, totalNegative, totalNeutral)            
    
    figpiesubjetivity = obj['figpiesubjetivity']
    figpie = obj['figpie'] 
    figtimeline = obj['figtimeline']
    tweets = obj['tweets']
    users = obj['users']
    datatable = obj['datatable']
    
        

    return  objectDateTimeRange['min_date_allowed'], objectDateTimeRange['max_date_allowed'],objectDateTimeRange['initial_visible_month'],objectDateTimeRange['start_date'],objectDateTimeRange['end_date'],figpiesubjetivity, figpie, figtimeline, tweets, users, datatable
    


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


# @app.callback(    
#     Output('output-pie-subjetivity', 'figure'),
#     Output('output-pie', 'figure'),
#     Output('output-timeline', 'figure'),
#     Output('output-tweets', component_property='children'),
#     Output('output-users', component_property='children'),
#     Output('output-datatable', component_property='children'), 
#     Input('my-date-picker-range', 'start_date'),
#     Input('my-date-picker-range', 'end_date')       
#     )
# def display_click_data(start_date, end_date):
#     print('----------------')
#     print(type(start_date))
#     print(type(end_date))

#     global dfcovid
#     global dfcovidcopy
#     global objectFilter
#     global totalPositive
#     global totalNegative
#     global totalNeutral
    

#     # actualizar el objeto filtro
#     objectFilter['rangeDate']['min'] =  start_date   
#     objectFilter['rangeDate']['max'] = end_date

#     # copia del dataframe original
#     dfcovidcopy = dfcovid[
#     (dfcovid["created_at"] >= objectFilter['rangeDate']['min'])
#         & (dfcovid["created_at"] <= objectFilter['rangeDate']['max'])
#     ] 

#     totalPositive = dict()
#     totalNegative = dict()
#     totalNeutral = dict()
#     # calculando los nuevos totales en base al nuevo dataframe
#     calcTotalesSentimental(dfcovid, totalPositive, totalNegative, totalNeutral)
        
#     # # obtener la graficas    
#     obj  = mostrarGraficasByFilter(dfcovidcopy, totalPositive, totalNegative, totalNeutral)            
    
#     figpiesubjetivity = obj['figpiesubjetivity']
#     figpie = obj['figpie'] 
#     figtimeline = obj['figtimeline']
#     tweets = obj['tweets']
#     users = obj['users']
#     datatable = obj['datatable']
    
#     return  figpiesubjetivity, figpie, figtimeline, tweets, users, datatable

    



if __name__ == '__main__':
    app.run_server(debug=True)
