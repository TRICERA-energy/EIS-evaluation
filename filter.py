import json
import re

## Read the JSON file
with open('data_api_raw.json') as json_file:
    data = json.load(json_file)

## Filter raw api data for modules that are from LG and whose name start with 4 digits
name_pattern = r'\b\d{4}\b.*'
manufacturer = 'LG Electronics'

filtered_data = [
    {
        'name': battery['meta']['battery']['name'],
        'measurements': 
        [
            {
                'frequency': measurement['frequency'],
                'amplitude': measurement['amplitude'],
                'phase_shift': measurement['phase_shift']
            } for measurement in battery['measured']['measurement_cycles']
        ]
    }
    for battery in data if ('battery' in battery['meta'] and (battery['meta']['battery']['battery_type']['manufacturer'] == manufacturer) 
                                    and re.match(name_pattern, (battery['meta']['battery']['name'])))
]

## Only keep the last measurement of each module
last_measurements = []
is_there = False

# Iterate through the list of dictionaries in reverse order
for d in reversed(filtered_data):
    is_there = False
    # Check if the name is among the selected modules
    for module in last_measurements:
        if module['name'][:4] == d["name"][:4]:
            is_there = True
    # If the name is not already in the last_entries list, add it
    if not is_there:   
        last_measurements.append(d)

## Create a new dictionary with the filtered data
result = {'filtered_data': last_measurements}

# Convert the result to JSON
with open('data_api_filtered.json', 'w') as json_file:
    json.dump(result, json_file, indent=4)