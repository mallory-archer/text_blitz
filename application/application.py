import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

# import plotly.plotly as py
import plotly.graph_objs as go
# import numpy as np
from matplotlib import pyplot as plt

import os
import pandas as pd
import pickle


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
    # Create random data with numpy

    # N = 500
    # random_x = np.linspace(0, 1, N)
    # random_y = np.random.randn(N)
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
        y=select_y
    )
    data = [trace]
    return data


def create_wc_fig_data(word_clouds, select_phone, freq, select_index):
    wc_object = word_clouds[select_phone][freq].ix[[select_index]][0]
    return wc_object


def plot_wordcloud(wordcloud_object, plot_properties):
    for prop in plot_properties.keys():
        # wordcloud_object[prop] = plot_properties[prop]
        wordcloud_object.__setattr__(prop, plot_properties[prop])

    plt.figure(1, figsize=(12, 12))
    plt.axis('off')
    fig_wordcloud = plt.imshow(wordcloud_object)
    # plt.show()
    return fig_wordcloud

# ----- INITIALIZE -----
# --- Define params
filepath_input_data = 'assets'
# filepath_input_data = 'application/assets'  ############### take out application
filename_input_data = 'count_text_messages_daily.csv'
filepath_wc_data = 'assets'
# filepath_wc_data = os.path.join('application', 'assets')    ############### take out application
filename_wc_data = 'word_clouds.pkl'
# filepath = 'output_graphs'      # folder(s) in S3 bucket specifying where to save graph object jsons (as a result of clicking "save" on the website
# filename = 'saved_graph.txt'    # specify name of graph object json
# bucket_name = os.environ.get('S3_BUCKET')       # Environmental variable configured through Elastic Beanstalk web interface. Name can be specified as free text in console.
# aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID') # Environmental variable configured through Elastic Beanstalk web interface. Name can be specified as free text in console.
# aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY') # Environmental variable configured through Elastic Beanstalk web interface. Name can be specified as free text in console.
select_port = 8080      # Beanstalk expects it to be running on 8080
plot_properties = {'background_color': 'white', 'cmap': 'magma', 'max_font_size': 40, 'scale': 10, 'random_state': 1}

# --- Calculations
# file_loc = os.path.join(filepath, filename)
# file_loc = filepath + '/' + filename
file_loc_input_data = os.path.join(filepath_input_data, filename_input_data)
file_loc_wc_data = os.path.join(filepath_wc_data, filename_wc_data)

# Initialize graph
df = pd.read_csv(file_loc_input_data)

with open(file_loc_wc_data, "rb") as input_file:
    word_clouds = pickle.load(input_file)


# Specify S3 read/write params
# s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
# s3_resource = boto3.resource('s3')


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
        data_temp = create_fig_data(df, phone_number=None)
        fig = go.Figure(data=data_temp)

        # wordcloud
        data_wc_temp = create_wc_fig_data(word_clouds, select_phone='5635804952', freq='year', select_index=['5635804952', 2016])
        fig_wc_test = plot_wordcloud(data_wc_temp, plot_properties)
        fig_wc = fig    #####

    layout_temp = html.Div([
        html.Div(children=html.Div([html.H1("You talkin' to me?")])),
        html.Div(dcc.Input(id='input-box', type='text', placeholder='212-555-1212')),
        html.Button('Submit', id='button'),
        dcc.Graph(id='plot', figure=fig),
        dcc.Graph(id='wordcloud', figure=fig_wc)])

    #     html.Div(dcc.Input(id='input-box-friend', type='text', placeholder="FRIEND [First_name Last_name]")),
    #     html.Div(
    #         dcc.Dropdown(
    #             id='relationship',
    #             options=dropdown_labels,
    #             value=None,
    #             className='dropdown'
    #         )),

    #     html.Button(type='submit', id='save-button', children="Save Data"),
    #     html.Ul(id="file-list"),
    #     html.Div(children=html.Label(["Python code: ", html.A('https://github.com/mallory-archer/cocktail_party/',
    #                                                           href='https://github.com/mallory-archer/cocktail_party/',
    #                                                           style={'color': '#ad1457'})],
    #                                  style={'color': '#E9DDE1'}))
    # ])
    return layout_temp


# Step 4. Create a Dash layout
app.layout = serve_layout


# Step 5. Add callback functions
@app.callback(Output('plot', 'figure'),
              [Input('button', 'n_clicks')],
              [State('input-box', 'value'), State('plot', 'figure')]
              )
def update_figure(n_clicks, phone_number, fig_updated):
    # if value and value_friend:
    #     G.add_nodes_from([value.strip().title()])
    #     G.add_edge(value.strip().title(), value_friend.strip().title(), label=value_relationship)
    if phone_number is not None:
        phone_number = remove_non_numeric(phone_number)

    data_temp = create_fig_data(df, phone_number)
    fig_updated = go.Figure(data=data_temp)


    # fig_updated = create_fig_data()
    # if n_clicks_save is not None:
    #     try:
    #         save_graph_object_to_s3(G, s3_resource, bucket_name, file_loc)
    #     except:
    #         None
    return fig_updated


