import sys
import os
import time
import signal
import argparse
import datetime
import threading
import tkinter as tk
from tkinter import ttk
from final_summarize import summarize_summaries
from screenshot import save_screenshot
from summarize import summarize_screenshot

is_paused = False
exit_flag = threading.Event()

def pause():
    global is_paused
    print("Pausing...")
    is_paused = True

def resume():
    global is_paused
    print("Resuming...")
    is_paused = False

def capture_and_summarize(project_name, base_save_folder=None, save_interval=None, max_batch_size=None):
    global is_paused
    
    if not base_save_folder:
        base_save_folder = os.getenv("DEFAULT_SAVE_FOLDER", "logs")
    if not save_interval:
        save_interval = int(os.getenv("DEFAULT_SAVE_INTERVAL", "300"))
    if not max_batch_size:
        max_batch_size = int(os.getenv("DEFAULT_MAX_BATCH_SIZE", "3"))

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    datestamp = datetime.datetime.now().strftime("%Y-%m-%d")
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

    try:
        while not exit_flag.is_set():
            if not is_paused:
                screenshot_path = save_screenshot(screenshots_folder)
                screenshot_buffer.append(screenshot_path)
                if len(screenshot_buffer) >= max_batch_size:
                    summary_context_path = summarize_screenshot(screenshot_buffer, summaries_folder, summary_context_path)
                    cleanupScreenshotBuffer()

            current_wait_time = 0
            while current_wait_time < save_interval and not exit_flag.is_set():
                time.sleep(1)
                current_wait_time += 1
                if is_paused:
                    break

    finally:
        print("\nCleaning up and generating final summary...")
        if screenshot_buffer:
            summary_context_path = summarize_screenshot(screenshot_buffer, summaries_folder, summary_context_path)
            cleanupScreenshotBuffer()
        final_summary_path = summarize_summaries(summaries_folder, os.path.join(project_folder, "final_summary.txt"))
        if not os.listdir(screenshots_folder):
            os.rmdir(screenshots_folder)
        print(f"Final Summary saved at: {final_summary_path}")

class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Screenshot Capture and Summarize")
        self.geometry("600x500")

        self.project_name = tk.StringVar()
        self.save_interval = tk.IntVar(None, int(os.getenv("DEFAULT_SAVE_INTERVAL", "300")))
        self.max_batch_size = tk.IntVar(None, int(os.getenv("DEFAULT_MAX_BATCH_SIZE", "3")))
        self.status = tk.StringVar()
        self.status.set("Ready")

        self.create_widgets()

        self.work_thread = None

    def create_widgets(self):
        ttk.Label(self, text="Project Name:").pack(pady=5)
        ttk.Entry(self, textvariable=self.project_name).pack(pady=5)
        ttk.Label(self, text="Save Interval (in seconds):").pack(pady=5)
        ttk.Entry(self, textvariable=self.save_interval).pack(pady=5)
        ttk.Label(self, text="Max Batch Size:").pack(pady=5)
        ttk.Entry(self, textvariable=self.max_batch_size).pack(pady=5)

        ttk.Button(self, text="Start/Resume", command=self.start_resume).pack(pady=5)
        ttk.Button(self, text="Pause", command=self.pause).pack(pady=5)
        ttk.Button(self, text="Stop", command=self.stop).pack(pady=5)

        ttk.Label(self, textvariable=self.status).pack(pady=10)

    def start_resume(self):
        if not self.work_thread or not self.work_thread.is_alive():
            if not self.project_name.get():
                self.status.set("Error: Project name is required")
                return

            self.work_thread = threading.Thread(
                target=capture_and_summarize,
                args=(self.project_name.get(),None, self.save_interval.get(), self.max_batch_size.get()),
                daemon=True
            )
            self.work_thread.start()
            self.status.set("Running")
        else:
            resume()
            self.status.set("Resumed")

    def pause(self):
        if self.work_thread and self.work_thread.is_alive():
            pause()
            self.status.set("Paused")

    def stop(self):
        if self.work_thread and self.work_thread.is_alive():
            exit_flag.set()
            self.work_thread.join()
            self.status.set("Stopped")
            # destroy the thread object
            self.work_thread = None
            # Reset the exit flag
            exit_flag.clear()

def main():
    app = Application()
    app.mainloop()

if __name__ == "__main__":
    main()
