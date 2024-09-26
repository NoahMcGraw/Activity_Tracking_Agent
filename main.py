import sys
import os
import time
import argparse
import datetime
from final_summarize import summarize_summaries
from screenshot import save_screenshot
from summarize import summarize_screenshot

def capture_and_summarize(project_name, base_save_folder=None, save_interval=None, max_batch_size=None):
    # Check if the project name is provided
    if not project_name:
        print("Error: Project name is required.")
        sys.exit(1)

    # Get the base save folder from the environment variable if not provided
    if not base_save_folder:
        base_save_folder = os.getenv("DEFAULT_SAVE_FOLDER", "logs")

    # Get the save interval from the environment variable if not provided
    if not save_interval:
        save_interval = int(os.getenv("DEFAULT_SAVE_INTERVAL", "300"))

    if not max_batch_size:
        max_batch_size = int(os.getenv("DEFAULT_MAX_BATCH_SIZE", "3"))

    # Get the OpenAI API key from the environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    datestamp = datetime.datetime.now().strftime("%Y-%m-%d")

    # Create the screenshots and summaries folders if they don't exist
    project_folder = os.path.join(base_save_folder, datestamp, project_name)
    screenshots_folder = os.path.join(project_folder, ".image_cache")
    summaries_folder = os.path.join(project_folder, "summaries")
    os.makedirs(screenshots_folder, exist_ok=True)
    os.makedirs(summaries_folder, exist_ok=True)

    screenshot_buffer = []
    summary_context_path = None

    def cleanupScreenshotBuffer():
        while len(screenshot_buffer) > 0:
            path = screenshot_buffer.pop(0)
            os.remove(path)

    # Capture and summarize the screenshots at the specified interval
    try:
        while True:
            screenshot_path = save_screenshot(screenshots_folder)
            screenshot_buffer.append(screenshot_path)
            if len(screenshot_buffer) >= max_batch_size:
                summary_context_path = summarize_screenshot(screenshot_buffer, summaries_folder, summary_context_path)
                # Clear the screenshot buffer after summarizing
                cleanupScreenshotBuffer()

            # Wait for the specified interval before capturing the next screenshot
            time.sleep(save_interval)

    except KeyboardInterrupt:
        print("\nUser interrupted the script. Generating final summary...")
        if screenshot_buffer:
            summary_context_path = summarize_screenshot(screenshot_buffer, summaries_folder, summary_context_path)
            cleanupScreenshotBuffer()
        final_summary_path = summarize_summaries(summaries_folder, os.path.join(project_folder, "final_summary.txt"))
        # Remove the image cache folder if it is empty
        if not os.listdir(screenshots_folder):
            os.rmdir(screenshots_folder)
        print(f"Final Summary saved at: {final_summary_path}")
        print("Exiting...")

if __name__ == "__main__":
    # Set up the command-line argument parser
    parser = argparse.ArgumentParser(description="Summarize the contents of a screenshot using AI.")
    parser.add_argument("project_name", type=str, help="Name of the project.")
    parser.add_argument("--base_save_folder", type=str, help="Path to the base folder to save screenshots and summaries.")
    parser.add_argument("--save_interval", type=int, help="Interval in seconds to save screenshots.")
    parser.add_argument("--max_batch_size", type=int, help="Maximum batch size to send for analysis.")

    args = parser.parse_args()

    capture_and_summarize(args.project_name,args.base_save_folder, args.save_interval, args.max_batch_size)
