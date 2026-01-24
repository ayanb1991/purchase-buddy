from data.items import Inventory
from models.state import InventoryItem


def searchSwiggy(itemName: str, category: str, pincode: str  = None) -> list[InventoryItem]:
    results = []

    if category.lower() in Inventory:
        categoryItems = [item for item in Inventory if item['category'].lower() == category.lower()]

        for item in categoryItems:
            if item['provider'].lower() == "swiggy" and itemName.lower() in item["name"].lower():
                if pincode and pincode not in item.get("pincodes", []):
                    item = item.copy()
                    item["isAvailable"] = False
                    item["availabilityStatus"] = "Item not deliverable to the provided pincode."
                results.append(InventoryItem(**item))

    return results
