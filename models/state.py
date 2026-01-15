from typing import TypedDict, Annotated, List
from pydantic import BaseModel
from langgraph.graph import add_messages

class RequestedItem(BaseModel):
    name: str
    category: str
    quantity: int

class PurchaseState(TypedDict):
    messages: Annotated[list, add_messages]
    user_input: str
    parsed_items: List[RequestedItem]
    current_agent: str
    conversation_complete: bool