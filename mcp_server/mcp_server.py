"""
MCP Server for Product Management
Provides tools for managing product data via FastMCP
"""

import json
import os
from pathlib import Path
from typing import Any
import logging

import mcp.server.fastmcp as mcp

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
server = mcp.FastMCP("product-server")

# Data storage
PRODUCTS_FILE = Path(__file__).parent.parent / "data" / "products.json"
products_data = []


def load_products() -> list[dict[str, Any]]:
    """Load products from JSON file."""
    global products_data
    if not products_data and PRODUCTS_FILE.exists():
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            products_data = json.load(f)
    return products_data


def save_products() -> None:
    """Save products to JSON file."""
    os.makedirs(PRODUCTS_FILE.parent, exist_ok=True)
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products_data, f, ensure_ascii=False, indent=2)


def get_next_product_id() -> int:
    """Get next available product ID."""
    if not products_data:
        return 1
    return max(p["id"] for p in products_data) + 1


@server.tool()
def list_products(category: str | None = None) -> dict[str, Any]:
    """
    Get list of all products, optionally filtered by category.
    
    Args:
        category: Optional product category to filter by
        
    Returns:
        Dictionary with products list and total count
    """
    products = load_products()
    
    if category:
        filtered = [p for p in products if p.get("category", "").lower() == category.lower()]
        return {
            "products": filtered,
            "total": len(filtered),
            "category": category
        }
    
    return {
        "products": products,
        "total": len(products)
    }


@server.tool()
def get_product(product_id: int) -> dict[str, Any]:
    """
    Get product details by ID.
    
    Args:
        product_id: The ID of the product to retrieve
        
    Returns:
        Product details
        
    Raises:
        ValueError: If product not found
    """
    products = load_products()
    
    for product in products:
        if product["id"] == product_id:
            return {
                "success": True,
                "product": product
            }
    
    raise ValueError(f"Product with ID {product_id} not found")


@server.tool()
def add_product(name: str, price: float, category: str, in_stock: bool = True) -> dict[str, Any]:
    """
    Add a new product to the inventory.
    
    Args:
        name: Product name
        price: Product price
        category: Product category
        in_stock: Whether the product is in stock (default: True)
        
    Returns:
        The newly created product with assigned ID
    """
    products = load_products()
    
    new_product = {
        "id": get_next_product_id(),
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock
    }
    
    products.append(new_product)
    products_data.clear()
    products_data.extend(products)
    save_products()
    
    logger.info(f"Added new product: {name} (ID: {new_product['id']})")
    
    return {
        "success": True,
        "product": new_product
    }


@server.tool()
def get_statistics() -> dict[str, Any]:
    """
    Get statistics about products in inventory.
    
    Returns:
        Dictionary with product statistics including count, average price, and categories
    """
    products = load_products()
    
    if not products:
        return {
            "total_products": 0,
            "average_price": 0,
            "in_stock_count": 0,
            "categories": [],
            "price_range": {"min": 0, "max": 0}
        }
    
    prices = [p["price"] for p in products]
    categories = list(set(p.get("category", "Unknown") for p in products))
    in_stock_count = sum(1 for p in products if p.get("in_stock", False))
    
    return {
        "total_products": len(products),
        "average_price": sum(prices) / len(prices),
        "in_stock_count": in_stock_count,
        "out_of_stock_count": len(products) - in_stock_count,
        "categories": categories,
        "price_range": {
            "min": min(prices),
            "max": max(prices)
        }
    }


if __name__ == "__main__":
    # Load initial data
    load_products()
    logger.info(f"Loaded {len(products_data)} products")
    
    # Start the server
    server.run(port=3001)
