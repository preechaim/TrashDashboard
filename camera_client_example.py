"""
Example Camera Client
This script demonstrates how to send images to the dashboard's camera feed.
Any camera server can use this approach to broadcast images to all connected users.

Usage:
    python camera_client_example.py <image_file>
    
Example:
    python camera_client_example.py photo.jpg
"""

import requests
import base64
import sys
from pathlib import Path

# Dashboard API endpoint
DASHBOARD_URL = "http://localhost:5000/api/camera-feed"

def send_image_from_file(image_path):
    """
    Send an image file to the dashboard
    
    Args:
        image_path: Path to the image file (JPG, JPEG, or PNG)
    """
    try:
        # Read the image file
        with open(image_path, 'rb') as image_file:
            # Encode to base64
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
        # Determine image type from extension
        ext = Path(image_path).suffix.lower()
        mime_type = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
        
        # Create data URI
        data_uri = f"data:{mime_type};base64,{image_data}"
        
        # Send to dashboard
        response = requests.post(
            DASHBOARD_URL,
            json={'image': data_uri},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Image sent successfully at {result['timestamp']}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error sending image: {e}")
        return False

def send_base64_directly(base64_string):
    """
    Send a base64-encoded image directly
    
    Args:
        base64_string: Base64-encoded image string (with or without data URI prefix)
    """
    try:
        # Ensure proper format
        if not base64_string.startswith('data:image'):
            base64_string = f"data:image/jpeg;base64,{base64_string}"
        
        response = requests.post(
            DASHBOARD_URL,
            json={'image': base64_string},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Image sent successfully at {result['timestamp']}")
            return True
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error sending image: {e}")
        return False

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Camera Client - Send image to dashboard")
        print("=" * 50)
        print("\nUsage: python camera_client_example.py <image_file>")
        print("\nExample:")
        print("  python camera_client_example.py photo.jpg")
        print("  python camera_client_example.py C:\\path\\to\\image.png")
        sys.exit(1)
    
    image_file = sys.argv[1]
    
    # Check if file exists
    if not Path(image_file).exists():
        print(f"✗ Error: File '{image_file}' not found")
        sys.exit(1)
    
    print(f"Sending image: {image_file}")
    print("-" * 50)
    
    if send_image_from_file(image_file):
        print("\n✓ Image successfully broadcast to all dashboard viewers!")
        sys.exit(0)
    else:
        print("\n✗ Failed to send image")
        sys.exit(1)
