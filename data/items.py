"""
Fixed list of items that app supports as of now.
"""

grocery_items = [
    {
        "name": "Milk",
        "type": "diary",
        "unit": "litre",
        "price": 30,
        "provider": "Blinkit",
        "isQuickDelivery": True,
        "isAvailable": True,
        "pincodes": [700129, 713304, 713303],
        "deliveryHours": "24hrs"
    }
]

electronic_items = [
    {
        "name": "Laptop",
        "type": "computer",
        "unit": "piece",
        "price": 45000,
        "provider": "Amazon",
        "isQuickDelivery": False,
        "isAvailable": True,
        "pincodes": [700129, 713304, 713303],
        "deliveryHours": "24hrs"
    }
]

cooked_foods = [
    {
        "name": "Biryani",
        "type": "food",
        "unit": "plate",
        "price": 250,
        "provider": "Swiggy",
        "isQuickDelivery": True,
        "isAvailable": True,
        "pincodes": [700129, 700020, 700001],
        "deliveryHours": "11-23"
    }
]