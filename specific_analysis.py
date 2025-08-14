import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from utils import delete_emoji, delete_tilde, remove_punctuation, regex_word, nube_words

# Cargar datos y preparar columnas

def load_data(csv_path):
    df = pd.read_csv(csv_path)
    return df

def add_words_column(df):
    df['words'] = df['message'].fillna('').apply(lambda s: len(s.split(' ')))
    return df

def filter_no_media(df):
    return df[df['message'] != '<Multimedia omitido>']

# Análisis de miembro

def analysis_member(df, member):
    # Filtrar mensajes que no sean media omitted
    df_no_media = filter_no_media(df)
    df_no_media = df_no_media[~df_no_media['message'].str.contains('<Media omitted>|<Multimedia omitido>', case=False, na=False)]
    df_member = df_no_media[df_no_media['author'] == member].copy()
    df_member['message'] = df_member['message'].fillna('')
    text = ' '.join(df_member['message'])
    text = delete_emoji(text)
    text = delete_tilde(text)
    text = remove_punctuation(text)
    text = regex_word(text)
    nube_words(df_member, f'Nube de palabras: {member}')
    return text

def line_time_member(df, member):
    df_member = df[df['author'] == member].copy()
    # Filtrar mensajes que no sean media omitted
    df_member = df_member[~df_member['message'].str.contains('<Media omitted>|<Multimedia omitido>', case=False, na=False)]
    # Convertir fechas de forma robusta (acepta m/d/yy y d/m/yyyy)
    df_member['date'] = pd.to_datetime(df_member['date'], dayfirst=True, errors='coerce')
    df_member = df_member.dropna(subset=['date'])
    df_member['month'] = df_member['date'].dt.month
    df_member['num_day'] = df_member['date'].dt.day
    df_member['date'] = df_member['date'].dt.strftime('%Y-%m-%d')
    line_time = df_member.groupby(['date', 'month', 'num_day']).count()['message'].reset_index()
    line_time_order = line_time.sort_values(by='message', ascending=False).reset_index()
    # Graficar línea de tiempo
    fig, ax = plt.subplots(figsize=(14, 5), dpi=150)
    ax.plot(line_time['date'], line_time['message'], marker='o')
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Cantidad de mensajes')
    ax.set_title(f'Línea de tiempo de mensajes para {member}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    return line_time, line_time_order
