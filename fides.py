#!/usr/bin/env python3
"""
Functions for interacting with Fides API to fetch data categories.
Only keeping fides_key and description fields.
"""

import requests
import json
import os
import sys
from typing import Dict, List, Any


def fetch_categories() -> List[Dict[str, Any]]:
    """
    Fetch Fides data categories from the Mozilla data privacy mapping API.
    
    Uses the FIDES_API_TOKEN environment variable for authorization.
    
    Returns:
        List of dictionaries containing Fides categories.
    
    Raises:
        Exception: If the API request fails or if FIDES_API_TOKEN is not set.
    """
    url = "https://prod.data-privacy-mapping.prod.dataservices.mozgcp.net/api/v1/data_category"
    
    # Get the access token from environment variable
    access_token = os.environ.get("FIDES_API_TOKEN")
    if not access_token:
        raise Exception("FIDES_API_TOKEN environment variable is not set")
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to fetch Fides categories: {e}")


def extract_simplified_categories(categories: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extract only the fides_key and description from each category.
    
    Args:
        categories: Full category data from API
        
    Returns:
        List of simplified dictionaries with only fides_key and description
    """
    return [{'fides_key': c['fides_key'], 'description': c['description']} for c in categories]


def save_categories_to_file(categories: List[Dict[str, str]], filename: str = "fides_categories.txt") -> None:
    """
    Save Fides categories to a JSON file.
    
    Args:
        categories: List of simplified category dictionaries to save
        filename: Path to save the categories to (default: fides_categories.txt)
    """
    with open(filename, 'w') as f:
        json.dump(categories, f, indent=2)
    print(f"Saved {len(categories)} categories to {filename}")


def load_categories_from_file(filename: str = "fides_categories.txt") -> List[Dict[str, str]]:
    """
    Load Fides categories from a JSON file.
    
    Args:
        filename: Path to load the categories from (default: fides_categories.txt)
        
    Returns:
        List of category dictionaries
    
    Raises:
        Exception: If the file doesn't exist or contains invalid JSON
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        raise Exception(f"File not found: {filename}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in file: {filename}")


if __name__ == "__main__":
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--load":
        try:
            # Load from file instead of API
            filename = sys.argv[2] if len(sys.argv) > 2 else "fides_categories.txt"
            categories = load_categories_from_file(filename)
            print(f"Successfully loaded {len(categories)} categories from {filename}")
        except Exception as e:
            print(f"Error loading categories: {e}")
            sys.exit(1)
    else:
        try:
            # Fetch from API
            raw_categories = fetch_categories()
            
            # Extract only fides_key and description
            categories = extract_simplified_categories(raw_categories)
            
            print(f"Successfully fetched {len(categories)} Fides categories")
            save_categories_to_file(raw_categories)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Print statistics
    print(f"\nTotal categories: {len(categories)}")
    
    # Print some examples
    if categories:
        print("\nExample categories:")
        for i, category in enumerate(categories[:3]):
            print(f"{i+1}. {category['fides_key']}")
            print(f"   Description: {category['description']}")