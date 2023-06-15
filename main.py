from PIL import Image, ImageDraw, ImageFont
import requests
import os
from dotenv import load_dotenv


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
    text_y = img_height - total_height - 200
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

    # Set the URL for the API endpoint
    URL = "https://www.rijksmuseum.nl/api/nl/collection"

    parameters = {
        "key": os.getenv('Key'),
        "q": "photograph"
    }

    # Send a GET request to the API endpoint with the specified parameters
    response = requests.get(url=URL, params=parameters)

    # Convert the response to JSON format
    data_json = response.json()

    # Extract the art objects from the JSON data
    art_objects = data_json["artObjects"]

    # Process each art object
    for art_object in art_objects:
        object_number = art_object["objectNumber"]
        URL_Object = f"https://www.rijksmuseum.nl/api/nl/collection/{object_number}?key={os.getenv('Key')}"

        # Send a GET request to the individual art object URL
        response_object = requests.get(url=URL_Object)
        response_object_json = response_object.json()

        # Check if the art object has a web image
        if art_object["webImage"] is None:
            # Skip processing if no web image is available
            continue
        else:
            img_url = art_object["webImage"]["url"]

        title = art_object["title"]
        long_title = art_object["longTitle"]

        filename = title + ".jpg"

        # Download the image from the provided URL
        download_image(img_url, filename)

        # Write the long title into the downloaded image
        writeTitleIntoImage(filename, long_title)


main()
