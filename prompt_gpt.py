import os
import sys
import argparse
import base64
import requests
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

def prompt_gpt(system_prompt: str, user_prompt: str, context_prompts: list = None, base64_images: list = None):
    if system_prompt is None:
        print("Error: System prompt is required.")
        exit(1)
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
          "role": "system",
          "content": [
            {
              "type": "text",
              "text": system_prompt
            }
          ]
        }
      ],
      "max_tokens": 600
    }

    if context_prompts is not None and len(context_prompts) > 0:
        # Add the context prompts to the payload
        for prompt in context_prompts:
            payload["messages"].append({
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            })

    user_message = {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": user_prompt
        }
      ]
    }

    if base64_images is not None and len(base64_images) > 0:
        for base64_image in base64_images:
          user_message["content"].append({
              "type": "image_url",
              "image_url": {
                  "url": f"data:image/png;base64,{base64_image}"
              }
          })

    payload["messages"].append(user_message)

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=30)

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
