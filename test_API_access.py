import requests
import os
import sys

# Check if the command-line argument is provided
if len(sys.argv) != 2 or sys.argv[1] not in ["local", "cloud"]:
    print("Usage: python testing_GPT_access.py [local|cloud]")
    sys.exit(1)

# Set the URL based on the command-line argument
if sys.argv[1] == "local":
    url = "http://127.0.0.1:8000/ask_gpt"
elif sys.argv[1] == "cloud":
    url = os.getenv("URL") + "/ask_gpt"

# Define the headers
secret = os.getenv("Test")
headers = {
    "X-API-Key": secret
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