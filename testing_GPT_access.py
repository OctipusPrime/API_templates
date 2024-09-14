import requests

# Define the API endpoint
url = "http://127.0.0.1:8000/check-key"

# Define the headers
headers = {
    "X-API-Key": "My_god_why_is_this_so_hard"
}

# Define the payload
params = {
    "prompt": "Hello, how are you?",
    "key_name": "Test"
}

# Make the GET request
response = requests.get(url, headers=headers, params=params)

# Print the response
print(response.json())