#!/usr/bin/env python3
"""
Test script to demonstrate Phase 4 functionality with the specified test case:
- Location: Bellandur
- Budget: 2000
- Rating: 4.0
- Get top 5 restaurants from LLM
"""

import json
import os
import sys
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from zomato_rec.phase4.prompting import build_system_prompt, build_user_prompt
from zomato_rec.phase4.recommend import load_shortlist
from zomato_rec.phase2.models import UserPreferences, BudgetRange


def main():
    print("=== Phase 4 Test Demo ===")
    print("Input: Bellandur, Budget 2000, Rating 4.0")
    print("Expected: Top 5 restaurants from LLM\n")
    
    # Test preferences - create proper UserPreferences object
    test_prefs = UserPreferences(
        location="Bellandur",
        budget=BudgetRange(min=0, max=2000),
        minimum_rating=4.0,
        cuisines=[],
        additional_preferences=None
    )
    
    # Check if shortlist exists
    shortlist_path = "storage/shortlist.json"
    if not os.path.exists(shortlist_path):
        print(f"ERROR: Shortlist file not found: {shortlist_path}")
        print("Please run Phase 3 first to generate the shortlist.")
        return 1
    
    try:
        # Load shortlist
        print("Loading shortlist...")
        candidates = load_shortlist(shortlist_path)
        print(f"Loaded {len(candidates)} candidates from shortlist")
        
        # Filter candidates for Bellandur (approximate match)
        bellandur_candidates = [
            c for c in candidates 
            if c.get("city", "").lower().find("bellandur") != -1 or 
               c.get("restaurant_name", "").lower().find("bellandur") != -1
        ]
        
        print(f"Found {len(bellandur_candidates)} candidates in/near Bellandur")
        
        # Show sample candidates
        if bellandur_candidates:
            print("\nSample candidates:")
            for i, c in enumerate(bellandur_candidates[:3]):
                print(f"  {i+1}. {c.get('restaurant_name', 'Unknown')} - {c.get('city', 'Unknown')}")
                print(f"     Rating: {c.get('rating', 'N/A')}, Cost: {c.get('cost_estimate', 'N/A')}")
                print(f"     Cuisines: {c.get('cuisines', 'N/A')}")
        
        # Build prompts to show what would be sent to LLM
        print("\nBuilding prompts for LLM...")
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(test_prefs, bellandur_candidates[:20], top_k=5)
        
        print("\nSystem Prompt (first 200 chars):")
        print(f"   {system_prompt[:200]}...")
        
        print("\nUser Prompt (first 300 chars):")
        print(f"   {user_prompt[:300]}...")
        
        print(f"\nSummary:")
        print(f"   - Location: {test_prefs.location}")
        print(f"   - Budget: {test_prefs.budget}")
        print(f"   - Min Rating: {test_prefs.minimum_rating}")
        print(f"   - Candidates available: {len(bellandur_candidates)}")
        print(f"   - Requested top-k: 5")
        
        print(f"\nPhase 4 test setup complete!")
        print(f"To run actual LLM inference:")
        print(f"   1. Set GROQ_API_KEY in .env file")
        print(f"   2. Run: python -m zomato_rec.phase4.run --prefs test_preferences.json --top-k 5")
        
        return 0
        
    except Exception as e:
        print(f"ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
