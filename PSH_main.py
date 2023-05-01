# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 15:50:16 2023

@author: jayaram
"""
import datetime
import pandas as pd
import numpy as np
import pvlib

# input parameters

latitude = 37.7749295
longitude = -122.4194155
elevation = 10 # meters
timezone = 'US/Pacific'
# create time range
start = pd.Timestamp(datetime.date.today(), tz=timezone)
end = start + pd.Timedelta(days=1)
time_range = pd.date_range(start=start, end=end, closed='left', freq='1min')

# get solar position
solar_position = pvlib.solarposition.get_solarposition(time_range, latitude, longitude)

# calculate clear sky irradiance
location = pvlib.location.Location(latitude, longitude, tz=timezone, altitude=elevation)
pressure = pvlib.atmosphere.alt2pres(location.altitude)
clearsky = location.get_clearsky(time_range, model='ineichen')

# calculate total irradiance on a tilted surface
surface_azimuth = 180 # degrees (south-facing)
winter_tilt = latitude + 15 # degrees
summer_tilt = latitude - 15 # degrees
tilt = solar_position['apparent_zenith'].apply(lambda x: winter_tilt if x <= 90 else summer_tilt)
total_irrad = pvlib.irradiance.get_total_irradiance(tilt, surface_azimuth, 
                                                    solar_position['apparent_zenith'], 
                                                    solar_position['azimuth'], 
                                                    clearsky['dni'], clearsky['ghi'], clearsky['dhi'], 
                                                    dni_extra=pvlib.irradiance.get_extra_radiation(time_range), 
                                                    model='haydavies')

# calculate solar energy potential for the day
energy = total_irrad['poa_global'].sum() # Wh/m^2

# calculate total peak sun hours for the day
threshold = 100 # W/m^2
hours = len(total_irrad[total_irrad['poa_global'] >= threshold]) / 60.0

# calculate current average daily peak sun hours
current_month = datetime.date.today().month
days_so_far = datetime.date.today().day - 1
average_peak_sun_hours = hours / days_so_far

# suggest optimal tilt angle and orientation to user
if latitude > 0:
    orientation = 'south'
    winter_tilt_angle = round(winter_tilt, 2)
    summer_tilt_angle = round(summer_tilt, 2)
else:
    orientation = 'north'
    winter_tilt_angle = round(summer_tilt, 2)
    summer_tilt_angle = round(winter_tilt, 2)
    
print("Solar energy potential for today: {:.2f} kWh/m^2".format(energy / 1000.0))
print("Total peak sun hours for today: {:.2f} hours".format(hours))
print("Average daily peak sun hours so far this month: {:.2f} hours".format(average_peak_sun_hours))
print("Optimal tilt angle for winter: {:.2f} degrees".format(winter_tilt_angle))
print("Optimal tilt angle for summer: {:.2f} degrees".format(summer_tilt_angle))
print("Orientation: {}".format(orientation))
