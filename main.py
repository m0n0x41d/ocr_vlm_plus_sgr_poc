from pydantic.types import Base64Bytes
from pydantic_ai import Agent, NativeOutput, BinaryContent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import json
import glob
import sys
import os
from loguru import logger
from dotenv import load_dotenv

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


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    RUB = "RUB"
    NUL = "NUL"


class LineItem(BaseModel):
    description: str = Field(..., description="Description of the item")
    quantity: int = Field(..., description="Quantity of the item")
    unit_price: float = Field(..., description="Price per unit")
    total_price: float = Field(..., description="Total price for this line item")


class ReceiptData(BaseModel):
    merchant_name: str = Field(..., description="Name of the store/merchant")
    currency: Currency = Field(
        ..., description="Currency of the transaction. Set NUL if can't be determined"
    )
    date: str = Field(..., description="Date of purchase")
    time: Optional[str] = Field(None, description="Time of purchase")
    line_items: List[LineItem] = Field(..., description="List of purchased items")
    subtotal: float = Field(..., description="Subtotal before tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    total: float = Field(..., description="Total amount paid")
    payment_method: PaymentMethod = Field(..., description="Payment method used")
    receipt_number: Optional[str] = Field(
        None, description="Receipt or transaction number"
    )


class OcrResponse(BaseModel):
    is_document_receipt: bool = Field(
        ...,
        description="Whether the OCR result is a document receipt. Do not try to parse the result if this is False.",
    )
    receipt_data: ReceiptData | None = Field(
        ...,
        description="Receipt data extracted from the OCR",
    )


agent = Agent(model, output_type=NativeOutput(OcrResponse))


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
