from data.items import Inventory
from models.state import InventoryItem


def searchSniggy(itemName: str, category: str, pincode: str = None) -> list[InventoryItem]:
    results = []

    if any(item['category'].lower() == category.lower() for item in Inventory):
        categoryItems = [item for item in Inventory if item['category'].lower() == category.lower()]

        for item in categoryItems:
            if item['provider'].lower() == "sniggy" and itemName.lower() in item["name"].lower():
                matchedItem = item.copy()
                if pincode and pincode not in matchedItem.get("pincodes", []):
                    matchedItem["isAvailable"] = False
                    matchedItem["availabilityStatus"] = "Item not deliverable to the provided pincode."
                results.append(InventoryItem(**matchedItem))

    return results
