import streamlit as st
import mysql.connector
import json
import pandas as pd
import matplotlib.pyplot as plt

# Create a connection to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="admin",
    port=3307,
    database="Carbon_Footprint_Calculator",
    auth_plugin="caching_sha2_password"
)

# Function to calculate carbon footprint based on user inputs
def calculate_carbon_footprint(distance, vehicle_type, electricity_usage, daily_activities):
    # Calculate carbon footprint based on a simple formula
    if vehicle_type == "Car":
        car_carbon_footprint = distance * 0.2 + electricity_usage * 0.1
    elif vehicle_type == "Motorcycle":
        car_carbon_footprint = distance * 0.1 + electricity_usage * 0.05
    else:
        car_carbon_footprint = distance * 0.15 + electricity_usage * 0.08

    # Calculate the carbon footprint from daily activities
    daily_activities_carbon_footprint = 0
    for activity, duration in daily_activities.items():
        carbon_footprint_per_hour = {
            'watching_tv': 0.1,
            'using_laptop': 0.06,
            'using_smartphone': 0.02,
            'using_light_bulb': 0.01
        }
        if activity in carbon_footprint_per_hour:
            carbon_footprint = carbon_footprint_per_hour[activity] * duration
            daily_activities_carbon_footprint += carbon_footprint

    total_carbon_footprint = car_carbon_footprint + daily_activities_carbon_footprint

    # Insert the carbon footprint data into the database
    cursor = mydb.cursor()
    query = "INSERT INTO carbon_footprint (distance, vehicle_type, electricity_usage, daily_activities, car_carbon_footprint, daily_activities_carbon_footprint, total_carbon_footprint) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (distance, vehicle_type, electricity_usage, json.dumps(daily_activities), car_carbon_footprint, daily_activities_carbon_footprint, total_carbon_footprint)
    cursor.execute(query, values)
    mydb.commit()
    cursor.close()

    return total_carbon_footprint


# Streamlit app
st.title("Carbon Footprint Calculator")
st.subheader("Daily Activity Related Carbon Footprint")
st.write("Please enter your daily energy-consuming activities and their durations.")
activities = [
    'watching_tv',
    'using_laptop',
    'using_smartphone',
    'using_light_bulb'
]

total_carbon_footprint = 0

daily_activities = {}
for activity in activities:
    duration = st.number_input(f"{activity} (hours per day):", min_value=0.0, value=0.0, step=0.1)
    daily_activities[activity] = duration

# Input fields for vehicle-related carbon footprint
st.subheader("Vehicle-Related Carbon Footprint")
distance = st.number_input("Distance (in km):", value=0.0, step=0.1)
vehicle_type = st.selectbox("Vehicle Type:", ["Car", "Motorcycle", "Bus", "Train"])
electricity_usage = st.number_input("Electricity Usage (in kWh):", value=0.0, step=0.1)

if st.button("Calculate Total Carbon Footprint"):
    carbon_footprint = calculate_carbon_footprint(distance, vehicle_type, electricity_usage, daily_activities)
    st.write(f"Your estimated total carbon footprint is {carbon_footprint:.2f} kg CO2e per day.")

# Display the recent data from the database
st.subheader("Recent Carbon Footprint Data")
cursor = mydb.cursor()
cursor.execute("SELECT * FROM carbon_footprint")
data = cursor.fetchall()
data_df = pd.DataFrame(data, columns=["ID", "Distance (km)", "Vehicle Type", "Electricity Usage (kWh)", "Daily Activities", "Carbon Footprint for Transportation(kg CO2)", "Daily Activities Carbon Footprint (kg CO2)", "Total Carbon Footprint (kg CO2)"])
st.dataframe(data_df)

# Plot a bar chart of the recent data
plt.figure(figsize=(8, 4))
plt.bar(data_df["ID"], data_df["Total Carbon Footprint (kg CO2)"])
plt.xlabel("ID")
plt.ylabel("Total Carbon Footprint (kg CO2)")
plt.title("Total Carbon Footprint Over Time")
st.pyplot(plt)

# Close the database connection
mydb.close()