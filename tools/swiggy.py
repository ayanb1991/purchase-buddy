from data.items import Inventory
from models.state import InventoryItem


def searchSwiggy(itemName: str, category: str, pincode: str = None) -> list[InventoryItem]:
    results = []

    if any(item['category'].lower() == category.lower() for item in Inventory):
        categoryItems = [item for item in Inventory if item['category'].lower() == category.lower()]

        for item in categoryItems:
            if item['provider'].lower() == "swiggy" and itemName.lower() in item["name"].lower():
                item_copy = item.copy()
                if pincode and pincode not in item_copy.get("pincodes", []):
                    item_copy["isAvailable"] = False
                    item_copy["availabilityStatus"] = "Item not deliverable to the provided pincode."
                results.append(InventoryItem(**item_copy))

    return results
