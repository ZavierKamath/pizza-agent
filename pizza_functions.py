# Simple in-memory storage
ORDERS_DB = {"orders": {}, "next_id": 1}

# Zavier's Pizza Menu
PIZZA_MENU = {
    "sizes": {
        "small": {"name": "Small (10\")", "base_price": 12.99},
        "medium": {"name": "Medium (12\")", "base_price": 15.99},
        "large": {"name": "Large (14\")", "base_price": 18.99},
        "extra_large": {"name": "Extra Large (16\")", "base_price": 21.99}
    },
    "specialty_pizzas": {
        "margherita": {
            "name": "Margherita",
            "description": "Fresh mozzarella, tomato sauce, basil",
            "toppings": ["mozzarella", "basil"]
        },
        "pepperoni": {
            "name": "Pepperoni Classic",
            "description": "Pepperoni and mozzarella cheese",
            "toppings": ["pepperoni", "mozzarella"]
        },
        "supreme": {
            "name": "Supreme",
            "description": "Pepperoni, sausage, bell peppers, onions, mushrooms",
            "toppings": ["pepperoni", "sausage", "bell_peppers", "onions", "mushrooms"]
        },
        "meat_lovers": {
            "name": "Meat Lovers",
            "description": "Pepperoni, sausage, ham, bacon",
            "toppings": ["pepperoni", "sausage", "ham", "bacon"]
        },
        "vegetarian": {
            "name": "Vegetarian",
            "description": "Bell peppers, onions, mushrooms, olives, tomatoes",
            "toppings": ["bell_peppers", "onions", "mushrooms", "olives", "tomatoes"]
        },
        "hawaiian": {
            "name": "Hawaiian",
            "description": "Ham and pineapple",
            "toppings": ["ham", "pineapple"]
        }
    },
    "toppings": {
        "meats": {
            "pepperoni": {"name": "Pepperoni", "price": 1.50},
            "sausage": {"name": "Italian Sausage", "price": 1.50},
            "ham": {"name": "Ham", "price": 1.50},
            "bacon": {"name": "Bacon", "price": 1.75},
            "chicken": {"name": "Grilled Chicken", "price": 2.00}
        },
        "vegetables": {
            "mushrooms": {"name": "Mushrooms", "price": 1.00},
            "bell_peppers": {"name": "Bell Peppers", "price": 1.00},
            "onions": {"name": "Onions", "price": 1.00},
            "olives": {"name": "Black Olives", "price": 1.25},
            "tomatoes": {"name": "Fresh Tomatoes", "price": 1.25},
            "pineapple": {"name": "Pineapple", "price": 1.25},
            "jalapenos": {"name": "Jalapeños", "price": 1.00},
            "basil": {"name": "Fresh Basil", "price": 1.50}
        },
        "cheeses": {
            "mozzarella": {"name": "Extra Mozzarella", "price": 1.75},
            "parmesan": {"name": "Parmesan", "price": 1.50},
            "feta": {"name": "Feta Cheese", "price": 2.00}
        }
    },
    "sides": {
        "garlic_bread": {"name": "Garlic Bread", "price": 6.99},
        "chicken_wings": {"name": "Chicken Wings (8 pcs)", "price": 9.99},
        "breadsticks": {"name": "Breadsticks (6 pcs)", "price": 5.99},
        "caesar_salad": {"name": "Caesar Salad", "price": 7.99},
        "garden_salad": {"name": "Garden Salad", "price": 6.99}
    },
    "drinks": {
        "coke": {"name": "Coca-Cola (2L)", "price": 3.99},
        "pepsi": {"name": "Pepsi (2L)", "price": 3.99},
        "sprite": {"name": "Sprite (2L)", "price": 3.99},
        "water": {"name": "Bottled Water", "price": 1.99},
        "orange_juice": {"name": "Orange Juice", "price": 3.49}
    }
}


