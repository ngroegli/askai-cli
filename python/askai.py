import argparse
import subprocess
import sys
from openrouter_api import ask_openrouter

def main():
    parser = argparse.ArgumentParser(description="Ask OpenRouter AI from your terminal.")
    parser.add_argument("-q", "--question", type=str, help="Your prompt/question.")
    parser.add_argument("-c", "--cli", action="store_true", help="Interpret previous CLI output.")
    parser.add_argument("-o", "--output", type=str, help="Write response to file.")
    parser.add_argument("-m", "--model", type=str, help="Override default model.")
    
    args = parser.parse_args()

    if not args.question:
        print("Error: Provide a question with -q")
        sys.exit(1)
    
    previous_output = None
    if args.cli:
        previous_output = sys.stdin.read()

    response = ask_openrouter(prompt=args.question, previous=previous_output, model=args.model)

    if args.output:
        with open(args.output, "w") as f:
            f.write(response)
        print(f"Response written to {args.output}")
    else:
        print(response)

if __name__ == "__main__":
    main()
