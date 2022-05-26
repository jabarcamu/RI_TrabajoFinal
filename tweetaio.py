from dash import Dash, Output, Input, State, html, dcc, callback, MATCH
import uuid

# All-in-One Components should be suffixed with 'AIO'
class TweetAIO(html.Div):  # html.Div will be the "parent" component

    # # A set of functions that create pattern-matching callbacks of the subcomponents
    # class ids:
    #     dropdown = lambda aio_id: {
    #         'component': 'MarkdownWithColorAIO',
    #         'subcomponent': 'dropdown',
    #         'aio_id': aio_id
    #     }
    #     markdown = lambda aio_id: {
    #         'component': 'MarkdownWithColorAIO',
    #         'subcomponent': 'markdown',
    #         'aio_id': aio_id
    #     }

    # Make the ids class a public class
    # ids = ids

    # Define the arguments of the All-in-One component
    # constructor
    def __init__(
        self,
        text,
        polarity,
        subjetivity,
        date        
    ):
        """MarkdownWithColorAIO is an All-in-One component that is composed
        of a parent `html.Div` with a `dcc.Dropdown` color picker ("`dropdown`") and a
        `dcc.Markdown` ("`markdown`") component as children.
        The markdown component's color is determined by the dropdown colorpicker.
        - `text` - The Markdown component's text (required)
        - `colors` - The colors displayed in the dropdown
        - `markdown_props` - A dictionary of properties passed into the dcc.Markdown component. See https://dash.plotly.com/dash-core-components/markdown for the full list.
        - `dropdown_props` - A dictionary of properties passed into the dcc.Dropdown component. See https://dash.plotly.com/dash-core-components/dropdown for the full list.
        - `aio_id` - The All-in-One component ID used to generate the markdown and dropdown components's dictionary IDs.

        The All-in-One component dictionary IDs are available as
        - MarkdownWithColorAIO.ids.dropdown(aio_id)
        - MarkdownWithColorAIO.ids.markdown(aio_id)
        """
        


        # Define the component's layout
        super().__init__([  # Equivalent to `html.Div([...])`
            html.Div(children=[
                html.Span(children=text, style={'flex':1 })
            ],
            style={
                'display':'flex',
                'background': '#AED1E6'
            }),
            html.Div(children=[
                html.Span(children='Sentimiento', style={'flex':1 }), 
                html.Span(children='Subjetividad', style={'flex':1 }), 
                html.Span(children='Fecha de publicación', style={'flex':1 })
            ],
            style={
                'display':'flex',
                'background': '#E8E9ED' 
            }),
            html.Div(children=[
                html.Span(children=polarity, style={'flex':1 }), 
                html.Span(children=subjetivity, style={'flex':1 }), 
                html.Span(children=date, style={'flex':1 })
            ],
            style={
                'display':'flex',
                'background': '#B7CADB'
            })          
        ])

    