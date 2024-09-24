import os
import sys
import argparse
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def prompt_gpt(prompt, base64_image=None):
    # Get the OpenAI API key from the .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        exit(1)

    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4o-mini",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": prompt
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    if base64_image:
        payload["messages"][0]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image}"
            }
        })

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    print(response.json())

    return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prompt_gpt.py <prompt>")
        sys.exit(1)

    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Summarize the contents of a screenshot using AI.")
    parser.add_argument("prompt", help="Prompt to send to the GPT-4o model.")
    parser.add_argument("--base64_image", help="Base64 encoded image to send to the GPT-4o model.")
    args = parser.parse_args()


    prompt_gpt(args.prompt, args.base64_image)
