import os
import argparse
import sys
import threading
import logging
import json
from banner_argument_parser import BannerArgumentParser
from openrouter_api import ask_openrouter
from config import load_config
from logger import setup_logger
from utils import (
    write_to_file,
    tqdm_spinner,
    get_piped_input,
    get_file_input,
    get_system_context,
    build_format_instruction,
    list_system_files,
    view_system_file,
    render_markdown,
    print_error_or_warnings
)


def parse_arguments(logger):
    parser = BannerArgumentParser(description="askai - AI assistant for your terminal")
    parser.add_argument('-q', '--question', help='Your question for the AI')
    parser.add_argument('-i', '--input', help='Input file to include as context')
    parser.add_argument('-o', '--output', help='Output file to save result')
    parser.add_argument('-f', '--format', default="rawtext", choices=["rawtext", "json", "md"], help='Instruct AI to respond in rawtext (default), json, or md format')
    parser.add_argument('--plain-md', action='store_true', help='If used with -f md, outputs raw markdown as plain text instead of rendering')
    parser.add_argument('-m', '--model', help='Override default AI model')
    parser.add_argument('-s', '--system', help='Add system-specific context from systems folder')
    parser.add_argument('-l', '--list-systems', action='store_true', help='List all available system files')
    parser.add_argument('-vs', '--view-system', help='View specific system file')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging for this session')

    logger.info(json.dumps({"log_message": "Prepared argument parser"}))

    return parser.parse_args()


def build_messages(args, base_path, logger):
    """Builds the message list for OpenRouter."""
    messages = []

    if context := get_piped_input():
        logger.info(json.dumps({"log_message": "Piped input received"}))
        messages.append({"role": "system", "content": f"Previous terminal output:\n{context}"})

    if args.input and (file_content := get_file_input(args.input)):
        logger.info(json.dumps({"log_message": "Input file read successfully", "file_path": args.input}))
        messages.append({"role": "system", "content": f"The file content of {args.input} to work with:\n{file_content}"})

    if args.system:
        logger.info(json.dumps({"log_message": "System used", "system": args.system}))
        system_context = get_system_context(args.system, base_path)
        if system_context:
            messages.append({"role": "system", "content": system_context})

    messages.append({"role": "system", "content": build_format_instruction(args.format)})

    if args.question:
        messages.append({"role": "user", "content": args.question})

    return messages


def main():
    config = load_config()
    logger = setup_logger(config)

    # Display --help option if no arguments are provided
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    args = parse_arguments(logger)
    base_path = base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug(json.dumps({"log_message": "Debug mode activated via CLI"}))

    if args.list_systems:
        logger.info(json.dumps({"log_message": "User requested to list all available system files"}))
        list_system_files(base_path)
        sys.exit(0)

    if args.view_system:
        logger.info(json.dumps({"log_message": "User requested to view system file", "system": args.view_system}))
        view_system_file(base_path, args.view_system)
        sys.exit(0)

    if not args.question and not args.system:
        logger.error(json.dumps({"log_message": "User did not provide a question with -q or a dedicated system with -s"}))
        print_error_or_warnings(text="ERROR: Provide a question with -q or a dedicated system with -s")
        sys.exit(1)

    if args.plain_md and args.format != "md":
        logger.warning(json.dumps({"log_message": "User used --plain-md without -f md"}))
        print_error_or_warnings(text="WARN: --plain-md can only be used with -f md. The parameter --plain-md will be ignored.", warning_only=True)

    messages = build_messages(args, base_path, logger)
    logger.debug(json.dumps({"log_message": "Messages content", "messages": messages}))

    stop_spinner = threading.Event()
    spinner = threading.Thread(target=tqdm_spinner, args=(stop_spinner,))
    spinner.start()

    try:
        logger.info(json.dumps({"log_message": "Messages sending to ai"}))
        response = ask_openrouter(messages=messages, model=args.model)
        logger.debug(json.dumps({"log_message": "Response from ai", "response_type": str(type(response))}))
        logger.info(json.dumps({"log_message": "Response received from ai"}))
    finally:
        stop_spinner.set()
        spinner.join()

    if args.output:
        logger.info(json.dumps({"log_message": "Writing response to output file", "output_file": args.output}))
        write_to_file(args.output, response)
        print(f"Response written to {args.output}")
        sys.exit(0) # No output since output is in file
    
    if args.format == "md" and not args.plain_md:
        logger.info(json.dumps({"log_message": "Rendering response as markdown"}))
        render_markdown(response)
        sys.exit(0) # No other output since output is rendered markdown
    
    logger.info(json.dumps({"log_message": "Printing response as raw text"}))
    print(response) # Catch if no other output is used


if __name__ == "__main__":
    main()
