import requests

# Get local 
#url = "http://127.0.0.1:8000/check-key"
url = "https://webapp-e475evrkjp63o.azurewebsites.net/check-key"

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

# Check the response status code
if response.status_code == 200:
    try:
        # Print the JSON response
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Error decoding JSON response")
        print(response.text)
else:
    print(f"Error: Received status code {response.status_code}")
    print(response.text)