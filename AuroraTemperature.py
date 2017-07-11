import os
from time import sleep
import requests
from nanoleaf import Aurora
from colour import Color
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


class AuroraHandler:

    IP = os.environ.get('AURORA_IP')
    AUTH_TOKEN = os.environ.get('AUTH_TOKEN')

    def show_temperature(self, temp):
        my_aurora = Aurora(self.IP, self.AUTH_TOKEN)
        red = Color("blue")
        colors = list(red.range_to(Color("red"), 50))
        color = colors[int(temp) + 10]
        hex = color.get_hex_l()[1:]
        my_aurora.rgb = hex
        my_aurora.brightness = 40
        sleep(2)
        my_aurora.on = False


class Netatmo:

    NETATMO_CLIENT_ID = os.environ.get('NETATMO_CLIENT_ID')
    NETATMO_CLIENT_SECRET = os.environ.get('NETATMO_CLIENT_SECRET')
    NETATMO_AUTH_ENDPOINT = 'https://api.netatmo.com/oauth2/token'
    NETATMO_DATA_ENDPOINT = 'https://api.netatmo.com/api/getmeasure'
    NETATMO_STATION_ENDPOINT = 'https://api.netatmo.com/api/getstationsdata'

    def __init__(self, station_name):
        self.STATION_NAME = station_name

    def get_tokens(self):
        scopes = 'read_station read_thermostat write_thermostat'
        params = {'grant_type': 'password',
                  'client_id': self.NETATMO_CLIENT_ID,
                  'client_secret': self.NETATMO_CLIENT_SECRET,
                  'username': os.environ.get('NETATMO_USERNAME'),
                  'password': os.environ.get('NETATMO_PW'),
                  'scope': scopes}
        headers = {'Content-type': 'application/x-www-form-urlencoded'}
        r = requests.post(self.NETATMO_AUTH_ENDPOINT, data=params, headers=headers)
        access_token = r.json()['access_token']
        refresh_token = r.json()['refresh_token']
        return access_token, refresh_token

    def get_temperature(self, access_tkn):
        access_token = {'access_token': access_tkn}
        r = requests.get(self.NETATMO_STATION_ENDPOINT, params=access_token)
        stations = r.json()['body']['devices']
        for station in stations:
            if station['station_name'] == self.STATION_NAME:
                for module in station['modules']:
                    if module['module_name'] == os.environ.get('MODULE_NAME'):
                        return module['dashboard_data']['Temperature']


netatmo = Netatmo(os.environ.get('STATION_NAME'))
access_tkn, refresh_tkn = netatmo.get_tokens()
temperature = netatmo.get_temperature(access_tkn)

aurora = AuroraHandler()
print(temperature)
aurora.show_temperature(temperature)

