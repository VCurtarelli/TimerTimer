from PIL import Image, ImageDraw
import base64


COLOR_BG = (30, 30, 30, 0)
fill  = "#202020"
green = "#5CB85C"
red   = "#D9534F"
blue  = "#02DDD8"
# 1. Create a 256x256 image with a rounded dark background
size = (256, 256)
img = Image.new("RGBA", size, COLOR_BG)
draw = ImageDraw.Draw(img)

# 2. Draw border frame
draw.rounded_rectangle((12., 12., 244., 244.), radius=32, outline="#444444", width=6, fill=fill)


# 3. Draw Stepped Blue Connecting Line (with two 90º turns)
# Segment 1: Upper horizontal line from green notch to midpoint
draw.line([(106, 125), (133, 125)], fill=blue, width=12)
draw.line([(127, 120), (127, 160)], fill=blue, width=12)
draw.line([(122, 155), (148, 155)], fill=blue, width=12)

lw = 20
# 4. Draw Left "T" Pulse (Green - High Notch at y=125)
draw.line([(40, 60), (115, 60)], fill=green, width=lw)  # Top bar
draw.line([(77, 60), (77, 190)], fill=green, width=lw)  # Vertical stem
draw.line([(77, 125), (105, 125)], fill=green, width=lw)  # Notch (Right)

# 5. Draw Right "T" Pulse (Red - Low Notch at y=155)
draw.line([(140, 60), (215, 60)], fill=red, width=lw)  # Top bar
draw.line([(177, 60), (177, 190)], fill=red, width=lw)  # Vertical stem
draw.line([(149, 155), (177, 155)], fill=red, width=lw)  # Notch (Left)

# 6. Save as PNG and ICO
img.save("app_icon.png")
img.save("app_icon.ico", format="ICO", sizes=[(16, 16), (32, 32), (64, 64), (128, 128), (256, 256)])

print("Saved app_icon.png and app_icon.ico successfully!")


with open("app_icon.png", "rb") as f:
    icon_b64 = base64.b64encode(f.read()).decode("utf-8")
    print(f'ICON_DATA = "{icon_b64}"')