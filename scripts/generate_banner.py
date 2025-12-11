from PIL import Image, ImageDraw, ImageFont
import os
import random

def create_banner():
    # Settings
    WIDTH = 1280
    HEIGHT = 640
    BG_COLOR = (15, 17, 26)  # Dark #0f111a
    ACCENT_COLOR = (0, 255, 0) # Neon Green
    GRID_COLOR = (0, 60, 0) # Dark Green
    TEXT_COLOR = (255, 255, 255)
    
    # Create canvas
    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 1. Draw Grid
    grid_size = 40
    for x in range(0, WIDTH, grid_size):
        draw.line([(x, 0), (x, HEIGHT)], fill=GRID_COLOR, width=1)
    for y in range(0, HEIGHT, grid_size):
        draw.line([(0, y), (WIDTH, y)], fill=GRID_COLOR, width=1)
        
    # 2. Draw "Matrix" rain effect (subtle)
    for _ in range(50):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        length = random.randint(10, 50)
        draw.line([(x, y), (x, y+length)], fill=(0, 100, 0), width=2)

    # 3. Load Fonts
    # Try to find a system font, fallback to default if necessary
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
    if not os.path.exists(font_path):
        # Fallback for common linux paths
        font_path = "/usr/share/fonts/TTF/DejaVuSansMono-Bold.ttf"
    
    try:
        title_font = ImageFont.truetype(font_path, 100)
        subtitle_font = ImageFont.truetype(font_path, 40)
        small_font = ImageFont.truetype(font_path, 25)
    except Exception:
        print("Warning: Custom font not found. Using default.")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # 4. Draw Main Text
    title_text = "TerminalCoin"
    
    # Get bounding box [left, top, right, bottom]
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    x_pos = (WIDTH - text_w) / 2
    y_pos = (HEIGHT - text_h) / 2 - 50
    
    # Text Shadow (Glow effect)
    draw.text((x_pos+4, y_pos+4), title_text, font=title_font, fill=(0, 100, 0))
    draw.text((x_pos, y_pos), title_text, font=title_font, fill=ACCENT_COLOR)
    
    # 5. Draw Subtitle
    sub_text = "The Crypto Dashboard for the Sovereign Developer"
    bbox_sub = draw.textbbox((0, 0), sub_text, font=subtitle_font)
    sub_w = bbox_sub[2] - bbox_sub[0]
    
    draw.text(((WIDTH - sub_w) / 2, y_pos + text_h + 20), sub_text, font=subtitle_font, fill=(0, 255, 255))

    # 6. Draw UI Elements (Fake Terminal Window)
    # Border
    border_margin = 20
    draw.rectangle(
        [(border_margin, border_margin), (WIDTH - border_margin, HEIGHT - border_margin)],
        outline=ACCENT_COLOR,
        width=3
    )
    
    # Top Bar
    draw.rectangle(
        [(border_margin, border_margin), (WIDTH - border_margin, border_margin + 40)],
        fill=GRID_COLOR,
        outline=ACCENT_COLOR
    )
    # Buttons
    draw.ellipse([(40, 35), (55, 50)], fill=(255, 95, 86)) # Red
    draw.ellipse([(70, 35), (85, 50)], fill=(255, 189, 46)) # Yellow
    draw.ellipse([(100, 35), (115, 50)], fill=(39, 201, 63)) # Green
    
    draw.text((WIDTH - 250, 30), "user@linux:~/TerminalCoin", font=small_font, fill=TEXT_COLOR)

    # Save
    output_path = "assets/banner.png"
    img.save(output_path)
    print(f"Banner generated successfully: {output_path}")

if __name__ == "__main__":
    create_banner()
