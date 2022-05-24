# -*- coding: utf-8 -*-
"""
Module doc string
"""
import pathlib
import re
import json
from datetime import datetime
import flask

from dash import Dash

import dash_table
#from dash import dash_table

import matplotlib.colors as mcolors

import dash_bootstrap_components as dbc

#from dash import dcc
import dash_core_components as dcc

#from dash import html
import dash_html_components as html

import plotly.graph_objs as go
import plotly.express as px

import pandas as pd
import numpy as np
from precomputing_bp import add_stopwords

#from dash import Input, Output, State
from dash.dependencies import Output, Input, State

from dateutil import relativedelta
from wordcloud import WordCloud, STOPWORDS
from sklearn.manifold import TSNE


DATA_PATH = pathlib.Path(__file__).parent.resolve()
EXTERNAL_STYLESHEETS = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
FILENAME = "data/dataset_covid19_coaid/consolidado.tsv"
FILENAME_PRECOMPUTED = "data/dataset_covid19_coaid/precomputed.json"
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
GLOBAL_DF = pd.read_csv(DATA_PATH.parent.joinpath(FILENAME),sep="\t")

with open(DATA_PATH.parent.joinpath(FILENAME_PRECOMPUTED)) as precomputed_file:
    PRECOMPUTED_LDA = json.load(precomputed_file)


"""
We are casting the whole column to datetime to make life easier in the rest of the code.
It isn't a terribly expensive operation so for the sake of tidyness we went this way.
"""
GLOBAL_DF["created_at"] = pd.to_datetime(
    GLOBAL_DF["created_at"], infer_datetime_format=True
)



# sample data: sampling the entire dataset of tweets
# in order to accelerate the plotting
# input: dataframe or dataset and float_percent (percentage of sampling)
def sample_data(dataframe, float_percent):
    """
    Returns a subset of the provided dataframe.
    The sampling is evenly distributed and reproducible
    """
    print("making a local_df data sample with float_percent: %s" % (float_percent))
    return dataframe.sample(frac=float_percent, random_state=1)


def get_tweet_count_by_annot(dataframe):
    """ Helper function to get tweet counts for unique dates """
    tweets_counts = dataframe["source"].value_counts()
    # we filter out all tweets with less than 11 tweet for now
    tweets_counts = tweets_counts[tweets_counts > 10]
    values = tweets_counts.keys().tolist()
    counts = tweets_counts.tolist()
    return values, counts


# helper function in order to work with sample data from covid tweets
# input: time_values or time interval with initial date and final date
# output Corpus reduced by time and number of registers

def make_local_df(selected_annot, time_values, n_selection):
    
    print("Get Interval Time:", str(time_values))

    n_float = float(n_selection / 100)
    print("Get Sample Data and Percentage", str(n_selection), str(n_float))
    
    # sample the dataset according to the slider
    local_df = sample_data(GLOBAL_DF, n_float)

    if time_values is not None:
        time_values = time_slider_to_date(time_values)
        local_df = local_df[
            (local_df["created_at"] >= time_values[0])
            & (local_df["created_at"] <= time_values[1])
        ]
    if selected_annot:
        local_df = local_df[local_df["source"] == selected_annot]
    #print(local_df.head())
    return local_df


def make_marks_time_slider(mini, maxi):
    """
    A helper function to generate a dictionary that should look something like:
    {1601528400: '2020', 1609300800: 'Q2', 1617163200: 'Q3', 1625112000: 'Q4'}
    """
    step = relativedelta.relativedelta(months=+1)
    print("Step: ",step)
    start = datetime(year=mini.year, month=1, day=1)
    print("Start: ",start)
    end = datetime(year=maxi.year, month=maxi.month, day=30)
    print("End: ",end)
    ret = {}

    current = start
    while current <= end:
        current_str = int(current.timestamp())
        if current.month == 1:
            ret[current_str] = {
                "label": str(current.year),
                "style": {"font-weight": "bold"},
            }
        elif current.month == 4:
            ret[current_str] = {
                "label": "Q2",
                "style": {"font-weight": "lighter", "font-size": 7},
            }
        elif current.month == 7:
            ret[current_str] = {
                "label": "Q3",
                "style": {"font-weight": "lighter", "font-size": 7},
            }
        elif current.month == 10:
            ret[current_str] = {
                "label": "Q4",
                "style": {"font-weight": "lighter", "font-size": 7},
            }
        else:
            pass
        current += step
    print("Ret: ",ret)
    return ret


def time_slider_to_date(time_values):
    #convertir el datetime a un formato string tipo Mon Sep 30 07:06:05 2013
    min_date = datetime.fromtimestamp(time_values[0]).strftime("%c")
    max_date = datetime.fromtimestamp(time_values[1]).strftime("%c")
    print("Converted time_values: ")
    print("\tmin_date:", time_values[0], "to: ", min_date)
    print("\tmax_date:", time_values[1], "to: ", max_date)
    return [min_date, max_date]


