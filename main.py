from PIL import Image, ImageDraw, ImageFont
import requests
import json
import os
from dotenv import load_dotenv


def configure():
    load_dotenv()


def writeTitleIntoImage(file, text):
    # Opens the image file
    img = Image.open(file)
    draw = ImageDraw.Draw(img)
    textToWrite = text

    myFont = ImageFont.truetype('FreeMono.ttf', 40)

    # Get the bounding box of the text
    text_bbox = draw.textbbox((0, 0), textToWrite, font=myFont)

    # Extract the text width and height from the bounding box
    # text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    img_width, img_height = img.size

    if img_width < img_height:
        position = ((img_height - img_width) // 2, img_height - text_height - 200)
    else:
        position = ((img_width - img_height) // 2, img_height - text_height - 200)

    # draw.rectangle(
    #     [(position[0] - 10, position[1] - 5), (position[0] + text_width + 10, position[1] + text_height + 20)],
    #     fill='white')

    draw.text(position, textToWrite, font=myFont, fill='white')
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
    URL = "https://www.rijksmuseum.nl/api/nl/collection"

    parameters = {
        "key": os.getenv('Key'),
        "q": "photograph"
    }

    response = requests.get(url=URL, params=parameters)
    # print(response.text)
    data_json = response.json()
    # data = json.dumps(data_json, indent=2)
    # print(data)

    art_objects = data_json["artObjects"]
    for art_object in art_objects:
        object_number = art_object["objectNumber"]
        URL_Object = f"https://www.rijksmuseum.nl/api/nl/collection/{object_number}?key={os.getenv('Key')}"

        response_object = requests.get(url=URL_Object)
        response_object_json = response_object.json()
        information = response_object_json["artObject"]
        print(information)

        if art_object["webImage"] is None:
            continue
        else:
            img_url = art_object["webImage"]["url"]
            # print(img_url)

        title = art_object["title"]

        # filename = title + ".jpg"
        # download_image(img_url, filename)
        # writeTitleIntoImage(filename, long_title)


main()
