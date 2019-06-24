import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go

import os
import pandas as pd
import pickle
import random
import datetime


# ----- FUNCTIONS -----
def remove_non_numeric(x):
    return str(''.join(c for c in x if c.isdigit()))


def check_valid_phone(phone_number):
    len_valid = ((len(phone_number) > 9) and (len(phone_number) < 13))    # account for country codes with 1 or 2 digits
    type_valid = (type(phone_number) is str)
    try:
        int(phone_number)
        digits_valid = True
    except:
        digits_valid = False

    phone_valid = len_valid & type_valid & digits_valid

    return phone_valid


def create_fig_data(df, phone_number):
    if phone_number is None:
        df_filtered = df
    elif check_valid_phone(phone_number):
        try:
            df_filtered = df[df['phone'] == phone_number]
        except:
            df_filtered = df
    else:
        df_filtered = df

    df_summarized = df_filtered[['date', 'count']].groupby('date').sum()

    select_x = df_summarized.index
    select_y = df_summarized['count']

    # Create a trace
    trace = go.Scatter(
        x=select_x,
        y=select_y,
        mode='lines',
        marker=dict(
            color='#ad1457',
            line=dict(
                width=2
            )
        )
    )

    # create a layout
    layout = go.Layout(
        autosize=True,
        showlegend=False,
        hovermode='closest',
        dragmode='pan',
        height=250,
        margin=dict(b=50, t=0, r=10),
        xaxis=dict(
            tickfont=dict(
                family='monospace',
                size=14,
                color='#E9DDE1'
            ),
            showticklabels=True,
            zeroline=False
        ),
        yaxis=dict(
            title='Count of Text Messages',
            titlefont=dict(
                size=14,
                color='#E9DDE1'),
            showticklabels=True,
            tickfont=dict(
                family='monospace',
                size=14,
                color='#E9DDE1'
            ),
            zeroline=True,
            zerolinecolor='#E9DDE1'
        ),
        paper_bgcolor='#5c595a',
        plot_bgcolor='#5c595a')
    data = [trace]
    return data, layout


def create_wc_fig_data(word_clouds, select_phone, freq, select_index):
    global COLOR_PALETTE, POSITIVE_WORDS, NEGATIVE_WORDS, NUM_WC_WORDS

    if (select_phone is None) or (select_phone ==''):
        select_data = word_clouds['all'][freq]
        if freq == 'all':
            # case1: select_phone is None, frequency is all
            word_bag = select_data.values[0].words_
        else:
            # case2: select phone is None, frequency has index
            if len(select_index) > 1:
                word_bag = select_data.ix[[select_index]][0].words_
            else:
                word_bag = select_data.ix[select_index].values[0].words_
    else:
        select_data = word_clouds[select_phone][freq]
        if freq == 'all':
            # case3: select phone is string, frequency is all
            word_bag = select_data.values[0].words_
        else:
            # case4: select phone is string, frequency has index
            word_bag = select_data.ix[[[select_phone] + select_index]].values[0].words_

    wordbag_sorted = pd.DataFrame.from_dict(data=word_bag, orient='index', columns=['rel_freq']).sort_values(by='rel_freq', ascending=False)
    words = list(wordbag_sorted.index)[0:NUM_WC_WORDS]
    rel_freq = list(wordbag_sorted.rel_freq[0:NUM_WC_WORDS])


    def map_weights(orig_weight, orig_int_min, orig_int_max, int_min, int_max, n_int):
        int_size = (int_max - int_min) / n_int
        return round(((orig_weight - orig_int_min)/(orig_int_max - orig_int_min) * (int_max - int_min)) / int_size) * int_size + int_min
    weights = rel_freq
    mapped_weights = [map_weights(x, min(weights), max(weights), 10, 50, 5) for x in weights]

    colors = pd.Series(['#fec88c']*len(words))
    colors[list(pd.Series(words).isin(POSITIVE_WORDS))] = '#E9DDE1'
    colors[list(pd.Series(words).isin(NEGATIVE_WORDS))] = '#ee5c5d'
    data = go.Scatter(x=[random.random() for i in range(len(words))],
                      y=[random.random() for i in range(len(words))],
                      mode='text',
                      text=words,
                      marker={'opacity': 0.3},
                      textfont={'size': mapped_weights,
                                'color': colors})
    layout = go.Layout({'xaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False},
                        'yaxis': {'showgrid': False, 'showticklabels': False, 'zeroline': False}},
                       autosize=True,
                       height=250,
                       paper_bgcolor='#5c595a',
                       plot_bgcolor='#5c595a',
                       margin=go.layout.Margin(
                           b=0,
                           t=0,
                           pad=0,
                           l=10,
                           r=10
                       )
                       )
    return [data], layout


def check_for_hover_change(clickData, select_freq):
    if clickData is None:
        select_freq = 'all'
        select_index = None
        date = None
    else:
        datestr = clickData['points'][0]['x']
        date = datetime.datetime.strptime(datestr, "%Y-%m-%d")
        if select_freq == 'year':
            select_index = [date.year]
        elif select_freq == 'month':
            select_index = [date.year, date.month]
        else:
            select_index = None
    return select_freq, select_index, date


# ----- INITIALIZE -----
# --- Define params
filepath_input_data = 'assets'
filename_input_data = 'count_text_messages_daily.csv'

