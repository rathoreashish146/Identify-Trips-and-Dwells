import pandas as pd
from geopy.distance import geodesic
from datetime import datetime, timedelta

# Load the dataset
gps_data = pd.read_csv('gps_data.csv', parse_dates=['Timestamp'])

# Preprocess data
gps_data.sort_values(by=['DeviceID', 'Timestamp'], inplace=True)

# Parameters
DISTANCE_THRESHOLD = 100  # meters
TIME_THRESHOLD = 300  # seconds (5 minutes)

# Function to identify trips and dwells
def identify_trips_dwells(gps_data):
    trips = []
    dwells = []
    
    for device_id, device_data in gps_data.groupby('DeviceID'):
        device_data = device_data.sort_values('Timestamp').reset_index(drop=True)
        
        start_dwell = None
        start_trip = None
        
        for i in range(1, len(device_data)):
            point1 = (device_data.loc[i-1, 'Latitude'], device_data.loc[i-1, 'Longitude'])
            point2 = (device_data.loc[i, 'Latitude'], device_data.loc[i, 'Longitude'])
            
            distance = geodesic(point1, point2).meters
            time_diff = (device_data.loc[i, 'Timestamp'] - device_data.loc[i-1, 'Timestamp']).total_seconds()
            
            if distance < DISTANCE_THRESHOLD:
                if time_diff > TIME_THRESHOLD:
                    if not start_dwell:
                        start_dwell = device_data.loc[i-1, 'Timestamp']
                    end_dwell = device_data.loc[i, 'Timestamp']
                if start_trip:
                    trips.append({
                        'DeviceID': device_id,
                        'Start': start_trip,
                        'End': device_data.loc[i-1, 'Timestamp']
                    })
                    start_trip = None
            else:
                if start_dwell:
                    dwells.append({
                        'DeviceID': device_id,
                        'Start': start_dwell,
                        'End': end_dwell
                    })
                    start_dwell = None
                if not start_trip:
                    start_trip = device_data.loc[i-1, 'Timestamp']
        
        if start_trip:
            trips.append({
                'DeviceID': device_id,
                'Start': start_trip,
                'End': device_data.loc[i-1, 'Timestamp']
            })
        if start_dwell:
            dwells.append({
                'DeviceID': device_id,
                'Start': start_dwell,
                'End': end_dwell
            })
    
    return pd.DataFrame(trips), pd.DataFrame(dwells)

# Run the function
trips_df, dwells_df = identify_trips_dwells(gps_data)

# Save the results
trips_df.to_csv('trips.csv', index=False)
dwells_df.to_csv('dwells.csv', index=False)

# Display the first few rows of the results
print("Trips:")
print(trips_df.head())
print("\nDwells:")
print(dwells_df.head())
