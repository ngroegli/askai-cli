import os
import argparse
import sys
import threading
from openrouter_api import ask_openrouter
from utils import (
    write_to_file,
    tqdm_spinner,
    get_piped_input,
    get_file_input,
    get_system_context,
    build_format_instruction,
    list_system_files,
    view_system_file
)


def parse_arguments():
    parser = argparse.ArgumentParser(description="askai - AI assistant for your terminal")
    parser.add_argument('-q', '--question', help='Your question for the AI')
    parser.add_argument('-i', '--input', help='Input file to include as context')
    parser.add_argument('-o', '--output', help='Output file to save result')
    parser.add_argument('-f', '--format', default="rawtext", choices=["rawtext", "json", "md"], help='Instruct AI to respond in rawtext (default), json, or md format')
    parser.add_argument('-m', '--model', help='Override default AI model')
    parser.add_argument('-s', '--system', help='Add system-specific context from systems folder')
    parser.add_argument('-l', '--list-systems', action='store_true', help='List all available system files')
    parser.add_argument('-vs', '--view-system', help='View specific system file')

    return parser.parse_args()


def build_messages(args, base_path):
    """Builds the message list for OpenRouter."""
    messages = []

    if context := get_piped_input():
        messages.append({"role": "system", "content": f"Previous terminal output:\n{context}"})

    if args.input and (file_content := get_file_input(args.input)):
        messages.append({"role": "system", "content": f"The file content of {args.input} to work with:\n{file_content}"})

    if args.system:
        system_context = get_system_context(args.system, base_path)
        if system_context:
            messages.append({"role": "system", "content": system_context})

    messages.append({"role": "system", "content": build_format_instruction(args.format)})

    if args.question:
        messages.append({"role": "user", "content": args.question})

    return messages


def main():
    args = parse_arguments()
    base_path = base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.list_systems:
        list_system_files(base_path)
        sys.exit(0)

    if args.view_system:
        view_system_file(base_path, args.view_system)
        sys.exit(0)

    if not args.question and not args.system:
        print("Error: Provide a question with -q or a dedicated system with -s")
        sys.exit(1)

    messages = build_messages(args, base_path)

    stop_spinner = threading.Event()
    spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
    spinner.start()

    try:
        response = ask_openrouter(messages=messages, model=args.model)
    finally:
        stop_spinner.set()
        spinner.join()

    if args.output:
        write_to_file(args.output, response)
        print(f"Response written to {args.output}")
    else:
        print(response)


if __name__ == "__main__":
    main()
