# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 09:00:24 2023

@author: jayaram
"""
import csv
import matplotlib.pyplot as plt

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
        writer.writerow(["", "", "", "", "", f"{total_power_per_day:.2f} kWh", f"{total_power_per_month:.2f} kWh", f"{total_power_per_year:.2f} kWh"])

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
    appliance_name = input("Enter appliance name (or 'q' to quit): ")
    if appliance_name.lower() == 'q':
        break
    quantity = int(input("Enter quantity: "))
    power_rating = int(input("Enter power rating (in watts): "))
    usage_per_day = int(input("Enter usage per day (in hours): "))
    power_requirement = calculate_power_requirement(len(appliances_list)+1, appliance_name, quantity, power_rating, usage_per_day)
    appliances_list.append(power_requirement)

generate_report(appliances_list)

total_power_per_day = total_power_per_month = total_power_per_year = 0
for appliance in appliances_list:
    print(f"{appliance[1]} - Power per day: {appliance[5]}, Power per month: {appliance[6]}, Power per year: {appliance[7]}")
    total_power_per_day += float(appliance[5].split(" ")[0])
    total_power_per_month += float(appliance[6].split(" ")[0])
    total_power_per_year += float(appliance[7].split(" ")[0])

print(f"Total Power per day: {total_power_per_day:.2f} kWh, Power per month: {total_power_per_month:.2f} kWh, Power per year: {total_power_per_year:.2f} kWh")

generate_charts(appliances_list)


