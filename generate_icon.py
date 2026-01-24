#!/usr/bin/env python3
"""
Generate addon icon - Robot mascot biting network cable
"""
from PIL import Image, ImageDraw

def create_robot_icon(size=256):
    """Create robot icon with network cable"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Scale factor
    s = size / 100

    # Colors
    body_color = (102, 126, 234, 255)  # #667eea
    head_color = (118, 75, 162, 255)   # #764ba2
    white = (255, 255, 255, 255)
    gold = (255, 215, 0, 255)
    gray = (102, 102, 102, 255)
    green = (0, 255, 0, 200)
    black = (51, 51, 51, 255)

    # Robot Body
    draw.rounded_rectangle(
        [(25*s, 35*s), (75*s, 80*s)],
        radius=5*s,
        fill=body_color,
        outline=white,
        width=int(2*s)
    )

    # Robot Head
    draw.rounded_rectangle(
        [(30*s, 15*s), (70*s, 40*s)],
        radius=3*s,
        fill=head_color,
        outline=white,
        width=int(2*s)
    )

    # Antenna
    draw.line([(50*s, 15*s), (50*s, 8*s)], fill=white, width=int(2*s))
    draw.ellipse([(47*s, 3*s), (53*s, 9*s)], fill=gold)

    # Eyes (white background)
    draw.ellipse([(36*s, 21*s), (44*s, 29*s)], fill=white)
    draw.ellipse([(56*s, 21*s), (64*s, 29*s)], fill=white)
    # Pupils
    draw.ellipse([(38*s, 23*s), (42*s, 27*s)], fill=black)
    draw.ellipse([(58*s, 23*s), (62*s, 27*s)], fill=black)

    # Network Cable (curved line)
    # Simplified as line for PNG
    draw.line([(50*s, 38*s), (70*s, 38*s)], fill=gold, width=int(3*s))
    # Plug
    draw.rectangle([(70*s, 36*s), (76*s, 40*s)], fill=gray)

    # Arms
    draw.rounded_rectangle(
        [(15*s, 45*s), (27*s, 51*s)],
        radius=2*s,
        fill=body_color,
        outline=white,
        width=int(1.5*s)
    )
    draw.rounded_rectangle(
        [(73*s, 45*s), (85*s, 51*s)],
        radius=2*s,
        fill=body_color,
        outline=white,
        width=int(1.5*s)
    )

    # Legs
    draw.rounded_rectangle(
        [(32*s, 78*s), (42*s, 93*s)],
        radius=2*s,
        fill=head_color,
        outline=white,
        width=int(1.5*s)
    )
    draw.rounded_rectangle(
        [(58*s, 78*s), (68*s, 93*s)],
        radius=2*s,
        fill=head_color,
        outline=white,
        width=int(1.5*s)
    )

    # Panel lights (3 green dots)
    draw.ellipse([(37.5*s, 52.5*s), (42.5*s, 57.5*s)], fill=green)
    draw.ellipse([(47.5*s, 52.5*s), (52.5*s, 57.5*s)], fill=green)
    draw.ellipse([(57.5*s, 52.5*s), (62.5*s, 57.5*s)], fill=green)

    return img

if __name__ == '__main__':
    # Create 256x256 icon
    icon = create_robot_icon(256)
    icon.save('/home/user/Addon/icon.png')
    print("✓ Created icon.png (256x256)")

    # Create smaller version for favicon
    icon_small = create_robot_icon(128)
    icon_small.save('/home/user/Addon/app/static/favicon.png')
    icon_small.save('/home/user/Addon/modbus/app/static/favicon.png')
    print("✓ Created favicon.png (128x128)")

    # Create 32x32 favicon.ico
    icon_ico = create_robot_icon(32)
    icon_ico.save('/home/user/Addon/app/static/favicon.ico', format='ICO')
    icon_ico.save('/home/user/Addon/modbus/app/static/favicon.ico', format='ICO')
    print("✓ Created favicon.ico (32x32)")

    print("\n✅ All icons generated successfully!")
