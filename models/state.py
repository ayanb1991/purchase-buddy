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
    current_agent: str