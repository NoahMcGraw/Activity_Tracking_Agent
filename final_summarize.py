import os
import glob

from prompt_gpt import prompt_gpt

def summarize_summaries(summaries_folder, final_summary_file_path):

    # Get all the summary files in the summaries folder
    summary_files = glob.glob(os.path.join(summaries_folder, "*.txt"))

    # Concatenate the summaries
    all_summaries = ""
    for summary_file in summary_files:
        with open(summary_file, "r", encoding="utf-8") as file:
            # Prepend the file name as a header since file names are timestamps
            all_summaries += f"### {os.path.basename(summary_file)}\n"
            all_summaries += file.read() + "\n"

    base_prompt = "The following are timestamped summaries of screenshots taken during a work session. Please provide a final summary of what the user was working on during the session. \n\n"

    # Generate the final summary
    response = prompt_gpt(base_prompt + all_summaries)

    # Write the final summary to a file
    with open(final_summary_file_path, "w", encoding="utf-8") as file:
        file.write(response.json()["choices"][0]["message"]["content"])

    return response.json()
