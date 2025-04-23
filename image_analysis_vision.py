import os
from dotenv import load_dotenv
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

# Load environment variables from .env file
load_dotenv()

vision_endpoint = os.getenv("VISION_ENDPOINT", "")
vision_key = os.getenv("VISION_KEY", "")

artifact_path = os.path.join(os.getcwd(), "artifacts", "input")

if not vision_endpoint:
  raise Exception("Endpoint should be provided")

if not vision_key:
  raise Exception("A key should be provided to invoke the endpoint")

client = ImageAnalysisClient(
    endpoint=vision_endpoint,
    credential=AzureKeyCredential(vision_key)
)

with open(os.path.join(artifact_path, "tiff", "2.tiff"), "rb") as f:
    image_data = f.read()

result = client._analyze_from_image_data(
    image_data=image_data,
    visual_features=[VisualFeatures.CAPTION, VisualFeatures.READ],
    gender_neutral_caption=True,
)

print("Image analysis results:")
# Print caption results to the console
print(" Caption:")
if result.caption is not None:
    print(f"   '{result.caption.text}', Confidence {result.caption.confidence:.4f}")

# Print text (OCR) analysis results to the console
print(" Read:")

content = ""

if result.read is not None:
    for line in result.read.blocks[0].lines:
        # print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
        for word in line.words:
            content += word.text + " "
            # print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")

print(f"Contenet: {content}")