# pip install azure-ai-inference
import os
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", '')
openai_key = os.getenv("AZURE_OPENAI_KEY", '')

if not openai_endpoint:
  raise Exception("Endpoint should be provided")

if not openai_key:
  raise Exception("A key should be provided to invoke the endpoint")

client = ChatCompletionsClient(
    endpoint=openai_endpoint,
    credential=AzureKeyCredential(openai_key)
)

payload = {
  "messages": [
    {
      "role": "user",
      "content": "I am going to Paris, what should I see?"
    },
    {
      "role": "assistant",
      "content": "Paris, the capital of France, is known for its stunning architecture, art museums, historical landmarks, and romantic atmosphere. Here are some of the top attractions to see in Paris:\n\n1. The Eiffel Tower: The iconic Eiffel Tower is one of the most recognizable landmarks in the world and offers breathtaking views of the city.\n2. The Louvre Museum: The Louvre is one of the world's largest and most famous museums, housing an impressive collection of art and artifacts, including the Mona Lisa.\n3. Notre-Dame Cathedral: This beautiful cathedral is one of the most famous landmarks in Paris and is known for its Gothic architecture and stunning stained glass windows.\n\nThese are just a few of the many attractions that Paris has to offer. With so much to see and do, it's no wonder that Paris is one of the most popular tourist destinations in the world."
    },
    {
      "role": "user",
      "content": "What is so great about #1?"
    }
  ],
  "max_tokens": 4096,
  "temperature": 1,
  "top_p": 1,
  "stop": []
}
response = client.complete(payload)

print("Response:", response.choices[0].message.content) # type: ignore
print("Model:", response['model']) # type: ignore
print("Usage:")
print("	Prompt tokens:", response.usage.prompt_tokens) # type: ignore
print("	Total tokens:", response.usage.total_tokens) # type: ignore
print("	Completion tokens:", response.usage.completion_tokens) # type: ignore