def make_options_annot_drop(values):
    """
    Helper function to generate the data format the dropdown dash component wants
    """
    ret = []
    for value in values:
        ret.append({"label": value, "value": value})
    return ret




# plotly_wordcloud: it work with wordcloud and get its properties
# such as, frequency, positions, words, and others {fontsize,orientation and color}
# then plot a bar frequency with every word
# and finally a treemap with the respective size of cells 
def plotly_wordcloud(data_frame):
    """A wonderful function that returns figure data for three equally
    wonderful plots: wordcloud, frequency histogram and treemap"""
    tweets_text = list(data_frame["text"].dropna().values)

    if len(tweets_text) < 1:
        return {}, {}, {}

    # join all documents in corpus
    text = " ".join(list(tweets_text))

    word_cloud = WordCloud(stopwords=set(STOPWORDS), max_words=100, max_font_size=90)
    word_cloud.generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[0])
        y_arr.append(i[1])

    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color=color_list),
        hoverinfo="text",
        textposition="top center",
        hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        mode="text",
        text=word_list,
    )

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 250],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                "automargin": True,
                "range": [-100, 450],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}
    word_list_top = word_list[:25]
    word_list_top.reverse()
    freq_list_top = freq_list[:25]
    freq_list_top.reverse()

    frequency_figure_data = {
        "data": [
            {
                "y": word_list_top,
                "x": freq_list_top,
                "type": "bar",
                "name": "",
                "orientation": "h",
            }
        ],
        "layout": {"height": "550", "margin": dict(t=20, b=20, l=100, r=20, pad=4)},
    }
    treemap_trace = go.Treemap(
        labels=word_list_top, parents=[""] * len(word_list_top), values=freq_list_top
    )
    treemap_layout = go.Layout({"margin": dict(t=10, b=10, l=5, r=5, pad=4)})
    treemap_figure = {"data": [treemap_trace], "layout": treemap_layout}
    return wordcloud_figure_data, frequency_figure_data, treemap_figure




def populate_lda_scatter(tsne_df, df_top3words, df_dominant_topic):
    """Calculates LDA and returns figure data you can jam into a dcc.Graph()"""
    mycolors = np.array([color for name, color in mcolors.TABLEAU_COLORS.items()])

    # for each topic we create a separate trace
    traces = []
    for topic_id in df_top3words["topic_id"]:
        tsne_df_f = tsne_df[tsne_df.topic_num == topic_id]
        cluster_name = ", ".join(
            df_top3words[df_top3words["topic_id"] == topic_id]["words"].to_list()
        )
        trace = go.Scatter(
            name=cluster_name,
            x=tsne_df_f["tsne_x"],
            y=tsne_df_f["tsne_y"],
            mode="markers",
            hovertext=tsne_df_f["doc_num"],
            marker=dict(
                size=6,
                color=mycolors[tsne_df_f["topic_num"]],  # set color equal to a variable
                colorscale="Viridis",
                showscale=False,
            ),
        )
        traces.append(trace)

    layout = go.Layout({"title": "Análisis de Tópicos usando LDA"})

    return {"data": traces, "layout": layout}


"""
#  Page layout and contents

In an effort to clean up the code a bit, we decided to break it apart into
sections. For instance: LEFT_COLUMN is the input controls you see in that gray
box on the top left. The body variable is the overall structure which most other
sections go into. This just makes it ever so slightly easier to find the right
spot to add to or change without having to count too many brackets.
"""

NAVBAR = dbc.Navbar(
    children=[
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                    dbc.Col(
                        dbc.NavbarBrand("Analisis de Datos - RealFakesCOVID-19", className="ml-2")
                    ),
                ],
                align="center",
                no_gutters=True,
            ),
            href="https://plot.ly",
        )
    ],
    color="dark",
    dark=True,
    sticky="top",
)

