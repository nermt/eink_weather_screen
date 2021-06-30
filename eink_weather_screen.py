#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import configparser
import lnetatmo
import sched, time
import datetime
from papirus import PapirusComposite

INTERVAL = 60

# Read configuration
config = configparser.ConfigParser()
config.read('config.ini')

# Setup Netatmo
authData = lnetatmo.ClientAuth( clientId = config['NETATMO']['ClientID'],
                                clientSecret = config['NETATMO']['ClientSecret'],
                                username = config['NETATMO']['Username'],
                                password = config['NETATMO']['Password'])

# Setup papirus
eink = PapirusComposite(False)

# Setup scheduling
s = sched.scheduler(time.time, time.sleep)


def setup_papirus_screen():
    eink.Clear()
    eink.AddText("0°C", 10, 10, Id="outdoor_temp")
    eink.AddText("2021-06-28 22:04:30", 10, 60, 12, Id="timestamp")
    eink.WriteAll()

def update_screen(wd):
    eink.UpdateText("outdoor_temp", "%s°C" % (wd['Utomhus']['Temperature']))

    ts = wd['Utomhus']['When']
    date = datetime.datetime.fromtimestamp(ts)
    print(date)
    eink.UpdateText("timestamp", date.strftime("%Y-%m-%d %H:%M:%S"))
    eink.WriteAll(True)

def run_and_update():
    weatherData = lnetatmo.WeatherStationData(authData)

    

    update_screen(weatherData.lastData())
    print ('Current temperature indoor: %s, trend is: %s' % (weatherData.lastData()['Vardagsrum']['Temperature'],
                                                            weatherData.lastData()['Vardagsrum']['temp_trend']))

    print ('Current temperature outdoor: %s, trend is: %s' % (weatherData.lastData()['Utomhus']['Temperature'],
                                                            weatherData.lastData()['Utomhus']['temp_trend']))

    print ('Battery of outdoor temperature sensor is: %d' % weatherData.lastData()['Utomhus']['battery_percent'])

    print ("It's currently raining with %s mm/h, totally %s mm over the last 24h" % (weatherData.lastData()['Regnmätare']['Rain'],
                                                                              weatherData.lastData()['Regnmätare']['sum_rain_24']))

    print ('Battery of rain sensor is: %d' % weatherData.lastData()['Regnmätare']['battery_percent'])
    print ('Done')
    s.enter(INTERVAL, 1, run_and_update)

def debug():
    weatherData = lnetatmo.WeatherStationData(authData)
    ts = weatherData.lastData()['Utomhus']['When']
    #print(ts)
    #date = datetime.datetime.fromtimestamp(ts)
    print(datetime.datetime.fromtimestamp(ts))
    print(weatherData.lastData()['Utomhus']['Temperature'])

#debug()
setup_papirus_screen()
run_and_update()
s.enter(INTERVAL, 1, run_and_update)
s.run()
