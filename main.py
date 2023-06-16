from PIL import Image, ImageDraw, ImageFont
import requests
import os
from dotenv import load_dotenv
import json


def configure():
    load_dotenv()


def writeTitleIntoImage(file, text):
    # Open the image file
    img = Image.open(file)
    draw = ImageDraw.Draw(img)
    textToWrite = text

    myFont = ImageFont.truetype('FreeMono.ttf', 40)

    # Get the dimensions of the image
    img_width, img_height = img.size

    # Set the maximum width and height for the text
    max_width = img_width - 20
    # max_height = img_height - 400

    lines = []
    words = textToWrite.split(' ')
    current_line = words[0]
    for word in words[1:]:
        # Check if adding the current word to the current line exceeds the maximum width
        if draw.textlength(current_line + ' ' + word, font=myFont) <= max_width:
            current_line += ' ' + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)

    # Calculate the total height of the text
    total_height = draw.multiline_textbbox((0, 0), '\n'.join(lines), font=myFont)[3] - draw.multiline_textbbox((0, 0), '\n'.join(lines), font=myFont)[1]

    # Calculate the coordinates for the text and the rectangle background
    text_x = 10
    text_y = img_height - total_height - 15
    rectangle_coords = [(text_x - 10, text_y - 5), (text_x + max_width + 10, text_y + total_height + 20)]

    # Draw the white rectangle background
    draw.rectangle(rectangle_coords, fill='white')

    # Draw each line of text
    for line in lines:
        line_bbox = draw.textbbox((0, 0), line, font=myFont)
        # line_width = line_bbox[2] - line_bbox[0]
        line_height = line_bbox[3] - line_bbox[1]
        draw.text((text_x, text_y), line, font=myFont, fill='black')
        text_y += line_height

    # Save the modified image
    img.save(file)


def download_image(url, file_path):
    response_img = requests.get(url)
    if response_img.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response_img.content)
        print("Image downloaded successfully:", file_path)
    else:
        print("Failed to download image. Status code:", response_img.status_code)


def main():
    configure()

    category = input("What kind of art or category are you interested in exploring at the museum?\n")

    req = requests.get(f"https://api.vam.ac.uk/v2/objects/search?q={category}")
    response = req.json()
    data_res = json.dumps(response['records'])
    # print(json.dumps(response['records'], indent=2))

    data = json.loads(data_res)

    iiif_presentation_urls = []
    img_sequences = []

    for item in data:
        if "_iiif_presentation_url" in item["_images"]:
            iiif_presentation_urls.append(item["_images"]["_iiif_presentation_url"])

    # print(iiif_presentation_urls)

    for iiif_presentation_url in iiif_presentation_urls:
        canvases = []
        if iiif_presentation_url is None:
            continue
        else:
            url_req = requests.get(url=iiif_presentation_url)
            # print(iiif_presentation_url)
            url_response = url_req.json()
            url_res = json.dumps(url_response)

            url_data = json.loads(url_res)
            text_on_image = url_data["description"]
            label_1 = url_data["label"]

            img_sequence = url_data["sequences"][0]
            canvases = img_sequence["canvases"]
            for canvas in canvases:
                label_2 = canvas["label"]
                image = canvas["images"][0]
                url_img = image["resource"]["@id"]

                filename = label_1 + " " + label_2 + ".jpg"

                # Download the image from the provided URL
                download_image(url_img, filename)

                # Write the long title into the downloaded image
                writeTitleIntoImage(filename, text_on_image)


main()
