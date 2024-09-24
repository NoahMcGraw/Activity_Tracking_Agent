import os
import sys
import datetime
from PIL import ImageGrab

def save_screenshot(save_folder):
    # Get the current date and time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Capture the screenshot
    screenshot = ImageGrab.grab()

    # Construct the file path
    file_path = os.path.join(save_folder, f"{timestamp}.png")

    # Save the screenshot
    screenshot.save(file_path)

    screenshot.close()

    print(f"Screenshot saved to: {file_path}")

    return file_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python screenshot_saver.py <save_folder>")
        sys.exit(1)

    save_folder = sys.argv[1]

    # Create the save folder if it doesn't exist
    os.makedirs(save_folder, exist_ok=True)

    save_screenshot(save_folder)
