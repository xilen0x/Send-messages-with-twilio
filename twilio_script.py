"""
************************************************************************
*               Envio de mensajes Twilio con Python                    *
************************************************************************
"""
import os
from twilio.rest import Client
from twilio_config import TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN,PHONE_NUMBER,API_KEY_WAPI
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import pandas as pd
import requests
from tqdm import tqdm
from datetime import datetime
#from utils import request_wapi,get_forecast,create_df,send_message,get_date

def get_date():

    input_date = datetime.now()
    input_date = input_date.strftime("%Y-%m-%d")

    return input_date

def request_wapi(api_key,query):

    url_clima = 'http://api.weatherapi.com/v1/forecast.json?key='+api_key+'&q='+query+'&days=1&aqi=no&alerts=no'

    try :
        response = requests.get(url_clima).json()
    except Exception as e:
        print(e)

    return response

query = 'Barcelona'
api_key = API_KEY_WAPI

input_date= get_date()
response = request_wapi(api_key,query)
#print(response)

# funcion que recoge los valores antes filtrados
def get_forecast(response, i):
    fecha = response['forecast']['forecastday'][0]['hour'][i]['time'].split()[0]
    hora = int(response['forecast']['forecastday'][0]['hour'][i]['time'].split()[1].split(':')[0])
    condicion = response['forecast']['forecastday'][0]['hour'][i]['condition']['text']
    temperatura = response['forecast']['forecastday'][0]['hour'][i]['temp_c']
    lluvia = response['forecast']['forecastday'][0]['hour'][i]['will_it_rain']
    prob_lluvia = response['forecast']['forecastday'][0]['hour'][i]['chance_of_rain']

    return fecha, hora, condicion, temperatura, lluvia, prob_lluvia


datos = []

for i in tqdm(range(len(response['forecast']['forecastday'][0]['hour'])), colour = 'green'):
    datos.append(get_forecast(response, i))

# creando las columnas del df
col = ['Fecha', 'Hora', 'Condicion', 'Temperatura', 'Lluvia', 'Prob_lluvia']

df = pd.DataFrame(datos, columns=col )


# Filtro el df con las horas que me importan. En este caso las de probabilidad de lluvia.
df_f = df[ (df['Hora']>7) & (df['Hora']<21) ]

# me quedo solo con las columnas que me importan
df_f = df_f[['Hora','Condicion']]

# cambio de índice
df_f.set_index('Hora', inplace=True)

# template para luego enviar al celular
template = '\nHola Carlos! \n\n El pronostico del tiempo para hoy '+ df['Fecha'][0] + ' en '+ query + ' es : \n\n '+ str(df_f)
print(template)

time.sleep(2)
account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN

client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                    body = template,
                    from_ = PHONE_NUMBER,
                    to = '+34 610 86 58 16'#your number
                )

print('El mensaje fue enviado con éxito!' + message.sid)