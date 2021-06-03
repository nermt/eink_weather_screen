import sys
import configparser
import lnetatmo

config = configparser.ConfigParser()
config.read('config.ini')

authData = lnetatmo.ClientAuth( clientId = config['NETATMO']['ClientID'],
                                clientSecret = config['NETATMO']['ClientSecret'],
                                username = config['NETATMO']['Username'],
                                password = config['NETATMO']['Password'])

weatherData = lnetatmo.WeatherStationData(authData)
print ('Current temperature indoor: %s °C, trend is: %s' % (weatherData.lastData()['Vardagsrum']['Temperature'],
                                                            weatherData.lastData()['Vardagsrum']['temp_trend']))

print ('Current temperature outdoor: %s °C, trend is: %s' % (weatherData.lastData()['Utomhus']['Temperature'],
                                                            weatherData.lastData()['Utomhus']['temp_trend']))

print ('Battery of outdoor temperature sensor is: %d' % weatherData.lastData()['Utomhus']['battery_percent'])

print ("It's currently raining with %s mm/h, totally %s mm over the last 24h" % (weatherData.lastData()['Regnmätare']['Rain'],
                                                                              weatherData.lastData()['Regnmätare']['sum_rain_24']))

print ('Battery of rain sensor is: %d' % weatherData.lastData()['Regnmätare']['battery_percent'])
print ('Done')