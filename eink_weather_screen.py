#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os.path
import configparser
import lnetatmo
import sched
import time
import datetime
import logging
from papirus import PapirusComposite

# Update period in seconds.
INTERVAL = 60

# Path to configuration file
CONFIG_FILE = 'config.ini'


def print_error(message):
    global screen_initialized
    eink.Clear()
    eink.AddText('ERROR', 10, 10, 20)
    eink.AddText(message, 10, 35, 14)
    eink.WriteAll()
    screen_initialized = False
    logging.debug('Printing error: screen_initialized is now %s' %
                  screen_initialized)


def show_modal_error(message):
    logging.exception(message)
    print_error(message)


def show_init_error(message):
    show_modal_error()
    quit()


def read_config():
    _config = configparser.ConfigParser()
    _config.read(CONFIG_FILE)
    if os.path.exists(CONFIG_FILE) is False:
        raise Exception("Configuration file doesn't exist")
    logging.info('Configuration file successfully read')
    return _config


def setup_papirus_screen():
    global screen_initialized
    eink.Clear()
    eink.AddText("0°C", 10, 10, Id="outdoor_temp")
    eink.AddText("2021-06-28 22:04:30", 10, 60, 12, Id="timestamp")
    eink.WriteAll()
    screen_initialized = True
    logging.debug('Setting up Papirus: screen_initialized is now %s' %
                  screen_initialized)


def update_screen(wd):
    global screen_initialized
    logging.debug('Updating screen: screen_initialized is now %s' %
                  screen_initialized)
    if screen_initialized is False:
        setup_papirus_screen()

    eink.UpdateText("outdoor_temp", "%s°C" % (wd['Utomhus']['Temperature']))

    ts = wd['Utomhus']['When']
    date = datetime.datetime.fromtimestamp(ts)
    # print(date)
    eink.UpdateText("timestamp", date.strftime("%Y-%m-%d %H:%M:%S"))
    eink.WriteAll(True)


def run_and_update():
    logging.info('New update')
    # Get new data from Netatmo
    try:
        weatherData = lnetatmo.WeatherStationData(authData)
    except lnetatmo.AuthFailure:
        show_init_error('Authentication to Netatmo failed')
    except Exception:
        show_modal_error('Cannot connect to Netatmo, will try again')
        s.enter(INTERVAL, 1, run_and_update)
        return

    # Update screen
    try:
        update_screen(weatherData.lastData())
    except Exception:
        show_modal_error('Cannot update screen, will try again')
        s.enter(INTERVAL, 1, run_and_update)
        return

    # Schedule next run
    s.enter(INTERVAL, 1, run_and_update)

# The following comment is just to show how to get more values from response
    # try:
    #     logging.debug('Current temperature indoor: %s, trend is: %s' %
    #                   (weatherData.lastData()['Vardagsrum']['Temperature'],
    #                    weatherData.lastData()['Vardagsrum']['temp_trend']))

    #     logging.debug('Current temperature outdoor: %s, trend is: %s' %
    #                   (weatherData.lastData()['Utomhus']['Temperature'],
    #                    weatherData.lastData()['Utomhus']['temp_trend']))

    #     logging.debug('Battery of outdoor temperature sensor is: %d' %
    #                   weatherData.lastData()['Utomhus']['battery_percent'])

    #     logging.debug("It's currently raining with %s mm/h, \
    #                    totally %s mm over the last 24h" %
    #                   (weatherData.lastData()['Regnmätare']['Rain'],
    #                    weatherData.lastData()['Regnmätare']['sum_rain_24']))
    #     logging.debug('Battery of rain sensor is: %d' %
    #                   weatherData.lastData()['Regnmätare']['battery_percent'])
    # except Exception:
    #     logging.exception('Logging failed')


def debug():
    weatherData = lnetatmo.WeatherStationData(authData)
    ts = weatherData.lastData()['Utomhus']['When']
    print(datetime.datetime.fromtimestamp(ts))
    print(weatherData.lastData()['Utomhus']['Temperature'])


# Initialization
screen_initialized = False


print(sys.version)
logging.basicConfig(filename='einkscreen.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler())
logging.info('Start: Welcome to einkscreen!')
logging.info('Starting initialization')
logging.debug('Application init: screen_initialized is now %s' %
              screen_initialized)

# Setup papirus
logging.debug('Setting up Papirus')
try:
    eink = PapirusComposite(False)
except Exception:
    show_init_error('Papirus cannot be set up properly')

# Read configuration
logging.debug('Reading configuration file')
try:
    config = read_config()
except Exception:
    show_init_error('Cannot read configuration file')

# Setup Netatmo
logging.debug('Setting up Netatmo client')
try:
    authData = lnetatmo.ClientAuth(
        clientId=config['NETATMO']['ClientID'],
        clientSecret=config['NETATMO']['ClientSecret'],
        username=config['NETATMO']['Username'],
        password=config['NETATMO']['Password'])
except KeyError:
    show_init_error('Incorrect key in configuration file')
except lnetatmo.AuthFailure:
    show_init_error('Authentication to Netatmo failed')
except Exception:
    show_init_error('Cannot connect to Netatmo')

# Setup scheduling
logging.debug('Setting up scheduler')
s = sched.scheduler(time.time, time.sleep)

logging.info('Initialization complete')
logging.info('Starting application')

# Application section
run_and_update()
s.run()
