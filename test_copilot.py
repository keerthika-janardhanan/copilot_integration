import requests

response = requests.post(
    "http://localhost:3030/api/copilot/chat",
    json={"messages": [{"role": "user", "content": "Write a hello world function in Python"}]}
)

print("Status:", response.status_code)
print("Full Response:", response.json())
