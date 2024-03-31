from flask import Flask, render_template
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)

def read_distance_matrix(file_path):
    distance_df = pd.read_csv(file_path, index_col=0)
    return distance_df

def read_time_spent(file_path):
    time_df = pd.read_csv(file_path, index_col=0)
    return time_df

def get_next_place(current_place, remaining_places, distance_df):
    min_distance = float('inf')
    next_place = None

    for place in remaining_places:
        distance = distance_df.loc[current_place, place]
        if distance < min_distance:
            min_distance = distance
            next_place = place

    return next_place, min_distance

def calculate_total_time(distance, average_speed):
    time_hours = distance / average_speed
    return time_hours

def generate_itinerary(start_location, start_time, max_hours_per_day, distance_matrix_file, time_spent_file):
    distance_df = read_distance_matrix(distance_matrix_file)
    time_df = read_time_spent(time_spent_file)
    
    remaining_places = list(distance_df.columns)
    remaining_places.remove(start_location)
    
    itinerary = []
    current_location = start_location
    current_time = start_time
    
    while remaining_places:
        next_place, distance = get_next_place(current_location, remaining_places, distance_df)
        time_spent = int(time_df.loc[current_location, 'Time'])
        total_time = calculate_total_time(distance, 50)  # Assuming average speed of 50 km/h
        
        if (current_time + timedelta(hours=total_time+time_spent)) <= current_time.replace(hour=22, minute=0):
            itinerary.append((current_location, time_spent, current_time.strftime('%I:%M %p')))
            current_time += timedelta(hours=time_spent)
            itinerary.append((current_location, next_place, current_time.strftime('%I:%M %p')))
            current_time += timedelta(hours=total_time)
            current_location = next_place
            remaining_places.remove(next_place)
        else:
            
            current_time = current_time.replace(hour=9, minute=0) + timedelta(days=1)
    
    return itinerary

def print_itinerary(itinerary):
    day = 0
    time_format = "%I:%M %p"
    formatted_itinerary = []
    # last_time  = None

    for i, (place_from, place_to, time) in enumerate(itinerary, start=1):
        if time == "09:00 AM":
            day += 1
            formatted_itinerary.append({
                "day": day,
                "time": time,
                "place_from": place_from,
                "time_spent": place_to
            })
            
        else:
            if isinstance(place_to, str):
                formatted_itinerary.append({
                    "day": day,
                    "time": datetime.strptime(time, time_format).strftime('%I:%M %p'),
                    "place_from": place_from,
                    "place_to": place_to
                    
                })
            else:
                formatted_itinerary.append({
                    "day": day,
                    "time": datetime.strptime(time, time_format).strftime('%I:%M %p'),
                    "place_from": place_from,
                    "time_spent": place_to
                })

    return formatted_itinerary

@app.route('/')
def index():
    start_location = "Varkala"  
    start_time = datetime.strptime("09:00 AM", "%I:%M %p")  
    max_hours_per_day = 10 

    distance_matrix_file = "distance_matrix.csv"
    time_spent_file = "time_spent.csv"

    itinerary = generate_itinerary(start_location, start_time, max_hours_per_day, distance_matrix_file, time_spent_file)
    formatted_itinerary = print_itinerary(itinerary)

    return render_template('itinerary.html', itinerary=formatted_itinerary)

if __name__ == '__main__':
    app.run(debug=True)
