import re
import pandas as pd

def date_chat(line):
    # Soporta fechas tipo: 7/26/25, 4:53 PM - ... (con espacio normal o especial)
        # Soporta fechas tipo inglés: 7/26/25, 4:53 PM - ...
        pattern_en = r'^(\d{1,2}/\d{1,2}/\d{2}),?\s\d{1,2}:\d{2}(?:\s|\u202f|\u2009|\u200a|\u200b|\u2002|\u2003|\u2004|\u2005|\u2006|\u2007|\u2008|\u2009|\u200a|\u202f|\u205f|\u3000)[AP]M\s-'
        # Soporta fechas tipo español: 12/6/2024, 8:15 p. m. - ...
        pattern_es = r'^(\d{1,2}/\d{1,2}/\d{4}),?\s\d{1,2}:\d{2}(?:\s|\u202f|\u2009|\u200a|\u200b|\u2002|\u2003|\u2004|\u2005|\u2006|\u2007|\u2008|\u2009|\u200a|\u202f|\u205f|\u3000)p\.\u202fm\.\s-'
        # También soporta p. m. y a. m. con o sin espacios
        pattern_es2 = r'^(\d{1,2}/\d{1,2}/\d{4}),?\s\d{1,2}:\d{2}(?:\s|\u202f|\u2009|\u200a|\u200b|\u2002|\u2003|\u2004|\u2005|\u2006|\u2007|\u2008|\u2009|\u200a|\u202f|\u205f|\u3000)[ap]\.\s?m\.\s-'
        return bool(re.match(pattern_en, line) or re.match(pattern_es, line) or re.match(pattern_es2, line))

def is_author(line):
    # Detecta nombres (con caracteres especiales y emojis) y números de teléfono seguidos de ':'
    # Ejemplo: 'Gordo forro: mensaje', '+593 96 834 7792: mensaje'
    pattern = r'^([\w\s\+\d\-\(\)\u00C0-\u017F\u1F600-\u1F64F]+):'
    result = re.match(pattern, line)
    return bool(result)

def data_point(line):
    split_line = line.split(' - ', 1)
    dt = split_line[0]
    date_time = dt.split(', ')
    date = date_time[0]
    message = split_line[1] if len(split_line) > 1 else ''
    # Detectar formato inglés o español
    # Inglés: 1/7/25, 11:26 AM
    # Español: 12/6/2024, 8:15 p. m.
    if re.match(r'\d{1,2}/\d{1,2}/\d{2},', dt):
        # Inglés
        date_time = dt.split(', ')
        date = date_time[0]
        time_fmt = date_time[1].split(' ')
        time = time_fmt[0]
        fmt = time_fmt[1] if len(time_fmt) > 1 else ''
    elif re.match(r'\d{1,2}/\d{1,2}/\d{4},', dt):
        # Español
        date_time = dt.split(', ')
        date = date_time[0]
        # Puede venir como "8:15\u202fp.\u202fm." o "8:15 p. m."
        time_part = date_time[1]
        # Quitar espacios unicode
        time_part = re.sub(r'[\u202f\u2009\u200a\u200b\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000]', ' ', time_part)
        # Buscar hora y formato
        match = re.match(r'(\d{1,2}:\d{2})\s*([ap]\.\s?m\.|[ap]\.\u202fm\.)', time_part)
        if match:
            time = match.group(1)
            fmt = match.group(2)
        else:
            # fallback: separar por espacio
            time_fmt = time_part.split(' ')
            time = time_fmt[0]
            fmt = ' '.join(time_fmt[1:])
    else:
        date = time = fmt = ''
    if is_author(message):
        authormes = message.split(': ', 1)
        author = authormes[0]
        message = authormes[1] if len(authormes) > 1 else ''
    else:
        author = None
    return date, time, fmt, author, message

def dataframe_data(file_path):
    parsed_data = []
    with open(file_path, encoding="utf-8") as fp:
        message_buffer = []
        date = time = fmt = author = None
        while True:
            line = fp.readline()
            if not line:
                break
            line = line.strip()
            if date_chat(line):
                if len(line) > 0:
                    parsed_data.append([date, time, fmt, author, ' '.join(message_buffer)])
                message_buffer.clear()
                date, time, fmt, author, message = data_point(line)
                message_buffer.append(message)
            else:
                message_buffer.append(line)
    df = pd.DataFrame(parsed_data, columns=['date', 'time', 'format', 'author', 'message'])
    return df

def protec_info(text):
    patron = r'\b\d{3}[-\s]?\d{7}\b|\(\d{3}\)[-.\s]?\d{3}[-.\s]?\d{4}\b'
    text = re.sub(patron, ' NNNN ', text)
    patron = r'\bhttps?://\S+\b'
    text = re.sub(patron, 'LLLL', text)
    patron = r'@\w+\s?'
    text = re.sub(patron, 'UUUU ', text)
    patron = r'\bwa.me/\d+\b'
    text = re.sub(patron, 'NNNN', text)
    return text
