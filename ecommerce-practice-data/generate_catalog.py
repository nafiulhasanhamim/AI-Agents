import json
import random

categories = {
    "Photography": ["Camera", "Lens", "Tripod", "Flash", "SD Card"],
    "Audio": ["Headphones", "Earbuds", "Speaker", "Soundbar", "Microphone"],
    "Computing": ["Laptop", "Desktop", "Monitor", "Keyboard", "Mouse"],
    "Smart Home": ["Bulb", "Camera", "Thermostat", "Plug", "Lock"],
    "Wearables": ["Watch", "Fitness Tracker", "Smart Ring", "VR Headset"],
    "Kitchen": ["Blender", "Air Fryer", "Coffee Maker", "Toaster", "Microwave"],
    "Home Office": ["Chair", "Desk", "Lamp", "Docking Station", "Webcam"],
    "Gaming": ["Console", "Controller", "Headset", "Gaming Chair", "Capture Card"],
    "Fitness": ["Treadmill", "Dumbbells", "Yoga Mat", "Bike", "Massage Gun"],
    "Mobile": ["Smartphone", "Tablet", "Case", "Power Bank", "Charger"]
}

brands = ["Titan", "Lumix", "Audio-Technica", "Swift", "Aero", "Pulse", "Zenith", "Glow", "Secure", "Vibe"]
features = ["Wireless", "Pro", "Elite", "Ultra", "Max", "Mini", "Lite", "Smart", "Carbon", "Prime"]

products = []

for i in range(1, 501):
    cat_name = random.choice(list(categories.keys()))
    sub_cat = random.choice(categories[cat_name])
    brand = random.choice(brands)
    feature = random.choice(features)
    
    sku = f"{cat_name[:3].upper()}-{brand[:3].upper()}-{i:03d}"
    name = f"{brand} {feature} {sub_cat} {random.randint(2024, 2026)}"
    price = round(random.uniform(19.99, 2999.99), 2)
    
    prod = {
        "id": sku,
        "name": name,
        "category": cat_name,
        "brand": brand,
        "price": price,
        "description": f"The {name} offers top-tier performance for {cat_name.lower()} enthusiasts. Designed with the latest technology for 2026.",
        "specs": {
            "model_year": 2026,
            "warranty": "2 Years",
            "rating": round(random.uniform(3.5, 5.0), 1)
        }
    }
    products.append(prod)

# Save as JSON
with open('c:/Projects/AI Agent/ecommerce-practice-data/massive_catalog.json', 'w') as f:
    json.dump(products, f, indent=2)

# Save as Markdown
with open('c:/Projects/AI Agent/ecommerce-practice-data/massive_catalog.md', 'w') as f:
    f.write("# Massive Product Catalog (500 Items)\n\n")
    for p in products:
        f.write(f"## {p['name']}\n")
        f.write(f"- **SKU**: {p['id']}\n")
        f.write(f"- **Category**: {p['category']}\n")
        f.write(f"- **Price**: ${p['price']}\n")
        f.write(f"- **Description**: {p['description']}\n")
        f.write(f"- **Rating**: {p['specs']['rating']} stars\n\n")

print(f"Successfully generated 500 items in JSON and Markdown formats.")
