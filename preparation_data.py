import re
import pandas as pd

def date_chat(line):
    # Soporta fechas tipo: 7/26/25, 4:53 PM - ... (con espacio normal o especial)
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2}),?\s\d{1,2}:\d{2}(?:\s|\u202f|\u2009|\u200a|\u200b|\u2002|\u2003|\u2004|\u2005|\u2006|\u2007|\u2008|\u2009|\u200a|\u202f|\u205f|\u3000)[AP]M\s-'
    result = re.match(pattern, line)
    return bool(result)

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
    # Soporta espacios especiales después de la hora
    time_format = re.split(r'[ \u202f\u2009\u200a\u200b\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u202f\u205f\u3000]', date_time[1])
    time = time_format[0]
    fmt = time_format[1]
    message = split_line[1] if len(split_line) > 1 else ''
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
