import os
from dotenv import load_dotenv
from openai import AzureOpenAI # type: ignore

# Load environment variables from .env file
load_dotenv()

openai_endpoint = os.getenv("OPENAI_ENDPOINT", "")
openai_key = os.getenv("OPENAI_KEY", "")

if not openai_endpoint:
  raise Exception("Endpoint should be provided")

if not openai_key:
  raise Exception("A key should be provided to invoke the endpoint")

client = AzureOpenAI(
  api_version="2024-12-01-preview",
  azure_endpoint=openai_endpoint,
  api_key=openai_key,
  max_retries=2,
  timeout=60
)

response = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant.",
        },
        {
            "role": "user",
            "content": "I am going to Paris, what should I see?",
        }
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model="gpt-4o"
)

print(response.choices[0].message.content)