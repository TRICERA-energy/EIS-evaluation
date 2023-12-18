import requests
import json

## Login to get bearer token

login_url = "https://novum-batteries.com/api/batman/v1/login"
username = "xxx"
password = "xxx"

login_body = {
    "username": username,
    "password": password
}

response = requests.post(login_url, json=login_body)

api_url = 'https://novum-batteries.com/api/batman/v1/datasets'
# Check if the request was successful (status code 200)
if response.status_code == 200:
    data = response.json()
    bearer_token = data['jwt']
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}")

## Query module measurements
    
# Give "limit" option, here simply a very high number to get all modules
limit = {"limit": 100000000000000000}
# Convert the JSON object to a string and URL encode it
json_string = json.dumps(limit)
url_encoded_json = requests.utils.quote(json_string)
# Include the "option" parameter in the URL
api_url_with_params = f'{api_url}?option={url_encoded_json}'

# Make a GET request
headers = {
    'Authorization': f'Bearer {bearer_token}',
}
response = requests.get(url=api_url_with_params, headers=headers)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse and use the response data
    data = response.json()
    with open('data_api_raw.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code}")