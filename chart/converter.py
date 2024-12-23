from PIL import Image, ImageDraw, ImageFont

def create_final_image(text, accountid_str):
    gradient_image = Image.open("./chart/Gradient-holistic-health_2k.png")
    polar_chart_image = Image.open(accountid_str)

    gradient_image_resized = gradient_image.resize(polar_chart_image.size)

    final_image = Image.alpha_composite(gradient_image_resized.convert("RGBA"), polar_chart_image.convert("RGBA"))

    final_image.save(accountid_str)

    white_circle_image = Image.open("./chart/white_circle.png")

    white_circle_image_resized = white_circle_image.resize(final_image.size)

    final_image_with_white_center = Image.alpha_composite(final_image.convert("RGBA"), white_circle_image_resized.convert("RGBA"))

    final_image_with_white_center.save(accountid_str)

    image = final_image_with_white_center

    font_path = './chart/TT-Norms-Pro-Medium.ttf'
    font = ImageFont.truetype(font_path, 110)

    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

    x_position = (image_width - text_width) // 2
    y_position = (image_height - text_height) // 2 - 30

    draw.text((x_position, y_position), text, font=font, fill=(0, 0, 0))

    output_path = accountid_str
    image.save(output_path)
    #image.show()
