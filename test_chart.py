"""
Quick test script to populate database with sample data for chart visualization
"""
import requests
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:5000"

def add_sample_data():
    """Add sample data for the past 7 days"""
    print("Adding sample data for daily capacity chart...")
    
    # Simulate data for the past 7 days
    for day_offset in range(7, 0, -1):
        date = datetime.now() - timedelta(days=day_offset)
        print(f"\nDay: {date.strftime('%Y-%m-%d')}")
        
        # Add normal waste (2-4 entries per day)
        for i in range(3):
            data = {
                "waste_type": "normal",
                "volume": 10 + (i * 5),
                "weight": 5 + (i * 2)
            }
            response = requests.post(f"{BASE_URL}/api/trash", json=data)
            if response.status_code == 201:
                print(f"  ✓ Added normal waste: {data['volume']}L, {data['weight']}kg")
            time.sleep(0.1)
        
        # Add recyclable waste (2-3 entries per day)
        for i in range(2):
            data = {
                "waste_type": "recycle",
                "volume": 8 + (i * 4),
                "weight": 3 + (i * 1.5)
            }
            response = requests.post(f"{BASE_URL}/api/trash", json=data)
            if response.status_code == 201:
                print(f"  ✓ Added recyclable waste: {data['volume']}L, {data['weight']}kg")
            time.sleep(0.1)
        
        # Empty bins every 2-3 days
        if day_offset % 2 == 0:
            response = requests.post(f"{BASE_URL}/api/reset", json={"waste_type": "both"})
            if response.status_code == 200:
                print(f"  🧹 Emptied both bins (CO₂ calculated)")
            time.sleep(0.1)
    
    print("\n✅ Sample data added successfully!")
    print(f"📊 View the dashboard at: {BASE_URL}")

if __name__ == "__main__":
    print("=" * 60)
    print("Smart Bin Dashboard - Chart Data Generator")
    print("=" * 60)
    print(f"\nMake sure the Flask app is running at {BASE_URL}")
    input("Press Enter to continue...")
    
    try:
        add_sample_data()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print(f"   Make sure Flask is running: python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
