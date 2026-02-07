from models.state import PurchaseState
from langchain.messages import AIMessage

def billing_agent(state: PurchaseState) -> PurchaseState:
    """ billing agent - calculate total and create order summary """

    parserdItems = state.get("parsed_items", [])
    selectedProvider = state.get("selected_provider", "")
    providerResults = state.get("provider_results", {})
    print(f"Provider Results: {providerResults}")

    finalOrder = {
        "provider": selectedProvider,
        "items": [],
        "totalAmount": 0.0,
        "deliveryPreference": "Unknown"
    }

    for item in parserdItems:
        itemName = item.get("name", "")
        itemQuantity = item.get("quantity", 1)

        providerItems = providerResults.get(itemName, {}).get(selectedProvider[itemName].lower(), [])
        print(f"Provider Items: {providerItems}")
        
        if providerItems:
            """
            for now take the first available item.
            later, this will be chosen by the Purchase Agent based on various factors.
            """
            itemFound = providerItems[0]
            itemTotal = getattr(itemFound, "price", 0.0) * itemQuantity

            finalOrder["items"].append({
                "name": itemName,
                "quantity": itemQuantity,
                "unitPrice": getattr(itemFound, "price", 0.0),
                "total": itemTotal,
            })

            finalOrder["deliveryPreference"] = getattr(itemFound, "deliveryHours", "Unknown")
            finalOrder["totalAmount"] += itemTotal
                
    state["final_order"] = finalOrder
    
    # construct output message
    orderSummary = f"Order Summary from {finalOrder['provider']}:\n"
    for orderItem in finalOrder["items"]:
        orderSummary += f"- {orderItem['name']}: {orderItem['quantity']} x {orderItem['unitPrice']} = {orderItem['total']}\n"
    orderSummary += f"Total Amount: {finalOrder['totalAmount']}\n"
    orderSummary += f"Delivery Preference: {finalOrder['deliveryPreference']}\n"

    state["messages"].append(AIMessage(content=orderSummary))
    # ask for human approval
    state["need_human_approval"] = True
    state["next_agent"] = "human_approval"

    return state