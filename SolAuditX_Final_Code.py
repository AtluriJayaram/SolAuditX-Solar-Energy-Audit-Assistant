# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 22:52:10 2023

@author: jayaram
"""
#%% Calculating the solar energy potential based on the input location and climate data

import datetime
import pandas as pd
import numpy as np
import pvlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import csv
import math
from geopy.geocoders import Nominatim

print("Hello!\nWelcome to SolAuditX [Solar/Energy Audit Tool]\nLets Calculate the solar energy potential of your area. ")

# input parameters
zip_code = int(input("Please enter your area ZipCode :"))  # replace with the zip code you want

geolocator = Nominatim(user_agent="my_custom_application")
location = geolocator.geocode(zip_code)
latitude = location.latitude
longitude = location.longitude
print("Latitude:", latitude)
print("Longitude:", longitude)
elevation = 10 # meters
timezone = 'US/Mountain'


# create time range
start = pd.Timestamp(datetime.date.today(), tz=timezone)
end = start + pd.Timedelta(days=1)
time_range = pd.date_range(start=start, end=end, inclusive='left', freq='1min')

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
threshold = 600 # W/m^2
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
    
print("\nENERGY POTENTIAL DETAILS:")
print("Solar energy potential for today: {:.2f} kWh/m^2".format(energy / 1000.0))
print("Total peak sun hours today: {:.2f} hours".format(hours))
print("Average daily peak sun hours so far this month: {:.2f} hours".format(average_peak_sun_hours))
print("\nSOLAR PANEL DETAILS:")
print("Optimal tilt angle for winter: {:.2f} degrees".format(winter_tilt_angle))
print("Optimal tilt angle for summer: {:.2f} degrees".format(summer_tilt_angle))
print("Orientation: {}".format(orientation))



# plot solar energy potential for every hour of the present day
fig, ax = plt.subplots()
ax.plot(time_range, total_irrad['poa_global'])
ax.set_xlabel('Time')
ax.set_ylabel('Solar Energy Potential (W/m^2)')
ax.set_title('Solar Energy Potential for Present Day')

# set x-axis ticks
ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))  # major ticks every 4 hours
ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))  # minor ticks every 1 hour

# format x-axis tick labels
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # format major tick labels to show only hours and minutes

plt.show()

#%% Energy audit based on user input of household appliances and usage hours



print("\n\nNow Lets perform Energy audit \nBased on your daily energy requirements[household appliances and usage hours]\nPlease kindly provide with the necessary details")


def calculate_power_requirement(serial_no, appliance_name, quantity, power_rating, usage_per_day):
    """Calculates power requirement per day, month, and year based on user inputs"""
    power_per_day = quantity * power_rating * usage_per_day / 1000
    power_per_month = power_per_day * 30
    power_per_year = power_per_day * 365
    return [serial_no, appliance_name, f"{quantity} units", f"{power_rating} W", f"{usage_per_day} hours", f"{power_per_day:.2f} kWh", f"{power_per_month:.2f} kWh", f"{power_per_year:.2f} kWh"]


def generate_report(appliances_list):
    """Generates a report in CSV format"""
    with open('Energy audit Report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Serial No.", "Appliance Name", "Quantity", "Power Rating (W)", "Usage per day (hours)", "Power per day (kWh)", "Power per month (kWh)", "Power per year (kWh)"])
        total_power_per_day = total_power_per_month = total_power_per_year = 0
        for i, appliance in enumerate(appliances_list, start=1):
            writer.writerow(appliance)
            total_power_per_day += float(appliance[5].split(" ")[0])
            total_power_per_month += float(appliance[6].split(" ")[0])
            total_power_per_year += float(appliance[7].split(" ")[0])
        writer.writerow(["#", "TOTAL:", "", "", "", f"{total_power_per_day:.2f} kWh", f"{total_power_per_month:.2f} kWh", f"{total_power_per_year:.2f} kWh"])
       
        
        # write solar energy potential details
        energy_potential_details = ["ENERGY POTENTIAL DETAILS:", 
                                    "Solar energy potential for today: {:.2f} kWh/m^2".format(energy / 1000.0), 
                                    "Total peak sun hours for today: {:.2f} hours".format(hours), 
                                    "Average daily peak sun hours so far this month: {:.2f} hours".format(average_peak_sun_hours), 
                                    "SOLAR PANEL DETAILS:", 
                                    "Optimal tilt angle for winter: {:.2f} degrees".format(winter_tilt_angle), 
                                    "Optimal tilt angle for summer: {:.2f} degrees".format(summer_tilt_angle), 
                                    "Orientation: {}".format(orientation)]
        for detail in energy_potential_details:
            writer.writerow([detail])
        writer.writerow([""])
        
        # write number of solar panels required and minimum battery capacity needed
        writer.writerow(["Number of solar panels required: ", num_panels])
        writer.writerow(["Minimum battery capacity needed to store the energy needed: ", min_battery_capacity, "Ah"])


def generate_charts(appliances_list):
    """Generates a pie chart and bar chart of power usage of various appliances in a day"""
    appliance_names = [appliance[1] for appliance in appliances_list]
    power_usage = [float(appliance[5].split(" ")[0]) for appliance in appliances_list]
    
    # Generate pie chart
    fig1, ax1 = plt.subplots()
    ax1.pie(power_usage, labels=appliance_names, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')
    plt.title("Power Usage per Appliance (in kWh)")

    # Generate bar chart
    fig2, ax2 = plt.subplots()
    ax2.bar(appliance_names, power_usage)
    plt.title("Power Usage per Appliance (in kWh)")
    plt.xlabel("Appliance Name")
    plt.ylabel("Power Usage (kWh)")
    plt.xticks(rotation=45)

    plt.show()

appliances_list = []
while True:
    appliance_name = input("Enter appliance name (or 'x' to quit): ")
    if appliance_name.lower() == 'x':
        break
    quantity = float(input("Enter quantity: "))
    power_rating = float(input("Enter power rating (in watts): "))
    usage_per_day = float(input("Enter estimated usage per day (in hours): "))
    power_requirement = calculate_power_requirement(len(appliances_list)+1, appliance_name, quantity, power_rating, usage_per_day)
    appliances_list.append(power_requirement)


total_power_per_day = total_power_per_month = total_power_per_year = 0
for appliance in appliances_list:
    print(f"{appliance[1]} - Power per day: {appliance[5]}, Power per month: {appliance[6]}, Power per year: {appliance[7]}")
    total_power_per_day += float(appliance[5].split(" ")[0])
    total_power_per_month += float(appliance[6].split(" ")[0])
    total_power_per_year += float(appliance[7].split(" ")[0])

print(f"\nTotal Power per day: {total_power_per_day:.2f} kWh, Power per month: {total_power_per_month:.2f} kWh, Power per year: {total_power_per_year:.2f} kWh")

generate_charts(appliances_list)


# calculate the number of solar panels required
def calculate_solar_panels(total_energy, panel_capacity):
    return int(math.ceil(total_energy*1000 / (panel_capacity * hours)))

# suggest the minimum battery capacity needed to store 50% of the energy needed
def suggest_battery_capacity(total_energy):
    Non_Sun_hours_Ratio =((1-(hours/24))/2)
    return int(math.ceil(total_energy*1000 * Non_Sun_hours_Ratio))

# Realistic total energy needed ,with concidering 25% energy losses
total_energy = total_power_per_day * 1.25

# calculate the number of solar panels required
panel_capacity = 300 # In watts,most commenly used, Can change the depending on panel used
num_panels = calculate_solar_panels(total_energy, panel_capacity)

# suggest the minimum battery capacity needed to store 50% of the energy needed
min_battery_capacity = suggest_battery_capacity(total_energy)

print(f"\nNumber of solar panels required: {num_panels}")
print(f"Minimum Battery capacity needed to store the energy needed: {min_battery_capacity} Ah")


generate_report(appliances_list)