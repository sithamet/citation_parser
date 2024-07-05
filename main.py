import json

from parser import APACitationParser


def main():
    print("APA Citation Parser")
    print("Enter your APA citation below (or 'q' to quit):")

    while True:
        citation = input().strip()
        if citation.lower() == 'q':
            break

        if not citation:
            print("Please enter a citation or 'q' to quit.")
            continue

        parsed_result = APACitationParser.parse(citation)
        print("\nParsed Result:")
        print(json.dumps(parsed_result, indent=2))
        print("\nEnter another citation or 'q' to quit:")

if __name__ == "__main__":
    main()