import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any
import uuid

class ComplexProductGenerator:
    def __init__(self):
        self.categories = {
            "Electronics > Computers > Gaming Laptops": {
                "brands": ["Titan", "Apex", "Vortex", "Phoenix", "Storm"],
                "price_range": (1200, 4000),
                "base_specs": {
                    "processor": ["Intel i7-13700K", "Intel i9-14900K", "AMD Ryzen 7 7700X", "AMD Ryzen 9 7900X"],
                    "graphics": ["RTX 4060", "RTX 4070", "RTX 4080", "RTX 4090", "RX 7600", "RX 7700 XT"],
                    "ram": ["16GB DDR5", "32GB DDR5", "64GB DDR5"],
                    "storage": ["512GB NVMe", "1TB NVMe", "2TB NVMe", "1TB + 512GB"]
                }
            },
            "Electronics > Mobile > Smartphones": {
                "brands": ["Apex", "Quantum", "Nova", "Stellar", "Pulse"],
                "price_range": (300, 1500),
                "base_specs": {
                    "processor": ["Snapdragon 8 Gen 3", "Snapdragon 8 Gen 4", "A17 Pro", "Dimensity 9300"],
                    "camera": ["50MP Triple", "108MP Quad", "200MP Triple", "64MP Dual"],
                    "battery": ["4000mAh", "5000mAh", "5500mAh", "6000mAh"],
                    "storage": ["128GB", "256GB", "512GB", "1TB"]
                }
            },
            "Electronics > Audio > Headphones": {
                "brands": ["SoundWave", "AudioTech", "Harmony", "Resonance", "Echo"],
                "price_range": (50, 800),
                "base_specs": {
                    "type": ["Over-ear", "On-ear", "In-ear", "True Wireless"],
                    "noise_cancelling": ["Active ANC", "Passive", "Hybrid ANC"],
                    "battery": ["20 hours", "30 hours", "40 hours", "8 hours + case"],
                    "connectivity": ["Bluetooth 5.3", "Bluetooth 5.4", "Wired + Wireless"]
                }
            },
            "Electronics > Gaming > Consoles": {
                "brands": ["GameForce", "PlayMax", "UltraBox", "NeoStation"],
                "price_range": (300, 800),
                "base_specs": {
                    "processor": ["Custom AMD Zen 4", "Custom ARM", "Intel Custom"],
                    "graphics": ["Custom RDNA 3", "Custom RTX", "Integrated"],
                    "storage": ["512GB SSD", "1TB SSD", "2TB SSD"],
                    "resolution": ["4K 60fps", "4K 120fps", "8K 30fps"]
                }
            },
            "Home > Kitchen > Appliances": {
                "brands": ["ChefMaster", "CookPro", "KitchenElite", "HomeTech"],
                "price_range": (100, 2000),
                "base_specs": {
                    "capacity": ["2L", "5L", "8L", "12L"],
                    "power": ["1200W", "1500W", "1800W", "2000W"],
                    "features": ["Digital Display", "Smart Controls", "Voice Control"],
                    "material": ["Stainless Steel", "Ceramic", "Non-stick"]
                }
            }
        }
        
        self.features_pool = {
            "gaming_laptop": [
                "RGB mechanical keyboard with customizable lighting",
                "Advanced liquid cooling system",
                "High refresh rate display (144Hz-240Hz)",
                "Thunderbolt 4 connectivity",
                "Wi-Fi 6E support",
                "Premium audio with subwoofer",
                "Overclocking support",
                "VR Ready certification"
            ],
            "smartphone": [
                "5G connectivity",
                "Wireless charging",
                "Water resistance IP68",
                "Face unlock and fingerprint scanner",
                "AI-powered camera features",
                "Fast charging technology",
                "Stereo speakers",
                "Always-on display"
            ],
            "headphones": [
                "Active noise cancellation",
                "Transparency mode",
                "Multi-device connectivity",
                "Voice assistant integration",
                "Custom EQ settings",
                "Quick charge capability",
                "Foldable design",
                "Premium materials"
            ],
            "console": [
                "Backward compatibility",
                "Ray tracing support",
                "Variable refresh rate",
                "Quick resume feature",
                "Cloud gaming integration",
                "4K Blu-ray player",
                "Expandable storage",
                "HDR10 support"
            ],
            "appliance": [
                "Smart home integration",
                "Energy efficient design",
                "Multiple cooking presets",
                "Easy cleanup features",
                "Safety auto-shutoff",
                "Digital timer and controls",
                "Compact design",
                "Warranty included"
            ]
        }
        
        self.review_templates = [
            {
                "rating": 5,
                "titles": ["Excellent product!", "Highly recommended", "Perfect for my needs", "Outstanding quality"],
                "comments": [
                    "Exceeded my expectations in every way",
                    "Build quality is exceptional",
                    "Performance is outstanding",
                    "Great value for the price",
                    "Customer service was helpful"
                ]
            },
            {
                "rating": 4,
                "titles": ["Very good product", "Solid choice", "Good but not perfect", "Recommended with minor issues"],
                "comments": [
                    "Great product with minor flaws",
                    "Good performance but could be better",
                    "Solid build quality, some software issues",
                    "Good value, minor complaints",
                    "Works well after initial setup"
                ]
            },
            {
                "rating": 3,
                "titles": ["Average product", "Mixed feelings", "Okay for the price", "Has potential"],
                "comments": [
                    "Does what it's supposed to do",
                    "Average quality for the price range",
                    "Some good features, some disappointing",
                    "Acceptable but not impressive",
                    "Works but has room for improvement"
                ]
            }
        ]

    def generate_product_id(self, category: str, brand: str, index: int) -> str:
        """Generate unique product ID"""
        cat_code = category.split(" > ")[-1][:3].upper()
        brand_code = brand[:3].upper()
        return f"{cat_code}-{brand_code}-{index:03d}"

    def generate_sku(self, product_id: str, variant: str = "") -> str:
        """Generate SKU"""
        year = datetime.now().year
        variant_code = f"-{variant}" if variant else ""
        return f"{product_id}-{year}{variant_code}"

    def generate_specifications(self, category: str, base_specs: Dict) -> Dict[str, Any]:
        """Generate detailed specifications based on category"""
        if "Gaming Laptops" in category:
            return self._generate_laptop_specs(base_specs)
        elif "Smartphones" in category:
            return self._generate_phone_specs(base_specs)
        elif "Headphones" in category:
            return self._generate_headphone_specs(base_specs)
        elif "Consoles" in category:
            return self._generate_console_specs(base_specs)
        elif "Appliances" in category:
            return self._generate_appliance_specs(base_specs)
        else:
            return {"general": base_specs}

    def _generate_laptop_specs(self, base_specs: Dict) -> Dict[str, Any]:
        """Generate laptop specifications"""
        processor_choice = random.choice(base_specs["processor"])
        graphics_choice = random.choice(base_specs["graphics"])
        
        return {
            "processor": {
                "model": processor_choice,
                "cores": random.choice([8, 12, 16, 24]),
                "threads": random.choice([16, 24, 32, 48]),
                "base_clock": f"{random.uniform(2.5, 3.5):.1f} GHz",
                "boost_clock": f"{random.uniform(4.5, 6.0):.1f} GHz"
            },
            "graphics": {
                "model": graphics_choice,
                "vram": random.choice(["8GB", "12GB", "16GB", "24GB"]),
                "ray_tracing": "RTX" in graphics_choice,
                "dlss": "RTX" in graphics_choice
            },
            "memory": {
                "capacity": random.choice(base_specs["ram"]),
                "type": "DDR5-5600",
                "slots": random.choice([2, 4]),
                "expandable": True
            },
            "storage": {
                "primary": random.choice(base_specs["storage"]),
                "type": "NVMe PCIe 4.0",
                "speed": f"{random.randint(5000, 7500)} MB/s"
            },
            "display": {
                "size": random.choice(["15.6 inch", "17.3 inch"]),
                "resolution": random.choice(["1920x1080", "2560x1440", "3840x2160"]),
                "refresh_rate": random.choice(["144Hz", "165Hz", "240Hz"]),
                "panel_type": random.choice(["IPS", "OLED", "Mini-LED"])
            },
            "physical": {
                "weight": f"{random.uniform(2.0, 3.5):.1f} kg",
                "thickness": f"{random.uniform(18, 25):.1f} mm",
                "material": random.choice(["Aluminum", "Magnesium Alloy", "Carbon Fiber"])
            }
        }

    def _generate_phone_specs(self, base_specs: Dict) -> Dict[str, Any]:
        """Generate smartphone specifications"""
        return {
            "processor": {
                "chipset": random.choice(base_specs["processor"]),
                "process": random.choice(["4nm", "3nm"]),
                "cpu_cores": "Octa-core",
                "gpu": random.choice(["Adreno 750", "Mali-G715", "Apple GPU"])
            },
            "display": {
                "size": f"{random.uniform(6.1, 6.8):.1f} inch",
                "type": random.choice(["AMOLED", "Super AMOLED", "LTPO OLED"]),
                "resolution": random.choice(["2400x1080", "3200x1440", "2796x1290"]),
                "refresh_rate": random.choice(["90Hz", "120Hz", "144Hz"]),
                "brightness": f"{random.randint(800, 2000)} nits"
            },
            "camera": {
                "main": {
                    "sensor": random.choice(base_specs["camera"]),
                    "aperture": f"f/{random.uniform(1.4, 2.0):.1f}",
                    "ois": random.choice([True, False])
                },
                "ultra_wide": {
                    "sensor": f"{random.choice([12, 16, 48])}MP",
                    "field_of_view": f"{random.randint(110, 130)}°"
                },
                "front": {
                    "sensor": f"{random.choice([12, 16, 32])}MP",
                    "aperture": f"f/{random.uniform(2.0, 2.4):.1f}"
                }
            },
            "battery": {
                "capacity": random.choice(base_specs["battery"]),
                "wired_charging": f"{random.choice([25, 45, 67, 120])}W",
                "wireless_charging": f"{random.choice([15, 25, 50])}W"
            },
            "memory_storage": {
                "ram": random.choice(["8GB", "12GB", "16GB"]),
                "storage": random.choice(base_specs["storage"]),
                "expandable": random.choice([True, False])
            }
        }

    def _generate_headphone_specs(self, base_specs: Dict) -> Dict[str, Any]:
        """Generate headphone specifications"""
        return {
            "audio": {
                "driver_size": f"{random.choice([40, 50, 53])}mm",
                "frequency_response": f"{random.choice([20, 15])}Hz - {random.choice([20, 40])}kHz",
                "impedance": f"{random.choice([32, 80, 250])} ohms",
                "sensitivity": f"{random.randint(95, 110)} dB"
            },
            "connectivity": {
                "wireless": random.choice(base_specs["connectivity"]),
                "codecs": random.choice([["SBC", "AAC"], ["SBC", "AAC", "aptX"], ["SBC", "AAC", "LDAC"]]),
                "range": f"{random.choice([10, 15, 30])}m"
            },
            "battery": {
                "life": random.choice(base_specs["battery"]),
                "charging_time": f"{random.choice([2, 3, 4])} hours",
                "quick_charge": f"{random.choice([15, 30])} min for {random.choice([3, 6])} hours"
            },
            "physical": {
                "weight": f"{random.randint(200, 400)}g",
                "foldable": random.choice([True, False]),
                "materials": random.choice(["Plastic", "Metal + Plastic", "Premium Metal"])
            }
        }

    def _generate_console_specs(self, base_specs: Dict) -> Dict[str, Any]:
        """Generate gaming console specifications"""
        return {
            "processor": {
                "cpu": random.choice(base_specs["processor"]),
                "cores": random.choice([8, 12]),
                "clock_speed": f"{random.uniform(3.0, 4.0):.1f} GHz"
            },
            "graphics": {
                "gpu": random.choice(base_specs["graphics"]),
                "compute_units": random.choice([36, 52, 60]),
                "ray_tracing": True
            },
            "memory": {
                "ram": random.choice(["16GB GDDR6", "32GB GDDR6"]),
                "bandwidth": f"{random.choice([448, 560, 672])} GB/s"
            },
            "storage": {
                "internal": random.choice(base_specs["storage"]),
                "expandable": True,
                "speed": f"{random.choice([2400, 5500, 7000])} MB/s"
            },
            "output": {
                "max_resolution": random.choice(base_specs["resolution"]),
                "hdr": random.choice(["HDR10", "HDR10+", "Dolby Vision"]),
                "audio": random.choice(["7.1 Surround", "Dolby Atmos", "DTS:X"])
            }
        }

    def _generate_appliance_specs(self, base_specs: Dict) -> Dict[str, Any]:
        """Generate kitchen appliance specifications"""
        return {
            "capacity": {
                "volume": random.choice(base_specs["capacity"]),
                "servings": f"{random.choice([2, 4, 6, 8])} people"
            },
            "power": {
                "wattage": random.choice(base_specs["power"]),
                "voltage": "120V",
                "energy_rating": random.choice(["A++", "A+++"])
            },
            "features": {
                "presets": random.choice([8, 12, 15]),
                "timer": "24-hour programmable",
                "display": random.choice(["LED", "LCD", "Touch Screen"])
            },
            "physical": {
                "dimensions": f"{random.randint(25, 40)}x{random.randint(30, 45)}x{random.randint(20, 35)} cm",
                "weight": f"{random.uniform(3.0, 8.0):.1f} kg",
                "material": random.choice(base_specs["material"])
            }
        }

    def generate_reviews(self, product_name: str, price: float) -> Dict[str, Any]:
        """Generate realistic product reviews"""
        total_reviews = random.randint(50, 2000)
        
        # Generate rating distribution (higher ratings more likely for expensive products)
        price_factor = min(price / 1000, 2.0)  # Normalize price influence
        
        # Higher priced items tend to have better ratings
        rating_weights = [
            max(1, 10 - int(price_factor * 3)),  # 1 star
            max(1, 15 - int(price_factor * 4)),  # 2 star  
            max(5, 25 - int(price_factor * 5)),  # 3 star
            max(15, 35 + int(price_factor * 2)), # 4 star
            max(20, 45 + int(price_factor * 5))  # 5 star
        ]
        
        distribution = {}
        remaining = total_reviews
        
        for i in range(5, 0, -1):
            if i == 1:
                count = remaining
            else:
                weight = rating_weights[i-1]
                count = int((weight / sum(rating_weights)) * total_reviews)
                remaining -= count
            distribution[f"{i}_star"] = max(0, count)
        
        # Calculate average rating
        total_weighted = sum(int(k.split('_')[0]) * v for k, v in distribution.items())
        avg_rating = round(total_weighted / total_reviews, 1)
        
        # Generate featured reviews
        featured_reviews = []
        for _ in range(random.randint(2, 4)):
            template = random.choice(self.review_templates)
            review = {
                "reviewer": f"User_{random.randint(1000, 9999)}",
                "rating": template["rating"],
                "title": random.choice(template["titles"]),
                "content": self._generate_review_content(product_name, template),
                "verified_purchase": random.choice([True, True, True, False]),  # 75% verified
                "helpful_votes": random.randint(5, 200)
            }
            featured_reviews.append(review)
        
        return {
            "average_rating": avg_rating,
            "total_reviews": total_reviews,
            "rating_distribution": distribution,
            "featured_reviews": featured_reviews
        }

    def _generate_review_content(self, product_name: str, template: Dict) -> str:
        """Generate review content based on template"""
        comments = template["comments"]
        
        content_parts = [
            random.choice(comments),
            f"The {product_name.split()[0]} brand delivers quality.",
            random.choice([
                "Would recommend to others.",
                "Good value for money.",
                "Meets my expectations.",
                "Solid product overall."
            ])
        ]
        
        return " ".join(random.sample(content_parts, random.randint(2, 3)))

    def generate_product(self, index: int, category: str, category_data: Dict) -> Dict[str, Any]:
        """Generate a single complex product"""
        brand = random.choice(category_data["brands"])
        price_min, price_max = category_data["price_range"]
        price = round(random.uniform(price_min, price_max), 2)
        
        # Generate product name
        model_suffix = random.choice(["Pro", "Elite", "Max", "Ultra", "Plus", "X", "Prime"])
        model_number = random.choice(["2024", "2025", "2026", f"X{random.randint(1, 9)}", f"{random.randint(100, 999)}"])
        product_name = f"{brand} {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Titan', 'Nova', 'Apex'])} {model_suffix} {model_number}"
        
        product_id = self.generate_product_id(category, brand, index)
        
        # Generate dates
        release_date = datetime.now() - timedelta(days=random.randint(30, 365))
        last_updated = datetime.now() - timedelta(days=random.randint(1, 30))
        
        # Generate specifications
        specifications = self.generate_specifications(category, category_data["base_specs"])
        
        # Generate features based on category
        category_key = self._get_feature_category_key(category)
        available_features = self.features_pool.get(category_key, self.features_pool["gaming_laptop"])
        features = random.sample(available_features, random.randint(4, 7))
        
        # Generate reviews
        reviews = self.generate_reviews(product_name, price)
        
        # Determine sale status
        on_sale = random.choice([True, False, False, False])  # 25% chance
        discount_percent = random.randint(5, 30) if on_sale else 0
        original_price = round(price / (1 - discount_percent/100), 2) if on_sale else price
        
        product = {
            "id": product_id,
            "name": product_name,
            "category": category,
            "subcategory": category.split(" > ")[-1],
            "brand": brand,
            "model": f"{model_suffix} {model_number}",
            "sku": self.generate_sku(product_id),
            "price": price,
            "currency": "USD",
            "in_stock": random.choice([True, True, True, False]),  # 75% in stock
            "stock_quantity": random.randint(0, 200) if random.choice([True, True, False]) else 0,
            "on_sale": on_sale,
            "discount_percent": discount_percent,
            "original_price": original_price,
            "release_date": release_date.strftime("%Y-%m-%d"),
            "last_updated": last_updated.strftime("%Y-%m-%d"),
            
            "short_description": self._generate_short_description(product_name, category),
            "detailed_description": self._generate_detailed_description(product_name, category, features),
            
            "specifications": specifications,
            "features": features,
            
            "warranty": {
                "duration": random.choice(["1 year", "2 years", "3 years"]),
                "type": random.choice(["Limited Warranty", "Extended Warranty", "Premium Warranty"]),
                "coverage": ["Manufacturing defects", "Hardware failures"],
                "support": random.choice(["Email support", "Phone support", "24/7 support"])
            },
            
            "reviews": reviews,
            
            "compatibility": {
                "operating_systems": self._get_compatible_os(category),
                "requirements": self._get_requirements(category)
            },
            
            "included_accessories": self._get_accessories(category),
            
            "tags": self._generate_tags(category, brand, features),
            "search_keywords": self._generate_search_keywords(product_name, category, brand)
        }
        
        return product

    def _get_feature_category_key(self, category: str) -> str:
        """Map category to feature pool key"""
        if "Gaming Laptops" in category:
            return "gaming_laptop"
        elif "Smartphones" in category:
            return "smartphone"
        elif "Headphones" in category:
            return "headphones"
        elif "Consoles" in category:
            return "console"
        elif "Appliances" in category:
            return "appliance"
        else:
            return "gaming_laptop"

    def _generate_short_description(self, name: str, category: str) -> str:
        """Generate short product description"""
        templates = {
            "Gaming Laptops": "High-performance gaming laptop with advanced graphics and premium build quality.",
            "Smartphones": "Feature-rich smartphone with advanced camera system and long-lasting battery.",
            "Headphones": "Premium audio experience with superior sound quality and comfort.",
            "Consoles": "Next-generation gaming console with cutting-edge performance and features.",
            "Appliances": "Smart kitchen appliance designed for convenience and efficiency."
        }
        
        for key, template in templates.items():
            if key in category:
                return template
        
        return "Premium product designed for performance and reliability."

    def _generate_detailed_description(self, name: str, category: str, features: List[str]) -> str:
        """Generate detailed product description"""
        intro = f"The {name} represents the latest in {category.split(' > ')[-1].lower()} technology, combining cutting-edge performance with premium design."
        
        feature_text = f"Key features include {', '.join(features[:3]).lower()}, ensuring exceptional user experience."
        
        conclusion = "Built with premium materials and backed by comprehensive warranty, this product delivers reliability and performance you can trust."
        
        return f"{intro}\n\n{feature_text}\n\n{conclusion}"

    def _get_compatible_os(self, category: str) -> List[str]:
        """Get compatible operating systems"""
        if "Gaming Laptops" in category:
            return ["Windows 11", "Linux (Ubuntu certified)"]
        elif "Smartphones" in category:
            return [random.choice(["Android 14", "iOS 17", "HarmonyOS"])]
        else:
            return ["Universal compatibility"]

    def _get_requirements(self, category: str) -> List[str]:
        """Get product requirements"""
        if "Gaming Laptops" in category:
            return ["Power adapter included", "Minimum 2GB free storage for software"]
        elif "Smartphones" in category:
            return ["SIM card", "Compatible carrier"]
        elif "Headphones" in category:
            return ["Bluetooth-enabled device", "Charging cable included"]
        else:
            return ["Standard power outlet", "User manual included"]

    def _get_accessories(self, category: str) -> List[str]:
        """Get included accessories"""
        accessories_map = {
            "Gaming Laptops": ["Power adapter", "User manual", "Warranty card", "Cleaning cloth"],
            "Smartphones": ["USB-C cable", "Power adapter", "SIM ejector tool", "Quick start guide"],
            "Headphones": ["Charging cable", "Carrying case", "Audio cable", "User manual"],
            "Consoles": ["Power cable", "HDMI cable", "Controller", "Quick setup guide"],
            "Appliances": ["Power cord", "Recipe book", "User manual", "Warranty card"]
        }
        
        for key, accessories in accessories_map.items():
            if key in category:
                return random.sample(accessories, random.randint(2, len(accessories)))
        
        return ["User manual", "Warranty card"]

    def _generate_tags(self, category: str, brand: str, features: List[str]) -> List[str]:
        """Generate product tags"""
        tags = [brand.lower(), category.split(" > ")[-1].lower().replace(" ", "-")]
        
        # Add feature-based tags
        for feature in features[:3]:
            tag = feature.lower().split()[0]
            if len(tag) > 3:
                tags.append(tag)
        
        # Add category-specific tags
        if "Gaming" in category:
            tags.extend(["gaming", "high-performance"])
        if "Premium" in " ".join(features):
            tags.append("premium")
        
        return list(set(tags))

    def _generate_search_keywords(self, name: str, category: str, brand: str) -> List[str]:
        """Generate search keywords"""
        keywords = [
            name.lower(),
            brand.lower(),
            category.split(" > ")[-1].lower()
        ]
        
        # Add category-specific keywords
        category_keywords = {
            "Gaming Laptops": ["gaming laptop", "high performance", "gaming computer"],
            "Smartphones": ["smartphone", "mobile phone", "cell phone"],
            "Headphones": ["headphones", "audio", "wireless headphones"],
            "Consoles": ["gaming console", "video game console"],
            "Appliances": ["kitchen appliance", "smart appliance"]
        }
        
        for key, kw_list in category_keywords.items():
            if key in category:
                keywords.extend(kw_list)
                break
        
        return list(set(keywords))

    def generate_catalog(self, total_products: int = 100) -> List[Dict[str, Any]]:
        """Generate complete product catalog"""
        catalog = []
        products_per_category = total_products // len(self.categories)
        
        index = 1
        for category, category_data in self.categories.items():
            print(f"Generating {products_per_category} products for {category}...")
            
            for i in range(products_per_category):
                product = self.generate_product(index, category, category_data)
                catalog.append(product)
                index += 1
        
        # Generate remaining products to reach total
        remaining = total_products - len(catalog)
        if remaining > 0:
            print(f"Generating {remaining} additional products...")
            for i in range(remaining):
                category = random.choice(list(self.categories.keys()))
                category_data = self.categories[category]
                product = self.generate_product(index, category, category_data)
                catalog.append(product)
                index += 1
        
        return catalog

def main():
    generator = ComplexProductGenerator()
    
    # Generate catalog with specified number of products
    num_products = int(input("Enter number of products to generate (default 100): ") or "100")
    
    print(f"Generating {num_products} complex products...")
    catalog = generator.generate_catalog(num_products)
    
    # Save to file
    output_file = "ecommerce-practice-data/large_complex_catalog.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {len(catalog)} products and saved to {output_file}")
    
    # Print summary statistics
    categories = {}
    brands = set()
    price_ranges = []
    
    for product in catalog:
        category = product['category']
        categories[category] = categories.get(category, 0) + 1
        brands.add(product['brand'])
        price_ranges.append(product['price'])
    
    print("\n=== CATALOG SUMMARY ===")
    print(f"Total Products: {len(catalog)}")
    print(f"Categories: {len(categories)}")
    for cat, count in categories.items():
        print(f"  - {cat}: {count} products")
    print(f"Brands: {len(brands)}")
    print(f"Price Range: ${min(price_ranges):.2f} - ${max(price_ranges):.2f}")
    print(f"Average Price: ${sum(price_ranges)/len(price_ranges):.2f}")

if __name__ == "__main__":
    main()