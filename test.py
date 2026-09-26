import requests

prompt = {
  "prompt": "Hello there, my name is joseph you? how's your day and can you tell me a little about yourself?",
  "context": "You are the ai for a chatbot called rave's Connect",
  "history": "",
  "system_command": "You are a helpful assistant named connect AI."
}


ai = "http://192.168.1.140:5000/api/v1/ai"

health = requests.get("http://192.168.1.140:5000/health")

# 1. Check if the request was successful (HTTP Status 200)
if health.status_code == 200:
    print('Typing...')
    response = requests.post(ai, json=prompt)
    # 2. Parse the response as JSON data (dict)
    if response.status_code == 200:
        data = response.json()
        print("AI: ", data["response"])  # Access data like a normal Python dictionary

else:
    print(f"Failed to fetch data. Status code: {health.status_code}")