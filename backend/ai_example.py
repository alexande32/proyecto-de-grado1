import os
import sys

import anthropic

api_key = os.getenv("AI_GATEWAY_API_KEY")
if not api_key:
    sys.exit("Falta la variable de entorno AI_GATEWAY_API_KEY")

client = anthropic.Anthropic(
    base_url="https://gateway.ngrok.ai",
    api_key=api_key,
)

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)

print(message.content[0].text)