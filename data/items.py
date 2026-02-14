from models.state import InventoryItem

"""
Fixed list of items that app supports as of now.
"""

Inventory: list[InventoryItem] = [
    {
        "name": "Milk",
        "type": "diary",
        "category": "grocery",
        "unit": "litre",
        "price": 30,
        "provider": "Blinkfit",
        "isQuickDelivery": True,
        "isAvailable": True,
        "pincodes": ["700129", "713304", "713303"],
        "deliveryHours": "24hrs"
    },
    {
        "name": "Laptop",
        "type": "computer",
        "category": "electronics",
        "unit": "piece",
        "price": 45000,
        "provider": "Amazon",
        "isQuickDelivery": False,
        "isAvailable": True,
        "pincodes": ["700129", "713304", "713303"],
        "deliveryHours": "24hrs"
    },
    {
        "name": "Biryani",
        "type": "food",
        "category": "cookedfood",
        "unit": "plate",
        "price": 250,
        "provider": "Sniggy",
        "isQuickDelivery": True,
        "isAvailable": True,
        "pincodes": ["700129", "700020", "700001"],
        "deliveryHours": "11-23"
    },
    {
        "name": "Biryani",
        "type": "food",
        "category": "cookedfood",
        "unit": "plate",
        "price": 300,
        "provider": "Zonato",
        "isQuickDelivery": True,
        "isAvailable": True,
        "pincodes": ["700129", "700020"],
        "deliveryHours": "11-23"
    }
]