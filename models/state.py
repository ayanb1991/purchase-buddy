from typing import TypedDict, Annotated, List
from pydantic import BaseModel
from langgraph.graph import add_messages

class RequestedItem(BaseModel):
    name: str
    category: str
    quantity: int
    unit: int
    priceExpectation: int | None
    isQuickDelivery: bool

class PurchaseState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str
    parsed_items: List[RequestedItem]
    user_pincode: str
    delivery_time_preference: str
    next_agent: str
    selected_provider: str
    provider_results: List[dict]

class InventoryItem(BaseModel):
    name: str
    category: str
    type: str
    unit: str
    price: float
    provider: str
    isQuickDelivery: bool
    isAvailable: bool
    pincodes: List[str]
    deliveryHours: str
    availabilityStatus: str | None = None