# @app.callback(Output('wordcloud', 'figure'),
#               [Input('button', 'n_clicks')],
#               [State('input-box', 'value'), State('wordcloud', 'figure')]
#               )
# def update_figure(n_clicks, phone_number, fig_wc_updated):
#     # if value and value_friend:
#     #     G.add_nodes_from([value.strip().title()])
#     #     G.add_edge(value.strip().title(), value_friend.strip().title(), label=value_relationship)
#     if phone_number is not None:
#         phone_number = remove_non_numeric(phone_number)
#
#     # data_temp = create_fig_data(df, phone_number)
#     # fig_updated = go.Figure(data=data_temp)
#
#     data_wc_temp = create_wc_fig_data(word_clouds, select_phone=phone_number, freq='year', select_index=[phone_number, 2016])
#     fig_wc_updated = plot_wordcloud(data_wc_temp, plot_properties)
#
#     # fig_updated = create_fig_data()
#     # if n_clicks_save is not None:
#     #     try:
#     #         save_graph_object_to_s3(G, s3_resource, bucket_name, file_loc)
#     #     except:
#     #         None
#     return fig_wc_updated



#==========================================================================
# def create_wordcloud(data, stopwords, max_words):
#     try:
#         wordcloud_object = WordCloud(
#             stopwords=stopwords,
#             max_words=max_words
#         ).generate(str(data))
#     except:
#         wordcloud_object = None
#     return wordcloud_object


# def plot_wordcloud(wordcloud_object, plot_properties):
#     for prop in plot_properties.keys():
#         # wordcloud_object[prop] = plot_properties[prop]
#         wordcloud_object.__setattr__(prop, plot_properties[prop])
#
#     plt.figure(1, figsize=(12, 12))
#     plt.axis('off')
#     plt.imshow(wordcloud_object)
#     plt.show()


# def get_word_clouds(df, select_phone, freq, max_words):
#     stopwords = set(STOPWORDS)
#
#     # pare dataframe to selected phone numbers
#     if select_phone is not None:
#         df = df.loc[df.phone.isin(select_phone)].reindex()
#
#     # remove characters not relevant for word cloud and convert all to lower case
#     df['text'] = df['text'].apply(funcs.remove_non_ascii)
#     df['text'] = df['text'].str.lower()
#
#     # create dataframe by phone number and desired level of frequency
#     freq_groupby_map = {'year': ['year'], 'month': ['year', 'month'], 'day': ['year', 'month', 'day'], 'all': []}
#     try:
#         df_grouped = pd.DataFrame(df[['phone', 'text'] + freq_groupby_map[freq]].groupby(['phone'] + freq_groupby_map[freq]).text.agg(funcs.cat_texts))
#     except KeyError:
#         print("Invalid frequency, 'freq' must be 'day', 'month', 'year', or None")
#
#     # generate word clouds
#     df_wordcloud = df_grouped['text'].apply(create_wordcloud, stopwords=stopwords, max_words=max_words)
#
#     return df_wordcloud


# def print_wordclouds_to_json(df, output_path, fn):
#     df = df.apply(lambda x: x.words_)
#     df.to_json(os.path.join(output_path, fn + '.json'), orient='index')


# # ----- word cloud data ----
# fn_wordcloud_objects = 'wordcloud_objects'
# # select_phone = None     #['5635804952', '5635802952']     # can be a list of phone numbers (as strings), note single phone number just be in 1-element list, set to 'None' if all phone numbers are to be run
# freq_level_wordcloud = 'month'
# max_words_wordcloud = 100

# # ===== GET WORDCLOUD DATA =====
# select_phone = df_freq_sum.loc[df_freq_sum['count'] >= 10].index.tolist()
# df_wordcloud_objects = create_text_summary_data.get_word_clouds(df_messages, select_phone, freq=freq_level_wordcloud, max_words=max_words_wordcloud)
# if write_to_file:
#     df_wordcloud_objects.to_pickle(os.path.join(output_path, fn_wordcloud_objects + '_' + freq_level_wordcloud))
#     create_text_summary_data.print_wordclouds_to_json(df_wordcloud_objects, output_path, fn=fn_wordcloud_objects + '_' + freq_level_wordcloud)
#
#
# # plot_properties = {'background_color': 'white', 'max_font_size': 40, 'scale': 10, 'random_state': 1}
# # create_text_summary_data.plot_wordcloud(df_wordcloud_objects.iloc[10], plot_properties)
# print(df_wordcloud_objects.loc[['2165262546', 2018, 4],].iloc[0].words_)

# # ===== GET WORDCLOUD DATA =====
# select_phone = df_freq_sum.loc[df_freq_sum['count'] >= 10].index.tolist()
# df_wordcloud_objects = create_text_summary_data.get_word_clouds(df_messages, select_phone, freq=freq_level_wordcloud, max_words=max_words_wordcloud)
# if write_to_file:
#     df_wordcloud_objects.to_pickle(os.path.join(output_path, fn_wordcloud_objects + '_' + freq_level_wordcloud))
#     create_text_summary_data.print_wordclouds_to_json(df_wordcloud_objects, output_path, fn=fn_wordcloud_objects + '_' + freq_level_wordcloud)
#
#
# # plot_properties = {'background_color': 'white', 'max_font_size': 40, 'scale': 10, 'random_state': 1}
# # create_text_summary_data.plot_wordcloud(df_wordcloud_objects.iloc[10], plot_properties)
# print(df_wordcloud_objects.loc[['2165262546', 2018, 4],].iloc[0].words_)


              # [Input('button', 'n_clicks'), Input('save-button', 'n_clicks')],
              # [State('input-box', 'value'), State('input-box-friend', 'value'), State('relationship', 'value'), State('plot', 'figure')]

# Step 6. Add the server clause
application = app.server

if __name__ == '__main__':
    application.run(debug=True, port=select_port)  # Beanstalk expects it to be running on 8080.