def get_menu():
    """Get the complete pizza menu."""
    return {
        "restaurant": "Zavier's Pizza",
        "menu": PIZZA_MENU,
        "message": "Here's our complete menu with all available items, sizes, and prices."
    }


def place_pizza_order(customer_name, phone, order_type, address, items):
    """Place a complete pizza order."""
    # Validate required fields
    if not customer_name or not phone:
        return {"error": "Customer name and phone number are required"}
    
    if order_type not in ["pickup", "delivery"]:
        return {"error": "Order type must be 'pickup' or 'delivery'"}
    
    if order_type == "delivery" and not address:
        return {"error": "Address is required for delivery orders"}
    
    if not items or len(items) == 0:
        return {"error": "At least one item must be ordered"}
    
    # Process and validate items
    processed_items = []
    total_price = 0.0
    
    for item in items:
        try:
            item_result = _process_order_item(item)
            if "error" in item_result:
                return item_result
            processed_items.append(item_result["item"])
            total_price += item_result["price"]
        except Exception as e:
            return {"error": f"Error processing item: {str(e)}"}
    
    # Create order
    order_id = ORDERS_DB["next_id"]
    ORDERS_DB["next_id"] += 1
    
    order = {
        "id": order_id,
        "customer_name": customer_name,
        "phone": phone,
        "order_type": order_type,
        "address": address if order_type == "delivery" else None,
        "items": processed_items,
        "total_price": round(total_price, 2),
        "status": "confirmed",
        "estimated_time": "25-35 minutes" if order_type == "pickup" else "35-45 minutes"
    }
    
    ORDERS_DB["orders"][order_id] = order
    
    return {
        "order_id": order_id,
        "message": f"Order #{order_id} confirmed for {customer_name}",
        "order_type": order_type,
        "total_price": order["total_price"],
        "estimated_time": order["estimated_time"],
        "items_count": len(processed_items)
    }


def _process_order_item(item):
    """Process and validate a single order item."""
    item_type = item.get("type")
    quantity = item.get("quantity", 1)
    
    if quantity < 1:
        return {"error": "Quantity must be at least 1"}
    
    if item_type == "pizza":
        return _process_pizza_item(item, quantity)
    elif item_type == "side":
        return _process_side_item(item, quantity)
    elif item_type == "drink":
        return _process_drink_item(item, quantity)
    else:
        return {"error": f"Invalid item type: {item_type}"}


def _process_pizza_item(item, quantity):
    """Process a pizza order item."""
    pizza_name = item.get("name", "").lower()
    size = item.get("size", "").lower()
    toppings = item.get("toppings", [])
    
    # Validate size
    if size not in PIZZA_MENU["sizes"]:
        available_sizes = list(PIZZA_MENU["sizes"].keys())
        return {"error": f"Invalid size '{size}'. Available sizes: {', '.join(available_sizes)}"}
    
    base_price = PIZZA_MENU["sizes"][size]["base_price"]
    item_price = base_price
    
    # Handle specialty pizza or build-your-own
    if pizza_name in PIZZA_MENU["specialty_pizzas"]:
        specialty = PIZZA_MENU["specialty_pizzas"][pizza_name]
        display_name = f"{specialty['name']} ({PIZZA_MENU['sizes'][size]['name']})"
        final_toppings = specialty["toppings"].copy()
        
        # Add any extra toppings
        for topping in toppings:
            if topping not in final_toppings:
                topping_price = _get_topping_price(topping)
                if topping_price is None:
                    return {"error": f"Invalid topping: {topping}"}
                item_price += topping_price
                final_toppings.append(topping)
    
    elif pizza_name == "build_your_own" or pizza_name == "custom":
        display_name = f"Build Your Own ({PIZZA_MENU['sizes'][size]['name']})"
        final_toppings = []
        
        # Add toppings and calculate price
        for topping in toppings:
            topping_price = _get_topping_price(topping)
            if topping_price is None:
                return {"error": f"Invalid topping: {topping}"}
            item_price += topping_price
            final_toppings.append(topping)
    
    else:
        return {"error": f"Invalid pizza type: {pizza_name}"}
    
    total_price = item_price * quantity
    
    return {
        "item": {
            "type": "pizza",
            "name": display_name,
            "size": size,
            "toppings": final_toppings,
            "quantity": quantity,
            "unit_price": round(item_price, 2),
            "total_price": round(total_price, 2)
        },
        "price": total_price
    }


