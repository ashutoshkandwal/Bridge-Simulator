"""
Script to create a sample chart image for ECDIS display.
This creates a simple Gibraltar Strait chart that can be used for testing.
Place the generated image in bridge_sim/areas/ folder as 'gibraltar.png'
"""

import os
from PIL import Image, ImageDraw, ImageFont

def create_gibraltar_chart():
    """Create a simple Gibraltar Strait chart"""
    
    # Create image (900x598 pixels to match ECDIS view)
    width, height = 900, 598
    img = Image.new('RGB', (width, height), color=(5, 30, 40))  # Water background
    draw = ImageDraw.Draw(img, 'RGBA')
    
    # Coordinates mapping (simplified)
    # Chart bounds: 36.55°N to 35.75°N, 5.90°W to 4.90°W
    # For 900x598 display
    
    def ll_to_xy(lat, lon):
        """Convert lat/lon to pixel coordinates"""
        latN, lonW = 36.55, -5.90
        latS, lonE = 35.75, -4.90
        u = (lon - lonW) / (lonE - lonW)
        v = (latN - lat) / (latN - latS)
        x = int(u * width)
        y = int(v * height)
        return x, y
    
    # Draw land masses (simplified coastline)
    # Spain (north)
    spain_coast = [
        (36.50, -5.80), (36.45, -5.70), (36.40, -5.60), (36.38, -5.50),
        (36.35, -5.40), (36.30, -5.35), (36.25, -5.40), (36.20, -5.45)
    ]
    spain_pts = [ll_to_xy(lat, lon) for lat, lon in spain_coast]
    if len(spain_pts) > 1:
        draw.line(spain_pts, fill=(60, 60, 60), width=2)
    
    # Morocco (south)
    morocco_coast = [
        (35.90, -5.80), (35.85, -5.70), (35.80, -5.60), (35.82, -5.50),
        (35.88, -5.40), (35.95, -5.35), (36.00, -5.40), (36.05, -5.45)
    ]
    morocco_pts = [ll_to_xy(lat, lon) for lat, lon in morocco_coast]
    if len(morocco_pts) > 1:
        draw.line(morocco_pts, fill=(60, 60, 60), width=2)
    
    # Draw Gibraltar (point)
    gib_x, gib_y = ll_to_xy(36.15, -5.35)
    draw.ellipse([gib_x-8, gib_y-8, gib_x+8, gib_y+8], fill=(100, 100, 100))
    
    # Draw Tangier (point)
    tang_x, tang_y = ll_to_xy(35.78, -5.80)
    draw.ellipse([tang_x-6, tang_y-6, tang_x+6, tang_y+6], fill=(100, 100, 100))
    
    # Draw grid lines (lat/lon)
    grid_color = (40, 120, 180)
    
    # Latitude lines (every 0.1 degrees)
    for lat in [35.8, 35.9, 36.0, 36.1, 36.2, 36.3, 36.4, 36.5]:
        x1, y1 = ll_to_xy(lat, -5.90)
        x2, y2 = ll_to_xy(lat, -4.90)
        draw.line([(x1, y1), (x2, y2)], fill=grid_color, width=1)
    
    # Longitude lines (every 0.1 degrees)
    for lon in [-5.8, -5.7, -5.6, -5.5, -5.4, -5.3, -5.2, -5.1, -5.0]:
        x1, y1 = ll_to_xy(36.55, lon)
        x2, y2 = ll_to_xy(35.75, lon)
        draw.line([(x1, y1), (x2, y2)], fill=grid_color, width=1)
    
    # Draw title
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 10), "Gibraltar Strait Chart", fill=(200, 220, 230), font=font)
    
    # Save image
    output_path = os.path.join(os.path.dirname(__file__), 'bridge_sim', 'areas', 'gibraltar.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✓ Chart created: {output_path}")
    print(f"  Image size: {width}x{height}")
    print(f"  Place this in your ECDIS display by restarting the simulator")

if __name__ == "__main__":
    try:
        create_gibraltar_chart()
    except ImportError:
        print("ERROR: PIL (Pillow) not installed!")
        print("Install with: pip install Pillow")
