import os
import io
import sys
import argparse
import base64
import datetime
import requests
from PIL import Image

from prompt_gpt import prompt_gpt


# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def summarize_screenshot(screenshot_paths: list, output_folder_path: str, context_path: str=None):
    base64_images = []

    for screenshot_path in screenshot_paths:
        if not os.path.exists(screenshot_path):
            print(f"Error: Screenshot file not found: {screenshot_path}")
            return

        # Getting the base64 string
        base64_images.append(encode_image(screenshot_path))


    context = []

    if context_path:
        with open(context_path, "r", encoding="utf-8") as file:
            context.append(file.read())

    response = prompt_gpt("You are about to receive a list of screenshots from someone during their typical workday. Along with the screenshots, you may also receive a text summary of the tasks they have already completed or worked on during that day. Your goal is to analyze the information provided from both the images and the summary and follow these steps:\n 1. Retain previous task context: Maintain any documented tasks or updates unless new information directly overrides or complements them.\n 2. Identify and add new tasks: If there are tasks in the screenshots or the summary that have not been previously documented, add them to the task list.\n 3. Update ongoing tasks: If any task from previous updates is still being worked on or shows progress, update its status using the new information. Always try to build on prior progress rather than replacing it entirely unless explicitly instructed by the new data.\n 4.Infer task progress: For each task (both new and existing), infer the current state based on available information from the screenshots and summaries.\n 5. Ensure your responses reflect the most relevant and current information from both the screenshots and summaries, while keeping previous context intact.\n 6. Group similar activities under broad task categories. Avoid breaking tasks into small sub-tasks.\n Return any updates clearly using bullet points or numbered lists. DO NOT RETURN ANYTHING MORE THAN THE LIST THAT YOU CREATED", "Attached are the current batch of screenshots", context, base64_images)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    output_filename = timestamp + ".txt"

    # Write the response to a file
    with open(os.path.join(output_folder_path, output_filename) , "w", encoding="utf-8") as file:
        file.write(response.json()["choices"][0]["message"]["content"])

    print(f"Summary saved at: {os.path.join(output_folder_path, output_filename)}")

    return os.path.join(output_folder_path, output_filename)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python summarize.py <screenshot_path> <output_file>")
        sys.exit(1)

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Summarize the contents of a screenshot using AI.")
    parser.add_argument("screenshot_path", help="Path to the screenshot file.")
    parser.add_argument("output_folder", help="Path to host folder to save the summary text file.")
    parser.add_argument("context_path", default=None, help="Path to the context file for previous summaries.")

    args = parser.parse_args()

    # Call the summarize_screenshot function with the provided argument
    summary_file_path = summarize_screenshot(args.screenshot_path, args.output_folder, args.context_path)
    print(summary_file_path)