def _process_side_item(item, quantity):
    """Process a side order item."""
    side_name = item.get("name", "").lower()
    
    if side_name not in PIZZA_MENU["sides"]:
        available_sides = list(PIZZA_MENU["sides"].keys())
        return {"error": f"Invalid side: {side_name}. Available sides: {', '.join(available_sides)}"}
    
    side = PIZZA_MENU["sides"][side_name]
    total_price = side["price"] * quantity
    
    return {
        "item": {
            "type": "side",
            "name": side["name"],
            "quantity": quantity,
            "unit_price": side["price"],
            "total_price": round(total_price, 2)
        },
        "price": total_price
    }


def _process_drink_item(item, quantity):
    """Process a drink order item."""
    drink_name = item.get("name", "").lower()
    
    if drink_name not in PIZZA_MENU["drinks"]:
        available_drinks = list(PIZZA_MENU["drinks"].keys())
        return {"error": f"Invalid drink: {drink_name}. Available drinks: {', '.join(available_drinks)}"}
    
    drink = PIZZA_MENU["drinks"][drink_name]
    total_price = drink["price"] * quantity
    
    return {
        "item": {
            "type": "drink",
            "name": drink["name"],
            "quantity": quantity,
            "unit_price": drink["price"],
            "total_price": round(total_price, 2)
        },
        "price": total_price
    }


def _normalize_topping_name(topping_name):
    """Normalize topping names to match menu keys."""
    # Create a mapping of display names and variations to menu keys
    topping_aliases = {
        "grilled chicken": "chicken",
        "italian sausage": "sausage",
        "bell peppers": "bell_peppers",
        "black olives": "olives",
        "fresh tomatoes": "tomatoes",
        "fresh basil": "basil",
        "jalapeños": "jalapenos",
        "jalapenos": "jalapenos",
        "extra mozzarella": "mozzarella"
    }
    
    # Convert to lowercase for comparison
    normalized = topping_name.lower().strip()
    
    # Check if it's an alias
    if normalized in topping_aliases:
        return topping_aliases[normalized]
    
    # Return as-is if no alias found
    return normalized


def _get_topping_price(topping_name):
    """Get the price for a topping."""
    # Normalize the topping name first
    normalized_name = _normalize_topping_name(topping_name)
    
    # Search through all topping categories
    for category in PIZZA_MENU["toppings"].values():
        if normalized_name in category:
            return category[normalized_name]["price"]
    
    # Also check if the original name matches any display names
    for category in PIZZA_MENU["toppings"].values():
        for key, topping_info in category.items():
            if topping_info["name"].lower() == topping_name.lower():
                return topping_info["price"]
    
    return None


def lookup_order(order_id):
    """Look up a pizza order."""
    try:
        order_id_int = int(order_id)
    except ValueError:
        return {"error": "Order ID must be a number"}
    
    order = ORDERS_DB["orders"].get(order_id_int)
    if order:
        return {
            "order_id": order_id,
            "customer_name": order["customer_name"],
            "phone": order["phone"],
            "order_type": order["order_type"],
            "address": order.get("address"),
            "items": order["items"],
            "total_price": order["total_price"],
            "status": order["status"],
            "estimated_time": order["estimated_time"]
        }
    return {"error": f"Order #{order_id} not found"}


# Function mapping dictionary
FUNCTION_MAP = {
    'get_menu': get_menu,
    'place_pizza_order': place_pizza_order,
    'lookup_order': lookup_order
}