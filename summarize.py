import os
import io
import sys
import argparse
import base64
import requests
from PIL import Image

from prompt_gpt import prompt_gpt


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def summarize_screenshot(screenshot_path, output_folder_path):
    # Getting the base64 string
    base64_image = encode_image(screenshot_path)

    response = prompt_gpt("Summarize the contents of the screenshot.", base64_image)

    output_filename = os.path.basename(screenshot_path).split(".")[0] + ".txt"

    # Write the response to a file
    with open(os.path.join(output_folder_path, output_filename) , "w", encoding="utf-8") as file:
        file.write(response.json()["choices"][0]["message"]["content"])

    return response.json()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python summarize.py <screenshot_path> <output_file>")
        sys.exit(1)

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Summarize the contents of a screenshot using AI.")
    parser.add_argument("screenshot_path", help="Path to the screenshot file.")
    parser.add_argument("output_folder", help="Path to host folder to save the summary text file.")
    args = parser.parse_args()

    if not os.path.exists(args.screenshot_path):
        print("Error: Screenshot file not found.")
        exit(1)

    # Call the summarize_screenshot function with the provided argument
    summary = summarize_screenshot(args.screenshot_path, args.output_folder)
    print(summary)
