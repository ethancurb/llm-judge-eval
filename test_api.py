from api_client import ChatGPT

model = ChatGPT(model="gpt-4.1-mini")

resp = model.generate([
    {"role": "user", "content": "Say 'hello world'."}
])

print("Response =", resp)
