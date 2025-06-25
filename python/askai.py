import os
import argparse
import sys
import itertools
import threading
import time
from openrouter_api import ask_openrouter
from tqdm import tqdm


def tqdm_spinner(stop_event):
    with tqdm(total=1, bar_format="{desc} {bar}") as pbar:
        spinner_cycle = itertools.cycle(['|', '/', '-', '\\'])
        while not stop_event.is_set():
            pbar.set_description_str(f"Thinking {next(spinner_cycle)}")
            time.sleep(0.1)

# Check if data is piped into stdin
def get_piped_input():
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        return data
    return None

# Check if data is provided as file input
def get_file_input(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return f.read()
    print("File {0} does not exists.".format(file_path))
    return None


def main():
    parser = argparse.ArgumentParser(description="askai - AI assistant for your terminal")
    parser.add_argument('-q', '--question', help='Your question for the AI')
    parser.add_argument('-i', '--input', help='Input file to read for prompt')
    parser.add_argument('-o', '--output', help='Output file to save result')
    parser.add_argument('-f', '--format', default="rawtext", choices=["rawtext", "json", "md"], help='Instruct AI to respond in rawtext (default), json, or md format')
    parser.add_argument('-m', '--model', help='Override default model')
    parser.add_argument('-s', '--system', help='Add specific system information from systems folder.')
    
    args = parser.parse_args()

    context_input = get_piped_input()
    file_input = get_file_input(args.input) if args.input else None

    if not args.question and not args.system:
        print("Error: Provide a question with -q or a dedicated system with -s")
        sys.exit(1)

    # Compose message for AI
    messages = []

    if context_input:
        messages.append({"role": "system", "content": "Previous terminal output:\n" + context_input})

    if file_input:
        messages.append({"role": "system", "content": "The file content of {0} to work with:\n{1}".format(args.input, file_input)})

    if args.system:
        for file in os.listdir("/home/nicola/Git/askai-cli/systems"):
            if "{0}".format(args.system) == file:
                with open("/home/nicola/Git/askai-cli/systems/{0}".format(args.system)) as f:
                    messages.append({"role": "system", "content": f.read()})


    format_instruction = {
        "rawtext": "Please provide your response as plain text.",
        "md": "Please format the response as GitHub-flavored Markdown.",
        "json": "Please respond with a valid JSON structure containing your answer."
    }.get(args.format, "Please provide your response as plain text.")

    messages.append({"role": "system", "content": format_instruction})

    if args.question:
        messages.append({"role": "user", "content": args.question})

    stop_spinner = threading.Event()
    spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
    spinner.start()

    try:
        response = ask_openrouter(messages=messages, model=args.model)
    finally:
        stop_spinner.set()
        spinner.join()


    if args.output:
        with open(args.output, "w") as f:
            f.write(response)
        print(f"Response written to {args.output}")
    else:
        print(response)

if __name__ == "__main__":
    main()
