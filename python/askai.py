import argparse
import subprocess
import sys
from openrouter_api import ask_openrouter

# Check if data is piped into stdin
def get_piped_input():
    if not sys.stdin.isatty():
        data = sys.stdin.read()
        return data
    return None

def main():
    parser = argparse.ArgumentParser(description="askai - AI assistant for your terminal")
    parser.add_argument('-q', '--question', help='Your question for the AI')
    parser.add_argument('-c', '--context', action='store_true', help='Use piped stdin as context')
    parser.add_argument('-o', '--output', help='Output file to save result')
    parser.add_argument('--format', default="rawtext", choices=["rawtext", "json", "md"], help='Instruct AI to respond in rawtext (default), json, or md format')
    parser.add_argument('-m', '--model', help='Override default model')
    
    args = parser.parse_args()

    context_input = get_piped_input() if args.context else None

    if not args.question:
        print("Error: Provide a question with -q")
        sys.exit(1)
    
    if args.context and context_input is None:
        print("Error: -c flag used but no piped input detected.")
        sys.exit(1)

    # Compose message for AI
    messages = []

    if context_input:
        messages.append({"role": "system", "content": "Previous terminal output:\n" + context_input})

    format_instruction = {
        "rawtext": "Please provide your response as plain text.",
        "md": "Please format the response as GitHub-flavored Markdown.",
        "json": "Please respond with a valid JSON structure containing your answer."
    }.get(args.format, "Please provide your response as plain text.")

    messages.append({"role": "system", "content": format_instruction})

    if args.question:
        messages.append({"role": "user", "content": args.question})

    response = ask_openrouter(messages=messages, model=args.model)

    if args.output:
        with open(args.output, "w") as f:
            f.write(response)
        print(f"Response written to {args.output}")
    else:
        print(response)

if __name__ == "__main__":
    main()
