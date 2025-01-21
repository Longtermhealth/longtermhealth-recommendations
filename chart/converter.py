from PIL import Image, ImageDraw, ImageFont

def create_final_image(text, accountid_str):

    gradient_image_path = "./chart/background_graph.png"
    white_circle_path = "./chart/white_circle.png"
    outlines_path = "./chart/foreground_lines.png"

    try:
        gradient_image = Image.open(gradient_image_path).convert("RGBA")
    except IOError:
        print(f"Gradient image not found at {gradient_image_path}.")
        return

    try:
        polar_chart_image = Image.open(accountid_str).convert("RGBA")
    except IOError:
        print(f"Polar chart image not found at {accountid_str}.")
        return

    gradient_resized = gradient_image.resize(polar_chart_image.size)
    print(f"Gradient image resized to {gradient_resized.size}.")

    combined_image = Image.alpha_composite(gradient_resized, polar_chart_image)
    print("Combined Gradient and Polar Chart.")

    try:
        outlines_image = Image.open(outlines_path).convert("RGBA")
    except IOError:
        print(f"Outlines image not found at {outlines_path}. Skipping overlay.")
    else:
        outlines_resized = outlines_image.resize(combined_image.size)
        print(f"Outlines image resized to {outlines_resized.size}.")

        combined_image = Image.alpha_composite(combined_image, outlines_resized)
        print("Overlayed Outlines on Combined Image.")

    try:
        white_circle_image = Image.open(white_circle_path).convert("RGBA")
    except IOError:
        print(f"White circle image not found at {white_circle_path}. Skipping overlay.")
    else:
        white_circle_resized = white_circle_image.resize(combined_image.size)
        print(f"White circle image resized to {white_circle_resized.size}.")

        combined_image = Image.alpha_composite(combined_image, white_circle_resized)
        print("Overlayed White Circle on Combined Image.")

    font_path = './chart/TT-Norms-Pro-Medium.ttf'
    font_size = 110

    try:
        font = ImageFont.truetype(font_path, font_size)
        print(f"Loaded custom font from {font_path} with size {font_size}.")
    except IOError:
        print(f"Font file not found at {font_path}. Using default font.")
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(combined_image)
    image_width, image_height = combined_image.size

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x_position = (image_width - text_width) // 2
    y_position = (image_height - text_height) // 2 - 30

    draw.text((x_position, y_position), text, font=font, fill=(0, 0, 0))
    print(f"Added text '{text}' at position ({x_position}, {y_position}).")

    try:
        combined_image.save(accountid_str)
        print(f"Final image saved at {accountid_str}.")
    except IOError as e:
        print(f"Failed to save final image at {accountid_str}: {e}")