LEFT_COLUMN = dbc.Jumbotron(
    [
        html.H4(children="Seleccciona un tamanio de dataset & filtro de tiempo", className="display-5"),
        html.Hr(className="my-2"),
        html.Label("Selecciona un Porcentaje del Dataset", className="lead"),
        html.P(
            "(Bajo valor, el render será rapido. Alto valor, visualización mas precisa)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Slider(
            id="n-selection-slider",
            min=1,
            max=100,
            step=1,
            marks={
                0: "0%",
                10: "",
                20: "20%",
                30: "",
                40: "40%",
                50: "",
                60: "60%",
                70: "",
                80: "80%",
                90: "",
                100: "100%",
            },
            value=20,
        ),
        html.Label("Selecciona filtro de Anotaciones", style={"marginTop": 50}, className="lead"),
        html.P(
            "(Puedes usar el menu o clic sobre el barchart de la derecha)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
        dcc.Dropdown(
            #["2019","2020"],"2019",id="annot-drop", clearable=False, style={"marginBottom": 50, "font-size": 12}
            id="annot-drop", clearable=False, style={"marginBottom": 50, "font-size": 12}
        ),
        html.Label("Seleccione Intervalo de Tiempo", className="lead"),
        html.Div(dcc.RangeSlider(id="time-window-slider"), style={"marginBottom": 50}),
        html.P(
            "(Puedes definir el intervalo para aplicar wordcloud and lda)",
            style={"fontSize": 10, "font-weight": "lighter"},
        ),
    ]
)


WORDCLOUD_PLOTS = [
    dbc.CardHeader(html.H5("Most frequently used words in complaints")),
    dbc.Alert(
        "Not enough data to render these plots, please adjust the filters",
        id="no-data-alert",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Loading(
                            id="loading-frequencies",
                            children=[dcc.Graph(id="frequency_figure")],
                            type="default",
                        )
                    ),
                    dbc.Col(
                        [
                            dcc.Tabs(
                                id="tabs",
                                children=[
                                    dcc.Tab(
                                        label="Treemap",
                                        children=[
                                            dcc.Loading(
                                                id="loading-treemap",
                                                children=[dcc.Graph(id="covid-treemap")],
                                                type="default",
                                            )
                                        ],
                                    ),
                                    dcc.Tab(
                                        label="Wordcloud",
                                        children=[
                                            dcc.Loading(
                                                id="loading-wordcloud",
                                                children=[
                                                    dcc.Graph(id="covid-wordcloud")
                                                ],
                                                type="default",
                                            )
                                        ],
                                    ),
                                ],
                            )
                        ],
                        md=8,
                    ),
                ]
            )
        ]
    ),
]

LDA_PLOT = dcc.Loading(
    id="loading-lda-plot", children=[dcc.Graph(id="tsne-lda")], type="default"
)
LDA_TABLE = html.Div(
    id="lda-table-block",
    children=[
        dcc.Loading(
            id="loading-lda-table",
            children=[
                dash_table.DataTable(
                    id="lda-table",
                    style_cell_conditional=[
                        {
                            "if": {"column_id": "Text"},
                            "textAlign": "left",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "min-width": "50%",
                        }
                    ],
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "rgb(243, 246, 251)",
                        }
                    ],
                    style_cell={
                        "padding": "16px",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "max-width": "0",
                    },
                    style_header={"backgroundColor": "white", "fontWeight": "bold"},
                    style_data={"whiteSpace": "normal", "height": "auto"},
                    filter_action="native",
                    page_action="native",
                    page_current=0,
                    page_size=5,
                    columns=[],
                    data=[],
                )
            ],
            type="default",
        )
    ],
    style={"display": "none"},
)

LDA_PLOTS = [
    dbc.CardHeader(html.H5("Modelamiento de Topicos LDA para RealFakeCovidTweets")),
    dbc.Alert(
        "Not enough data to render LDA plots, please adjust the filters",
        id="no-data-alert-lda",
        color="warning",
        style={"display": "none"},
    ),
    dbc.CardBody(
        [
            html.P(
                "Clic sobre un punto en el scatter para explorar un especifico realfake-covidtweet",
                className="mb-0",
            ),
            html.P(
                "(selecciona un anio para aplicar el analisis de topicos)",
                style={"fontSize": 10, "font-weight": "lighter"},
            ),
            LDA_PLOT,
            html.Hr(),
            LDA_TABLE,
        ]
    ),
]

BODY = dbc.Container(
    [  
        dbc.Row(
            [
                dbc.Col(LEFT_COLUMN, md=4, align="center"),
                dbc.Col([
                    dbc.Row(
                        dbc.Col(dbc.Card(WORDCLOUD_PLOTS)),
                    ),
                    dbc.Row(
                        dbc.Col(dbc.Card(LDA_PLOTS)),
                    )] ,md=8,
                ),
            ],
            style={"marginTop": 30},
        ),
        #dbc.Row([dbc.Col([dbc.Card(LDA_PLOTS)])], style={"marginTop": 50}),

    ],
    className="mt-12",
)


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server  # for Heroku deployment

app.layout = html.Div(children=[NAVBAR, BODY])


# -- -- -- -- -- -- -- -- CALLBACKS -- -- -- -- -- -- -- -- --

