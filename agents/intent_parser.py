import re
from models.state import PurchaseState, RequestedItem

category_keywords = {
    "grocery": ["milk", "bread", "eggs", "rice", "flour", "sugar", "salt"],
    "electronics": ["headphones", "mouse", "keyboard", "charger", "laptop", "phone"],
    "cooked food": ["biryani", "pizza", "pasta", "burger", "sandwich"]
}

""" A simple function to extract quantity from text."""
def extract_quantity(text: str) -> int:
  return 1

"""
  This agent will be the frontline of all user queries. Responsibility of this agent will be:
  - Parse raw user queries and extract required information.
  - Detect category of item like grocery, electronics, clothing, etc.
  - Extract quantity of the item.
  - Extract unit of the desired quantity such as pcs, pieces, kg, litre, boxes, and so on.
  - Decide the next action.
"""
def parse_user_input(text: str) -> RequestedItem:
  items = []
  text = text.lower()

  # reducing common phrases so that we can focus on the keywords
  text = re.sub(r'\bi want\b|\bi need\b|\bbuy\b|\bget me\b', '', text)

  # handling conjunctions like 'and' and commas when multiple items are requested
  # splits text wherever the pattern matches
  parts = re.split(r',|\sand\s', text)

  for part in parts:
        part = part.strip()
        if not part:
            continue
        
        quantity = extract_quantity(part)
        
        
        item_text = re.sub(r'\d+\s*(?:pcs|pieces|units|nos|boxes)?', '', part).strip()
        
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in item_text:
                    items.append(RequestedItem(
                        name=keyword,
                        category=category,
                        quantity=quantity
                    ))
                    break
    
  return items

def intent_parser_agent(state: PurchaseState) -> PurchaseState:
    user_input = state["user_input"]
    parsed_items = parse_user_input(user_input)

    # Add a message from the assistant summarizing the parsed items
    if parsed_items:
        summary = "I found these items:\n" + "\n".join(
            f"- {item.quantity} x {item.name} ({item.category})" for item in parsed_items
        )
    else:
        summary = "Sorry, I couldn't find any items in your request."

    # Update state
    state["parsed_items"] = parsed_items
    state["messages"] = ({"role": "assistant", "content": summary})
    state["conversation_complete"] = True  # End after one turn for now

    return state