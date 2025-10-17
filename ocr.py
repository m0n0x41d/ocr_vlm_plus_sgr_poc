from pydantic_ai import Agent, NativeOutput, BinaryContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
import json
import glob
import sys
import os
from loguru import logger
from dotenv import load_dotenv
from sgr_models import OcrResponse

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "no_model")
API_KEY = os.getenv("API_KEY")
OPEN_AI_API_COMPATABLE_BASE_URL = os.getenv("OPEN_AI_API_COMPATABLE_BASE_URL")


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
)


model = OpenAIChatModel(
    MODEL_NAME,
    provider=OpenAIProvider(
        base_url=OPEN_AI_API_COMPATABLE_BASE_URL,
        api_key=API_KEY,
    ),
)


SYSTEM_PROMPT = """
You are a specialized document recognition system focused on payment-related documents.
Your task is to analyze images and determine if they contain valid payment documents.

## DOCUMENT CLASSIFICATION:
First, classify the image into one of these categories:
1. INVOICE - A formal bill requesting payment for goods/services, typically includes: company details, invoice number, itemized charges, totals, payment terms
2. RECEIPT - Proof of completed payment, typically includes: vendor name, items purchased, prices, payment method, date/time, transaction number
3. NOT_PAYMENT_DOCUMENT - Any other type of document or image

## IMPORTANT GUIDELINES:
- Only process clear payment-related documents
- Reject blurry, partial, or ambiguous images
- Do not attempt OCR on non-payment documents
- Prioritize accuracy over completeness
- If uncertain about classification, default to NOT_PAYMENT_DOCUMENT
"""

agent = Agent(
    model,
    output_type=NativeOutput(OcrResponse),
    system_prompt=SYSTEM_PROMPT,
)


if __name__ == "__main__":
    jpg_files = glob.glob("files_to_ocr/*.jpg")

    if not jpg_files:
        logger.error("No JPG files found in files_to_ocr directory")
        SystemExit(1)

    logger.success(f"Got {len(jpg_files)} JPG files to process")
    logger.info("=" * 60)

    for i, jpg_file in enumerate(jpg_files, 1):
        logger.info(f"[{i}/{len(jpg_files)}] Processing: {jpg_file}")
        logger.info("-" * 40)

        try:
            with open(jpg_file, "rb") as f:
                image_data = BinaryContent(f.read(), media_type="image/jpeg")
                logger.info("Sending image to LLM...")

                result = agent.run_sync([image_data])

                receipt_data = result.output.model_dump()
                logger.success("OCR processing completed successfully!")
                logger.info("Extracted receipt data:")

                formatted_json = json.dumps(receipt_data, indent=2, ensure_ascii=False)
                logger.info(f"\n{formatted_json}")

        except Exception as e:
            logger.error(f"Error processing {jpg_file}: {str(e)}")
            continue

    logger.info("\n" + "=" * 60)
    logger.success("All receipts processed")
