import requests

endpoint = "http://localhost"
response = requests.get(endpoint)
print(response.text)
