import os
import base64
import requests # type: ignore
import asyncio
import asyncpg
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import json

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
connection_string = os.getenv('DATABASE_URL')

# Azure OpenAI and Vision credentials
openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
openai_key = os.getenv('AZURE_OPENAI_KEY')
artifact_path = "./artifacts/input"

async def main():
    # Load filtering criteria from config file
    with open(f'${artifact_path}/config.json', 'r') as config_file:
        config = json.load(config_file)

    date_range = config['date_range']
    sections = config['sections']
    topics = config['topics']
    keywords = config['keywords']

    try:
        # Connect to the PostgreSQL database
        pool = await asyncpg.create_pool(connection_string)

        async with pool.acquire() as conn:
            # Construct the SQL query with filtering criteria
            article_ids = await conn.fetch("""
                    SELECT id FROM news
                        WHERE publication_date BETWEEN %s AND %s
                        AND selection = ANY(%s)
                        AND topic = ANY(%s)
                        AND (
                            headling ILIKE ANY(%s) OR
                            content ILIke ANY(%s)
                        )
                """,
                date_range['start_date'],
                date_range['end_date'],
                sections,
                topics,
                [f"%{keywords}%" for keywords in keywords],
                [f"%{keywords}%" for keywords in keywords]
            )

            conn.close()

        # Iterate through the article ID array
        for article_id in article_ids:
            article_id = article_id[0]
        
            # Pull histrical archives from artifacts/input
            with Image.open(f"${artifact_path}/${article_id}.002") as image:
                image.save(f"${artifact_path}/${article_id}.png", format="PNG")

            # Open the PNG file from artifacts/input
            with Image.open(f"${artifact_path}/${article_id}.png") as pngImage:
                # Create a ByteIo object to hold the image data
                buffered = BytesIO()
                # Save the image to the ByteIO object in PNG format
                pngImage.save(buffered, format="PNG")
                # Get the byte data from the BytesIO object
                pngImage_byte = buffered.getvalue()
                # Encode the byte data to base64
                pngImage_base64 = base64.b64encode(pngImage_byte).decode('uft-8')

            # Generate default prompt for GPT-4o
            prompt = f"""
            Extract text form article ID {article_id}:
            {pngImage_base64}
            """

            # Process the OCR result using Azure OpenAI
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {openai_key}'
            }
            data = {
                'prompt': prompt,
                'max_tokens': 100
            }

            response = requests.post(f"{openai_endpoint}/v1/engines/davinci-codex/completions", headers=headers, json=data)
            response.raise_for_status()
            openai_result = response.json()

            # Isolate message from default completion choice
            message = openai_result['choices'][0]['text']
            print(f"Article ID {article_id} - Extracted Text: {message}")

    except Exception as e:
        print(f"An error occured: {e}")

asyncio.run(main())