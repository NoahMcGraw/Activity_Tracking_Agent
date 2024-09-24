import sys
import os
import time
import argparse
import datetime
from final_summarize import summarize_summaries
from screenshot import save_screenshot
from summarize import summarize_screenshot

def capture_and_summarize(base_save_folder=None, save_interval=300):
    # Get the base save folder from the environment variable if not provided
    if not base_save_folder:
        base_save_folder = os.getenv("DEFAULT_SAVE_FOLDER")
        if not base_save_folder:
            print("Error: DEFAULT_SAVE_FOLDER environment variable is not set.")
            sys.exit(1)

    # Create base save folder if it doesn't exist
    os.makedirs(base_save_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create the screenshots and summaries folders if they don't exist
    session_folder = os.path.join(base_save_folder, timestamp)
    os.makedirs(session_folder, exist_ok=True)
    screenshots_folder = os.path.join(session_folder, "screenshots")
    summaries_folder = os.path.join(session_folder, "summaries")
    os.makedirs(screenshots_folder, exist_ok=True)
    os.makedirs(summaries_folder, exist_ok=True)

    # Get the OpenAI API key from the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    # Capture and summarize the screenshots at the specified interval
    try:
        while True:
            screenshot_path = save_screenshot(screenshots_folder)
            summary_path = summarize_screenshot(screenshot_path, summaries_folder)
            print(f"Screenshot saved at: {screenshot_path}")
            print(f"Summary saved at: {summary_path}")

            # Wait for the specified interval before capturing the next screenshot
            time.sleep(save_interval)

    except KeyboardInterrupt:
        print("\nUser interrupted the script. Generating final summary...")
        final_summary_file_path = os.path.join(session_folder, "final_summary.txt")
        # Call the summarize_summaries function with the provided argument
        summarize_summaries(summaries_folder, final_summary_file_path)
        print(f"Final summary saved to: {final_summary_file_path}")
        print("Exiting...")

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Summarize the contents of a screenshot using AI.")
    parser.add_argument("--base_save_folder", help="Path to the base folder to save screenshots and summaries.")
    parser.add_argument("--save_interval", type=int, default=10, help="Interval in seconds to save screenshots.")
    args = parser.parse_args()

    capture_and_summarize(args.base_save_folder, args.save_interval)
