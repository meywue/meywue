# Description:
"""
Description:
Simple template for a Python script to be used as a starting point for new projects.

Requirements:

ToDo:
- [ ] Add requirements
- [ ] Add description
- [ ] Add usage
- [ ] Add examples
- [ ] Add tests
- [ ] Add documentation
"""

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="A template for a Python script.")
    parser.add_argument(
        '--option',
        type=str,
        help='An example option for the script.'
    )
    return parser.parse_args()

def main():
    args = parse_args()

    if args.option:
        print(f"You provided the option: {args.option}")
    else:
        print("No option provided.")


if __name__ == "__main__":
    main()