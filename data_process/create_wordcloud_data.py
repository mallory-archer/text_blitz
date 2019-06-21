import os
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import pickle


def create_wordcloud(data, stopwords, max_words):
    try:
        wordcloud_object = WordCloud(
            stopwords=stopwords,
            max_words=max_words
        ).generate(str(data))
    except:
        wordcloud_object = None
    return wordcloud_object


def remove_non_ascii(x):
    try:
        y = ''.join([i if 32 < ord(i) < 126 else " " for i in x])
        return y
    except:
        return None


def cat_texts(x):
    return ' '.join(x.astype(str))


def get_word_clouds(df, select_phone, freq, stopwords, max_words):
    # remove characters not relevant for word cloud and convert all to lower case
    df['text'] = df['text'].apply(remove_non_ascii).reindex()
    df['text'] = df['text'].str.lower().reindex()

    # create dataframe by phone number and desired level of frequency
    freq_groupby_map = {'year': ['year'], 'month': ['year', 'month'], 'day': ['year', 'month', 'day'], 'all': []}
    try:
        if (select_phone is None) or (select_phone == ''):
            if freq == 'all':
                df_grouped = pd.DataFrame(data={'text': [df.text.str.cat(sep=' ')]}).reindex()
            else:
                df_grouped = pd.DataFrame(df[['text'] + freq_groupby_map[freq]].groupby(freq_groupby_map[freq]).text.agg(cat_texts)).reindex()
        else:
            df_select = df[df.phone.isin(select_phone)].reindex()
            df_grouped = pd.DataFrame(df_select[['phone', 'text'] + freq_groupby_map[freq]].groupby(['phone'] + freq_groupby_map[freq]).text.agg(cat_texts)).reindex()

        df_wordcloud = df_grouped['text'].apply(create_wordcloud, stopwords=stopwords, max_words=max_words).reindex()
    except:
        print("Invalid frequency, 'freq' must be 'day', 'month', 'year', or 'all'")
        df_wordcloud = None

    return df_wordcloud


# --- input parameters
filepath_input_data = 'input_data'     #### DELETE DATA PROCESS WHEN RUNNING
filename_input_data = 'messages_table.json'
filepath_output_data = 'wordclouds'         #### DELETE DATA PROCESS WHEN RUNNING
filename_output_data = 'word_clouds.pkl'
max_words = 100

#####
select_phone = ['2165262546', '5635804952']     # + [None]
freq = ['all', 'year']      # 'month', 'day']
#####

# --- calculations
file_loc_input_data = os.path.join(filepath_input_data, filename_input_data)
file_loc_output_data = os.path.join(filepath_output_data, filename_output_data)
df_messages = pd.read_json(file_loc_input_data)
stopwords = set(STOPWORDS)

word_clouds = dict()
for p in select_phone:
    temp_dict = dict()
    print('Working on phone: ' + p)
    for f in freq:
        print('Working on freq: ' + f)
        wordcloud_object = get_word_clouds(df_messages.reindex(), [p], f, stopwords, max_words)
        temp_dict.update({f: wordcloud_object})
    word_clouds.update({p: temp_dict})

# save word cloud data objects
with open(file_loc_output_data, "wb") as f:
    pickle.dump(word_clouds, f)











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






# def print_wordclouds_to_json(df, output_path, fn):
#     df = df.apply(lambda x: x.words_)
#     df.to_json(os.path.join(output_path, fn + '.json'), orient='index')


