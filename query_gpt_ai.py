import openai 

openai.api_key = "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"

with open('test.txt') as f:
    user_message = f.read()

response = openai.ChatCompletion.create(
  model="gpt-4",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": user_message},
  ]
)

print(response["choices"][0]["message"]["content"])