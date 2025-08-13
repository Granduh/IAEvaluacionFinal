import pandas as pd
import numpy as np

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df

def add_letters_words_columns(df):
    df['letters'] = df['message'].astype(str).apply(len)
    df['words'] = df['message'].astype(str).apply(lambda s: len(s.split(' ')))
    return df

def add_url_count_column(df):
    df['url_count'] = df['message'].astype(str).apply(lambda x: x.count('LLLL'))
    return df

def basic_stats(df):
    total_message = df.shape[0]
    media_message = df[df['message'] == '<Multimedia omitido>'].shape[0]
    del_message = df[df['message'] == 'Se eliminó este mensaje'].shape[0]
    percent_media = (media_message / total_message) * 100 if total_message else 0
    percent_deleted = (del_message / total_message) * 100 if total_message else 0
    return {
        'total_message': total_message,
        'media_message': media_message,
        'del_message': del_message,
        'percent_media': percent_media,
        'percent_deleted': percent_deleted
    }

def member_stats(df):
    df_no_media = df[df['message'] != '<Multimedia omitido>']
    members = df['author'].unique()
    stat_df = pd.DataFrame(columns=['author', 'n_message', 'n_multimedia', 'prom_words'])
    for member in members:
        member_df = df[df['author'] == member]
        member_no_media = df_no_media[df_no_media['author'] == member]
        n_multimedia = sum(member_df['message'] == '<Multimedia omitido>')
        if member_no_media.shape[0] == 0:
            word_per_message = 0
        else:
            word_per_message = np.sum(member_no_media['words']) / member_no_media.shape[0]
        stat_df = pd.concat([
            stat_df,
            pd.DataFrame([{
                'author': member,
                'n_message': member_df.shape[0],
                'n_multimedia': n_multimedia,
                'prom_words': round(word_per_message, 2)
            }])
        ], ignore_index=True)
    return stat_df
