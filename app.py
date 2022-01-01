import speech_recognition as sr   
import streamlit as st
import re 
import pandas as pd
from PIL import Image

import base64
import io

#-------------------------


import av
import cv2
from aiortc.contrib.media import MediaRecorder

from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer


file = 'favicon.png'
favicon = Image.open(file)

st.set_page_config(
        page_title="AInigma LABS",
        page_icon= 'https://ainigma.com.ar/media/favicon.png',
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
             'Get Help': 'https://www.instagram.com/Ainigma.labs',
             'Report a bug': "https://www.ainigma.com.ar",
            'About': "# AInigma LABS. Soluciones a tus problemas!"
        }
    )

# Sidebar section
file = 'logo.png'
image = Image.open(file)

st.sidebar.image(image)
st.sidebar.write('## AInigma')
st.sidebar.write('### Gracias por confiar en nosotros!')

def word2num (num):
    numbers = {
            'uno':1,'dos':2,"tres":3,"cuatro":4,
            'cinco':5,'seis':6,'siete':7,'ocho':8,
            'nueve':9,'zero':0,'diez':10,
            'once':11, 'doce':12, 'trece':13, 'catorce':14, 'quince':15, 'dieciseis':16, 'diecisiete':17,
            'dieciocho':18, 'diecinueve':19,
            'veinte':20,'treinta':30,'cuarenta':40,
            'cincuenta':50,'sesenta':60,'setenta':70,
            'ochenta':80,'noventa':90
        }
    if (num in numbers):
        return str(numbers[num])
    else: 
        return num
    '''
    try:
        return int(num)
    except:
        return num
    '''
class OpenCVEdgeProcessor(VideoProcessorBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

            # perform edge detection
        img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def in_recorder_factory() -> MediaRecorder:
    return MediaRecorder(
        "input.flv", format="flv"
    )  # HLS does not work. See https://github.com/aiortc/aiortc/issues/331

def out_recorder_factory() -> MediaRecorder:
    return MediaRecorder("output.flv", format="flv")

webrtc_streamer(
        key="loopback",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={
            "video": True,
            "audio": True,
        },
        video_processor_factory=OpenCVEdgeProcessor,
        in_recorder_factory=in_recorder_factory,
        out_recorder_factory=out_recorder_factory,
    )


'''
# Conversor de Audio de voz a planilla Excel 

## Ingrese un audio y se formará un excel automáticamente.

### El formato debe ser:
* Cualquier duración PESO MÁXIMO 200MB y se debe escuchar claro para evitar posibles errores (a más largo, más tardará en procesarlo).
* Los formatos permitidos se indican debajo. Recomendado WAV.
* Se deben indicar la cantidad de palabras por celda para cada columna y la cantidad de columnas totales 
'''

st.write('''
### Al elegir la cantidad de palabras por celda debe tener en cuenta que cada columna debe tener la misma cantidad de datos (no se aceptan celdas vacías) y se deben completar la cantidad de palabras totales (se indican una vez cargado el audio)!
''')

audio_upload = st.file_uploader('Ingrese el audio en fomarto MP3, MP4, WAV, FLAC', type=['wav', 'mp3', 'mp4', 'flac'])

buttons = []

AUDIO_FILE = audio_upload

cant_columns = st.number_input('''Ingrese cuantas columnas quiere generar.
        Tenga en cuenta que el número de columnas sea compatible con los datos que usted posee, por ejemplo si tiene 8 palabras, puede generar 1, 2, 4 u 8 columnas, variando también la cantidad de palabras por celda
    ''', 1)
columns = {}
for i in range(cant_columns):
    buttons.append(st.number_input('Ingrese la cantidad de palabras para las filas de la columna ' + str(i+1), 1))
    columns[i] = []
if (AUDIO_FILE is not None):
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        audio = r.record(source)  # read the entire audio file
    try:
        txt = r.recognize_google(audio, language='es-ES')
        st.write("Usted dijo: " + txt)
        s = re.split('\s', txt)
        st.write('La cantidad de datos es: ' + str(len(s)))
        correct = st.button('Sí! Comenzar conversión')
        not_correct = st.button('No :(. Intentar de nuevo')
    except sr.UnknownValueError:
        st.write("Imposible entender el audio. Pruebe de nuevo con otro")
    except sr.RequestError as e:
        st.write("Error de la API, por favor vuelva a intentar; {0}".format(e))

    if (correct):
        st.write('Espere mientras se genera la planilla')
        column_pos, word, i, button_pos = 0, 0, 0, 0
        while (i < len(s)):
            tmp = ''
            for j in range(int(buttons[button_pos])):
                tmp += word2num(s[word]) + ' '
                if (word + 1 < len(s)):
                    word += 1
                else:
                    break
            columns[button_pos].append(tmp)
            if (button_pos + 1 == cant_columns):
                button_pos = 0
            else:
                button_pos += 1
            i += buttons[button_pos]
        df = pd.DataFrame()
        for i in range(len(columns)):
            if (len(columns[i]) > 0):
                df[i] = columns[i]
        st.dataframe(df, width=1000)
        
    if (not_correct):
        st.write(''' ## Vuelva a intentarlo o grabe otro audio por favor!''')


#-------------------------