@app.callback(
    Output("annot-drop", "options"),
    [Input("time-window-slider", "value"), Input("n-selection-slider", "value")],
)
def populate_bank_dropdown(time_values, n_value):
    if time_values is not None:
        pass
    n_value += 1
    annot_names, counts = get_tweet_count_by_annot(GLOBAL_DF)
    counts.append(1)
    return make_options_annot_drop(annot_names)


# Callback para poblar el time slider, capturando del minimo y maxima
# fecha del dataset de tweets.
@app.callback(
    [
        Output("time-window-slider", "min"),
        Output("time-window-slider", "max"),
        Output("time-window-slider", "step"),
        Output("time-window-slider", "marks"),
        Output("time-window-slider", "value"),
    ],
    [Input("n-selection-slider", "value")],
)


def populate_time_slider(value):
    """
    Depending on our dataset, we need to populate the time-slider
    with different ranges. This function does that and returns the
    needed data to the time-window-slider.
    """
    value += 0
    GLOBAL_DF["created_at"] = GLOBAL_DF["created_at"].astype("datetime64[ns]")
    print("Min: ",GLOBAL_DF["created_at"].min())
    print("Max: ",GLOBAL_DF["created_at"].max())

    min_date = GLOBAL_DF["created_at"].min()
    max_date = GLOBAL_DF["created_at"].max()
    
    print("Global mindate: ",min_date)
    print("Global maxdate: ",max_date)

    marks = make_marks_time_slider(min_date, max_date)
    min_epoch = list(marks.keys())[0]
    max_epoch = list(marks.keys())[-1]
    
    print("marks: ",marks)
    print("marks_epochs: ",min_epoch,max_epoch)
    return (
        min_epoch,
        max_epoch,
        (max_epoch - min_epoch) / (len(list(marks.keys())) * 3),
        marks,
        [min_epoch, max_epoch],
    )


# Callback de actualizacion de los plots de frecuencia, wordcloud, treemap
# input: filtro de tiempo, slider de tiempo, tamanio de dataset
@app.callback(
    [
        Output("covid-wordcloud", "figure"),
        Output("frequency_figure", "figure"),
        Output("covid-treemap", "figure"),
        Output("no-data-alert", "style"),
    ],
    [
        Input("annot-drop","value"),
        Input("time-window-slider", "value"),
        Input("n-selection-slider", "value"),
    ],
)
def update_wordcloud_plot(year_drop,time_values, n_selection):
    """ Callback to rerender wordcloud plot """
    local_df = make_local_df(year_drop,time_values, n_selection)
    wordcloud, frequency_figure, treemap = plotly_wordcloud(local_df)
    alert_style = {"display": "none"}
    if (wordcloud == {}) or (frequency_figure == {}) or (treemap == {}):
        alert_style = {"display": "block"}
    print("redrawing wordcloud...done")
    return (wordcloud, frequency_figure, treemap, alert_style)



@app.callback(
    [
        Output("lda-table", "data"),
        Output("lda-table", "columns"),
        Output("tsne-lda", "figure"),
        Output("no-data-alert-lda","style"),
    ],
    [Input("annot-drop", "value"), Input("time-window-slider","value")],
)
def update_lda_table(selected_annot,time_values):
    """ Update LDA table and scatter plot based on precomputed data """

    if selected_annot in PRECOMPUTED_LDA:
        df_dominant_topic = pd.read_json(
            PRECOMPUTED_LDA[selected_annot]["df_dominant_topic"]
        )
        tsne_df = pd.read_json(PRECOMPUTED_LDA[selected_annot]["tsne_df"])
        df_top3words = pd.read_json(PRECOMPUTED_LDA[selected_annot]["df_top3words"])
    else:
        return [[], [], {}, {}]

    lda_scatter_figure = populate_lda_scatter(tsne_df, df_top3words, df_dominant_topic)

    columns = [{"name": i, "id": i} for i in df_dominant_topic.columns]
    data = df_dominant_topic.to_dict("records")

    return (data, columns, lda_scatter_figure, {"display":"none"})

@app.callback(
    [Output("lda-table", "filter_query"), Output("lda-table-block", "style")],
    [Input("tsne-lda", "clickData")],
    [State("lda-table", "filter_query")],
)
def filter_table_on_scatter_click(tsne_click, current_filter):
    """ TODO """
    if tsne_click is not None:
        selected_tweet = tsne_click["points"][0]["hovertext"]
        if current_filter != "":
            filter_query = (
                "({Document_No} eq "
                + str(selected_tweet)
                + ") || ("
                + current_filter
                + ")"
            )
        else:
            filter_query = "{Document_No} eq " + str(selected_tweet)
        print("current_filter", current_filter)
        return (filter_query, {"display": "block"})
    return ["", {"display": "none"}]

if __name__ == "__main__":
    app.run_server(debug=True)
