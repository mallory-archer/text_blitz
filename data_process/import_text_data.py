import sqlite3
import os
import pandas as pd


# --- import apple backup text message data as tables ---
def import_raw_txt_data(input_data_path_text, fn_text_data, fn_names, output_data_path, write_to_file):
    tables_processed = dict()
    with sqlite3.connect(os.path.join(input_data_path_text, fn_text_data)) as db:
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
    for table_name in tables:
        table_name = table_name[0]
        if table_name in fn_names.values():
            print('Reading table ' + table_name)
            if table_name == 'message':
                table = pd.read_sql_query("select datetime(substr(date, 1, 9) + 978307200, 'unixepoch', 'localtime') as date_convert, datetime(substr(date_read, 1, 9) + 978307200, 'unixepoch', 'localtime') as date_read_convert, datetime(substr(date_delivered, 1, 9) + 978307200, 'unixepoch', 'localtime') as date_delivered_convert, * from message", db)
                table = table.drop(columns={'date', 'date_delivered', 'date_read'}).rename(columns={'date_convert': 'date', 'date_delivered_convert': 'date_delivered', 'date_read_convert': 'date_read'})
            else:
                table = pd.read_sql_query("SELECT * from %s" % table_name, db)
            tables_processed[table_name] = table

            if write_to_file:
                print('Writing table ' + table_name)
                table.to_csv(os.path.join(output_data_path, table_name + '.csv'), index_label='index')
    return tables_processed


# --- join text tables to get master table ---
def import_relevant_text_tables(fn_names, df_dict, output_data_path):
    if df_dict is not None:
        df_message = df_dict[fn_names['fn_message']]
        df_handle = df_dict[fn_names['fn_handle']]
        df_chat = df_dict[fn_names['fn_chat']]
        df_chat_handle_join = df_dict[fn_names['fn_chat_handle_join']]
        df_chat_message_join = df_dict[fn_names['fn_chat_message_join']]

    if len(set([f + '.csv' for f in list(fn_names.values())]) - set(os.listdir(output_data_path))) == 0:
        df_message = pd.read_csv(os.path.join(output_data_path, fn_names['fn_message'] + '.csv'))
        df_handle = pd.read_csv(os.path.join(output_data_path, fn_names['fn_handle'] + '.csv'), dtype={'id': str})
        df_chat = pd.read_csv(os.path.join(output_data_path, fn_names['fn_chat'] + '.csv'))
        df_chat_handle_join = pd.read_csv(os.path.join(output_data_path, fn_names['fn_chat_handle_join'] + '.csv'))
        df_chat_message_join = pd.read_csv(os.path.join(output_data_path, fn_names['fn_chat_message_join'] + '.csv'))

    df_chat_handle_join = df_chat_handle_join.merge(df_handle[['ROWID', 'id']].rename(columns={'ROWID': 'handle_id', 'id': 'phone'}), how='left', on='handle_id')
    df_chat = df_chat.merge(df_chat_handle_join[['chat_id', 'phone']].rename(columns={'chat_id': 'ROWID'}), how='left', on='ROWID')
    df_chat_message_join = df_chat_message_join.merge(df_chat[['ROWID', 'phone']].rename(columns={'ROWID': 'chat_id'}), how='left', on='chat_id')
    df_message = df_message.merge(df_chat_message_join[['message_id', 'phone']].rename(columns={'message_id': 'ROWID'}), how='left', on='ROWID')
    return df_message


def get_text_data(path_head, dir_output_data, input_data_path_text, fn_text_data, write_to_file, read_raw_data):
    fn_names = {'fn_message': 'message',
                'fn_handle': 'handle',
                'fn_chat': 'chat',
                'fn_chat_handle_join': 'chat_handle_join',
                'fn_chat_message_join': 'chat_message_join'}
    output_data_path = os.path.join(path_head, dir_output_data)

    if read_raw_data:
        tables_processed = import_raw_txt_data(input_data_path_text, fn_text_data, fn_names, output_data_path,
                                               write_to_file)
    else:
        tables_processed = None
    df_message = import_relevant_text_tables(fn_names, tables_processed, output_data_path)
    return df_message


def clean_messages_table(df, strip_chars):
    df_clean = df.reindex()
    for col_key in strip_chars.keys():
        for str_key in strip_chars[col_key].keys():
            df_clean[col_key] = df_clean[col_key].str.replace(pat=str_key, repl=strip_chars[col_key][str_key], regex=False)

    df_clean['datetime'] = pd.to_datetime(df_clean.date, errors='coerce')
    df_clean['year'] = df_clean['datetime'].apply(lambda x: x.year)
    df_clean['month'] = df_clean['datetime'].apply(lambda x: x.month)
    df_clean['day'] = df_clean['datetime'].apply(lambda x: x.day)

    return df_clean

# ===== GET TEXT DATA =====
path_head = os.getcwd()
dir_input_data = 'input_data'
fn_text_data = '3d0d7e5fb2ce288813306e4d4636395e047a3d28'
fn_text_processed = 'messages_table.json'
write_to_file = True
read_raw_data = False    # if false, loads from preprocessed/saved csv files
dir_output_data = 'input_data'

input_data_path_text = os.path.join(path_head, dir_input_data)
output_data_path_json = os.path.join(path_head, dir_output_data)

try:
    df_messages = get_text_data(path_head, dir_output_data, input_data_path_text, fn_text_data, write_to_file, read_raw_data)
    df_messages = clean_messages_table(df_messages, strip_chars={'phone': {'+1': ''}})
    df_messages.to_json(os.path.join(output_data_path_json, fn_text_processed))
except UnboundLocalError as e:
    print('Error: ' + e + ". Try running file with 'read_raw_data' set to True.")
