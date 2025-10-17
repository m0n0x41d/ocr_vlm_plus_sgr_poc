from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional


class OcrQualityEnum(str, Enum):
    GOOD = "good"
    MEDIUM = "medium"
    BAD = "bad"
    NUL = "nul"


class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"


class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    RUB = "RUB"
    NUL = "NUL"


class DocumentType(str, Enum):
    RECEIPT = "receipt"
    INVOICE = "invoice"
    NOT_PAYMENT_DOCUMENT = "not_payment_document"


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


class InvoiceData(BaseModel):
    invoice_number: str = Field(..., description="Invoice number or ID")
    invoice_date: str = Field(..., description="Invoice date")
    due_date: Optional[str] = Field(None, description="Payment due date")
    currency: Currency = Field(
        ..., description="Currency of the invoice. Set NUL if can't be determined"
    )

    seller_name: str = Field(
        ..., description="Name of the seller/company issuing invoice"
    )
    seller_address: Optional[str] = Field(None, description="Seller's address")
    seller_phone: Optional[str] = Field(None, description="Seller's phone number")
    seller_email: Optional[str] = Field(None, description="Seller's email")
    seller_tax_id: Optional[str] = Field(
        None, description="Seller's tax ID or VAT number"
    )

    buyer_name: str = Field(..., description="Name of the buyer/customer")
    buyer_address: Optional[str] = Field(None, description="Buyer's billing address")
    buyer_phone: Optional[str] = Field(None, description="Buyer's phone number")
    buyer_email: Optional[str] = Field(None, description="Buyer's email")
    buyer_tax_id: Optional[str] = Field(
        None, description="Buyer's tax ID or VAT number"
    )

    line_items: List[LineItem] = Field(
        ..., description="List of products/services billed"
    )
    subtotal: float = Field(..., description="Subtotal before tax and discounts")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    discount_amount: Optional[float] = Field(None, description="Total discount amount")
    total_amount: float = Field(..., description="Total amount due")

    payment_method: PaymentMethod = Field(..., description="Payment method")
    payment_terms: Optional[str] = Field(
        None, description="Payment terms (e.g., 'NET 30', 'Due on receipt')"
    )
    bank_details: Optional[str] = Field(
        None, description="Bank transfer details if applicable"
    )

    notes: Optional[str] = Field(None, description="Additional notes or terms")
    purchase_order_number: Optional[str] = Field(
        None, description="Related purchase order number"
    )


class OcrResponse(BaseModel):
    document_type: DocumentType = Field(
        ...,
        description="Pick on of the document type enum types. If cant be determined, set to NUL and not try to OCR the document.",
    )
    receipt_data: ReceiptData | None = Field(
        ...,
        description="Receipt data extracted from the OCR",
    )
    invoice_data: InvoiceData | None = Field(
        ...,
        description="Invoice data extracted from the OCR",
    )
    ocr_quality_confidence: OcrQualityEnum = Field(
        ...,
        description="How confidend you are in OCR quality confidence. Set NUL if there was no OCR done.",
    )
    reasoning_commentary: Optional[str] = Field(
        None,
        description="Reasoning commentary if there is anything to expain about low OCR quality confidence.",
    )
