import streamlit as st
import pandas as pd
from preparation_data import dataframe_data, protec_info
from general_analysis import load_data, add_letters_words_columns, add_url_count_column, basic_stats, member_stats
from specific_analysis import analysis_member, line_time_member

st.title('Análisis de chats de WhatsApp')
st.write('Sube tu archivo de chat de WhatsApp para analizarlo.')

# Subir archivo de chat
uploaded_file = st.file_uploader('Selecciona el archivo de chat (.txt)', type=['txt'])

if uploaded_file is not None:
	# Guardar archivo temporalmente
	with open('chat_temp.txt', 'wb') as f:
		f.write(uploaded_file.read())



	# Procesar y limpiar datos
	df = dataframe_data('chat_temp.txt')
	df = df.drop(range(0,1)).reset_index(drop=True)
	df = df.drop(df[df['message'] == ''].index).reset_index(drop=True)
	miembros = df['author'].unique()
	for i, m in enumerate(miembros):
		if pd.notnull(m):
			df['author'] = df['author'].replace(m, f'user {i}')
	df['message'] = df['message'].apply(protec_info)
	df = df.dropna(subset=['author'])
	df = df.reset_index(drop=True)

	# Mostrar tabla de datos
	st.subheader('Vista previa de los datos procesados')
	st.dataframe(df.head(20))

	# Análisis general
	st.subheader('Estadísticas generales')
	df = add_letters_words_columns(df)
	df = add_url_count_column(df)
	stats = basic_stats(df)
	st.write(f"Total de mensajes: {stats['total_message']}")
	st.write(f"Mensajes multimedia: {stats['media_message']} ({stats['percent_media']:.2f}%)")
	st.write(f"Mensajes eliminados: {stats['del_message']} ({stats['percent_deleted']:.2f}%)")
	st.write(f"Total de links: {df['url_count'].sum()}")

	# Estadísticas por miembro
	st.subheader('Estadísticas por miembro')
	stat_df = member_stats(df)
	st.dataframe(stat_df)

	# Análisis específico
	st.subheader('Análisis específico por miembro')
	member_selected = st.selectbox('Selecciona un miembro', stat_df['author'].unique())
	if st.button('Mostrar nube de palabras y línea de tiempo'):
		st.write(f'Nube de palabras para {member_selected}')
		analysis_member(df, member_selected)
		st.write(f'Línea de tiempo de mensajes para {member_selected}')
		line_time, line_time_order = line_time_member(df, member_selected)
		st.dataframe(line_time.head())
