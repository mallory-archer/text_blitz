import pandas as pd
import os


def create_freq_table(df, freq_level):
    req_columns = ['phone', 'is_from_me', 'text', 'date']
    df_temp = None
    if len(set(req_columns) - set(df.columns)) == 0:
        df = df[req_columns].dropna()
        df['date'] = pd.to_datetime(df['date'])
        if freq_level == 'daily':
            df_temp = df.reindex()
            df_temp['date_agg_to_day'] = df_temp.date.dt.date
            df_temp = df_temp[['phone', 'date_agg_to_day', 'text']].groupby(
                ['phone', 'date_agg_to_day']).count().reset_index()
            df_temp.columns = ['phone', 'date', 'count']
            # df_temp['phone'] = df_temp.phone.str.replace(pat='+1', repl='', regex=False)
            df_temp.sort_values(by='date', inplace=True)
    else:
        print('Some of required columns are missing, check create_text_summary_data.create_req_table')

    return df_temp


def get_freq_table(df, freq_level, output_path, fn_freq, write_to_file):
    df_freq = create_freq_table(df, freq_level)
    if write_to_file:
        df_freq.to_csv(os.path.join(output_path, fn_freq), index=False)

    return df_freq


# ===== GET FREQUENCY COUNT DATA =====
# --- Set parameters
path_head = os.getcwd()
dir_input_data = 'input_data'
dir_output_data = 'input_data'
fn_text_processed = 'messages_table.json'
freq_level_count = 'daily'    # currently only option
fn_freq = 'count_text_messages_' + freq_level_count + '.csv'
write_to_file = True

# --- Calculations
input_path = os.path.join(path_head, dir_input_data)
output_path = os.path.join(path_head, dir_output_data)

# --- Summarize table
print('Reading in dataframe of messages from ' + fn_text_processed)
df_messages = pd.read_json(os.path.join(input_path, fn_text_processed))
print('Calculating frequency counts')
df_freq = get_freq_table(df_messages, freq_level_count, output_path, fn_freq, write_to_file)
df_freq_sum = df_freq[['phone', 'count']].groupby('phone').agg(sum).sort_values(by='count', ascending=False)


