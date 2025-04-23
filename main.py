import datetime
import json
import os
import asyncio
import asyncpg
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import List, Dict, Any

async def fetch_article_ids(
    conn: asyncpg.Connection,
    start_date: datetime.date,
    end_date: datetime.date,
    sections: List[str],
    topics: List[str],
    keywords: List[str],
) -> List[str]:
    """Fetch article IDs based on filtering criteria."""
    section_patterns = [f"%{section}%" for section in sections]
    topic_patterns = [f"%{topic}%" for topic in topics]
    keyword_patterns = [f"%{keyword}%" for keyword in keywords]

    results = await conn.fetch(
        """
        SELECT id FROM news
        WHERE publication_date BETWEEN $1 AND $2
            AND selection ILIKE ANY($3)
            AND "topic " ILIKE ANY($4)
            OR (
                headline ILIKE ANY($5) OR
                "content " ILIKE ANY($6)
            )
    """,
        start_date,
        end_date,
        section_patterns,
        topic_patterns,
        keyword_patterns,
        keyword_patterns,
    )

    return [record["id"] for record in results]


async def process_image(
    article_id: str,
    tiff_path: str,
    vision_client: ImageAnalysisClient,
    openai_client: AzureOpenAI,
    model: str,
) -> Dict[str, Any]:
    """Process a single image through Vision API and GPT."""
    # Read the TIFF image
    try:
        with open(tiff_path, "rb") as tiff_image:
            tiff_image_data = tiff_image.read()
    except FileNotFoundError:
        print(f"TIFF file not found: {tiff_path}")
        return {"article_id": article_id, "error": "File not found"}

    # Analyze with Vision API
    vision_response = vision_client._analyze_from_image_data(
        image_data=tiff_image_data,
        visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
        gender_neutral_caption=True,
    )

    # Extract caption
    caption = None
    if vision_response.caption is not None:
        caption = {
            "text": vision_response.caption.text,
            "confidence": vision_response.caption.confidence,
        }

    # Extract content from VISION response
    content = ""
    if vision_response.read is not None and vision_response.read.blocks:
        for line in vision_response.read.blocks[0].lines:
            for word in line.words:
                content += word.text + " "

    # Process with OpenAI
    openai_response = openai_client.chat.completions.create(
        max_tokens=4096,
        temperature=1.0,
        top_p=1.0,
        stream=False,
        model=model,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant for identifying and correcting any spelling mistakes while preserving the original formatting and structure of the text",
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": content},
                ],
            },
        ],
    )

    # Extract results
    corrected_text = openai_response.choices[0].message.content
    usage = openai_response.usage

    return {
        "article_id": article_id,
        "caption": caption,
        "raw_text": content,
        "corrected_text": corrected_text,
        "token_usage": {
            "prompt_tokens": usage.prompt_tokens,  # type: ignore
            "completion_tokens": usage.completion_tokens,  # type: ignore
            "total_tokens": usage.total_tokens,  # type: ignore
        },
    }


async def main() -> None:
    """Main execution function."""
    try:
        # Load environment variables
        load_dotenv()

        # Set up paths
        artifact_path = os.path.join(os.getcwd(), "artifacts", "input")
        config_path = os.path.join(artifact_path, "config.json")

        # Validate required environment variables
        required_env_vars = {
            "DATABASE_URL": os.getenv("DATABASE_URL", ""),
            "OPENAI_ENDPOINT": os.getenv("OPENAI_ENDPOINT", ""),
            "OPENAI_KEY": os.getenv("OPENAI_KEY", ""),
            "VISION_ENDPOINT": os.getenv("VISION_ENDPOINT", ""),
            "VISION_KEY": os.getenv("VISION_KEY", ""),
        }

        # Check for missing environment variables
        missing_vars = [var for var, value in required_env_vars.items() if not value]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        # Load configuration
        try:
            with open(config_path, "r") as config_file:
                config = json.load(config_file)

            date_range = config["date_range"]
            sections = config["sections"]
            topics = config["topics"]
            keywords = config["keywords"]

            # Convert string dates to datetime objects
            start_date = datetime.datetime.strptime(
                date_range["start_date"], "%Y-%m-%d"
            ).date()
            end_date = datetime.datetime.strptime(
                date_range["end_date"], "%Y-%m-%d"
            ).date()
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Error loading configuration: {e}")

        # Initialize clients
        vision_client = ImageAnalysisClient(
            endpoint=required_env_vars["VISION_ENDPOINT"],
            credential=AzureKeyCredential(required_env_vars["VISION_KEY"]),
        )

        openai_client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=required_env_vars["OPENAI_ENDPOINT"],
            api_key=required_env_vars["OPENAI_KEY"],
            max_retries=2,
            timeout=60,
        )

        # Fetch article IDs from database
        async with asyncpg.create_pool(required_env_vars["DATABASE_URL"]) as pool:
            async with pool.acquire() as conn:
                article_ids = await fetch_article_ids(
                    conn, start_date, end_date, sections, topics, keywords
                )

        if not article_ids:
            print("No articles found matching the criteria")
            return

        print(f"Found {len(article_ids)} matching articles")

        # Process each article concurrently
        tasks = []
        for article_id in article_ids:
            tiff_path = os.path.join(artifact_path, "tiff", f"{article_id}.tiff")
            task = process_image(
                article_id, tiff_path, vision_client, openai_client, "gpt-4o"
            )
            tasks.append(task)

        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if isinstance(result, Exception):
                print(f"Error processing article: {result}")
            else:
                article_id = result["article_id"]  # type: ignore
                if "error" in result:  # type: ignore
                    print(f"Failed to process article {article_id}: {result['error']}")  # type: ignore
                    continue

                print(f"\nArticle ID: {article_id}")
                if result["caption"]:  # type: ignore
                    print(
                        f"Caption: '{result['caption']['text']}', "  # type: ignore
                        f"Raw Content: '{result['raw_text']}', "  # type: ignore
                        f"Confidence: {result['caption']['confidence']:.4f}"  # type: ignore
                    )  # type: ignore
                print(f"Corrected Text: {result['corrected_text'][:100]}...")  # type: ignore
                print("Token Usage: ", result["token_usage"])  # type: ignore

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
