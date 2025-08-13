import re
import emoji
import string
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
import io
import streamlit as st

def delete_tilde(text):
    list_char = ['á','é','í','ó','ú','ü']
    list_sust = ['a','e','i','o','u','u']
    for i, x in enumerate(list_char):
        if x in text:
            text = text.replace(x, list_sust[i])
    text = text.lower()
    return text

def remove_punctuation(text):
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    return text

def regex_word(text):
    word = [
        '\s\<(M|m)ultimedia\somitido\>', '\somitido\s', '\smultimedia\s','https?\S*',
        '(\<Multimedia\s)', '\w+\.vcf','\(archivo\sadjunto\)',
        'omitido\>', '\s{4}', '\s{3}', '\s{2}', '\s[a-zA-Z]\s',
        '\svcf', '\s(p|P)\s(m|M)\s', '\s(p|P)(m|M)\s', '\sp\s',
        '\sm\s', '\sde\s', '\scon\s', '\sque\s', '\sla\s',
        '\slo\s', '\spara\s', '\ses\s', '\sdel\s', '\spor\s',
        '\sel\s', '\sen\s', '\slos\s', '\stu\s', '\ste\s',
        '[\w\._]{5,30}\+?[\w]{0,10}@[\w\.\-]{3,}\.\w{2,5}',
    '\sun\s', '\sus\s', 'su\s', '\s\u200e', '\u200e', '\s\s',
        '\s\s\s', '\s\u200e3', '\s\u200e2', '\s\.\.\.\s', '/',
        '\s\u200e4', '\s\u200e7', '\s\u200e8', '\suna\s',
        'la\s', '\slas\s', '\sse\s', '\sal\s','\sle\s',
        '\sbuenas\s', '\sbuenos\s', '\sdias\s', '\stardes\s', '\snoches\s',
        '\sesta\s', '\spero\s','\sdia\s', '\sbuenas\s', '\spuede\s', '\spueden\s',
        '\sson\s', '\shay\s', '\seste\s', '\scomo\s', '\salgun\s', '\salguien\s',
        '\stodo\s', '\stodos\s', '\snos\s', '\squien\s', '\seso\s', '\sdesde\s',
        '\sarchivo\sadjunto\s', 'gmailcom', '\sdonde\s', '\shernan\s', '\slavadoras\s',
        'gracias', '\selimino\smensaje\s', '\snnnn\s',
        '\sllll\s', '\slll/\s', 'llll'
    ]
    regexes = [re.compile(p) for p in word]
    for regex in regexes:
        text = regex.sub(' ', text)
    return text

def delete_emoji(text):
    return emoji.replace_emoji(text, replace='')

def nube_words(df, fecha):
    text = ' '.join(df['message'])
    text = delete_emoji(text)
    text = delete_tilde(text)
    text = remove_punctuation(text)
    text = regex_word(text)
    # Usa la fuente local descargada desde Google Fonts
    wordcloud = WordCloud(
        stopwords=STOPWORDS,
        background_color='white',
        width=1600,  # mayor resolución horizontal
        height=800,  # mayor resolución vertical
        scale=2      # escala interna para más nitidez
    ).generate(text)
    buf = io.BytesIO()
    fig, ax = plt.subplots(figsize=(16, 8), dpi=200)
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title(fecha)
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=200)
    plt.close(fig)
    buf.seek(0)
    st.image(buf, caption=fecha)
