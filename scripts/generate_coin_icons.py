from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(name, symbol_text, color, filename):
    # Settings
    SIZE = 300
    BG_COLOR = (14, 16, 25)  # Dark #0e1019
    
    img = Image.new('RGB', (SIZE, SIZE), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Draw simple grid background
    grid_size = 30
    grid_color = (0, 40, 0)
    for i in range(0, SIZE, grid_size):
        draw.line([(i, 0), (i, SIZE)], fill=grid_color, width=1)
        draw.line([(0, i), (SIZE, i)], fill=grid_color, width=1)
        
    # Draw Outer Glow/Circle (Simulated)
    center = SIZE // 2
    radius = 100
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=color, width=3)
    
    # Try to load a font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
        
    try:
        # Load a very large font for the symbol
        font = ImageFont.truetype(font_path, 150)
    except:
        font = ImageFont.load_default()

    # Draw Text
    bbox = draw.textbbox((0, 0), symbol_text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x = (SIZE - text_w) / 2
    y = (SIZE - text_h) / 2 - 15 # slight vertical adjustment
    
    # Shadow
    draw.text((x+4, y+4), symbol_text, font=font, fill=(0, 50, 0))
    # Main Text
    draw.text((x, y), symbol_text, font=font, fill=color)
    
    # Label at bottom
    try:
        small_font = ImageFont.truetype(font_path, 30)
    except:
        small_font = ImageFont.load_default()
        
    label_bbox = draw.textbbox((0, 0), name, font=small_font)
    label_w = label_bbox[2] - label_bbox[0]
    draw.text(((SIZE - label_w) / 2, SIZE - 50), name, font=small_font, fill=(255, 255, 255))

    img.save(filename)
    print(f"Generated {filename}")

def create_eth_icon(filename):
    # Custom draw for ETH since it's a shape
    SIZE = 300
    BG_COLOR = (14, 16, 25)
    COLOR = (0, 255, 255) # Cyan
    
    img = Image.new('RGB', (SIZE, SIZE), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Grid
    grid_size = 30
    grid_color = (0, 40, 0)
    for i in range(0, SIZE, grid_size):
        draw.line([(i, 0), (i, SIZE)], fill=grid_color, width=1)
        draw.line([(0, i), (SIZE, i)], fill=grid_color, width=1)
        
    # Draw Circle
    center = SIZE // 2
    radius = 100
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], outline=COLOR, width=3)

    # Draw Diamond Shape (ETH logo simplified)
    # Top point
    top = (center, center - 70)
    # Middle points
    left = (center - 40, center)
    right = (center + 40, center)
    # Bottom point
    bottom = (center, center + 70)
    
    # Top triangle
    draw.polygon([top, left, right], outline=COLOR, fill=(0, 100, 100))
    # Bottom triangle
    draw.polygon([left, bottom, right], outline=COLOR, fill=(0, 80, 80))
    
    # Label
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    if not os.path.exists(font_path):
        font_path = "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
    try:
        small_font = ImageFont.truetype(font_path, 30)
    except:
        small_font = ImageFont.load_default()
        
    name = "ETHEREUM"
    label_bbox = draw.textbbox((0, 0), name, font=small_font)
    label_w = label_bbox[2] - label_bbox[0]
    draw.text(((SIZE - label_w) / 2, SIZE - 50), name, font=small_font, fill=(255, 255, 255))

    img.save(filename)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_icon("BITCOIN", "B", (255, 165, 0), "assets/icon_btc.png") # Orange
    create_eth_icon("assets/icon_eth.png")