filepath_wc_data = 'assets'
filename_wc_data = 'word_clouds.pkl'
select_port = 8080      # Beanstalk expects it to be running on 8080
plot_properties = {'background_color': 'white', 'cmap': 'magma', 'max_font_size': 40, 'scale': 10, 'random_state': 1}

select_phone = None
select_freq = 'all'
select_index = None
DATE_YEAR_OLD = 0
DATE_MONTH_OLD = 0
NUM_WC_WORDS = 40

# colormap
COLOR_PALETTE = {'light grey': '#E9DDE1', 'yellow': '#fec88c', 'salmon': '#ee5c5d', 'magenta': '#ad1457', 'violet': '#8c2980', 'indigo': '#4a148c'}
with open('assets/positive_words.txt', errors='ignore') as f:
    POSITIVE_WORDS = [word for line in f for word in line.split()]
with open('assets/negative_words.txt', errors='ignore') as f:
    NEGATIVE_WORDS = [word for line in f for word in line.split()]

# --- Calculations
file_loc_input_data = os.path.join(filepath_input_data, filename_input_data)
file_loc_wc_data = os.path.join(filepath_wc_data, filename_wc_data)

# Initialize graph
df = pd.read_csv(file_loc_input_data)

with open(file_loc_wc_data, "rb") as input_file:
    word_clouds = pickle.load(input_file)


# ----- START APPLICATION ------
# Step 1. Launch the application
app = dash.Dash(__name__, meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1, user-scalable=0"}
    ])

# Step 3. Create a plotly figure
def serve_layout():
    try:
        fig
    except NameError:
        # frequency plot
        data_temp, layout_temp = create_fig_data(df, phone_number=None)
        fig = go.Figure(data=data_temp, layout=layout_temp)

        # wordcloud
        data_wc_temp, layout_wc_temp = create_wc_fig_data(word_clouds, select_phone=select_phone, freq=select_freq, select_index=select_index)
        fig_wc = go.Figure(data=data_wc_temp, layout=layout_wc_temp)

    layout_temp = html.Div([
        html.Div(children=html.Div([html.H1("You talkin' to me?")])),
        html.Div(
            className='row',
            children=[
                html.Div(
                    dcc.Input(id='input-box', type='text', placeholder='212-555-1212'),
                    style={'display': 'inline-block', 'width': '50%'}
                ),
                html.Div(
                    dcc.Dropdown(
                        id='wc_agg_freq',
                        options=[{'value': 'month', 'label': 'monthly'}, {'value': 'year', 'label': 'annually'},
                                 {'value': None, 'label': 'all'}],
                        value=None,
                        className='dropdown'
                    ),
                    style={'display': 'inline-block', 'width': '50%', 'vertical-align': 'middle'}
                )
            ],
            style={'display': 'inline-block', 'width': '100%'}
        ),
        html.Button('Submit', id='button'),
        dcc.Graph(id='wordcloud', figure=fig_wc),
        dcc.Graph(id='plot', figure=fig),
        html.Div(children=html.Label(["Python code: ", html.A('https://github.com/mallory-archer/text_blitz/',
                                                              href='https://github.com/mallory-archer/text_blitz/',
                                                              style={'color': '#ad1457'})],
                                     style={'color': '#E9DDE1'}))
    ])
    return layout_temp


# Step 4. Create a Dash layout
app.layout = serve_layout


# Step 5. Add callback functions
@app.callback(Output('plot', 'figure'),
              [Input('button', 'n_clicks')],
              [State('input-box', 'value'), State('plot', 'figure')]
              )
def update_figure(n_clicks, phone_number, fig_updated):
    if phone_number is not None:
        phone_number = remove_non_numeric(phone_number)

    data_temp, layout_temp = create_fig_data(df, phone_number)
    fig_updated = go.Figure(data=data_temp, layout=layout_temp)

    return fig_updated


@app.callback(Output('wordcloud', 'figure'),
              [Input('button', 'n_clicks'), Input('plot', 'clickData')],
              [State('input-box', 'value'), State('wordcloud', 'figure'), State('wc_agg_freq', 'value')]
              )
def update_figure(n_clicks, clickData, phone_number, fig_wc_updated, select_freq):
    global DATE_YEAR_OLD, DATE_MONTH_OLD
    if phone_number is not None:
        phone_number = remove_non_numeric(phone_number)

    if select_freq is None:
        select_freq = 'all'

    # Check to see if need to update wordclou based on changing hover input (still in same month or year?)
    select_freq, select_index, date = check_for_hover_change(clickData, select_freq)
    try:
        if select_freq == 'year':
            recalc = (date.year != DATE_YEAR_OLD)
            DATE_YEAR_OLD = date.year
        elif select_freq == 'month':
            recalc = ((date.year != DATE_YEAR_OLD) or (date.month != DATE_MONTH_OLD))
            DATE_YEAR_OLD = date.year
            DATE_MONTH_OLD = date.month
        else:
            recalc = True
    except:
        recalc = True
        DATE_YEAR_OLD = 0
        DATE_MONTH_OLD = 0

    if recalc:
        data_wc_temp, layout_wc_temp = create_wc_fig_data(word_clouds, select_phone=phone_number, freq=select_freq, select_index=select_index)
        fig_wc_updated = go.Figure(data=data_wc_temp, layout=layout_wc_temp)

    return fig_wc_updated

# Step 6. Add the server clause
application = app.server

if __name__ == '__main__':
    application.run(debug=True, port=select_port)  # Beanstalk expects it to be running on 8080.
