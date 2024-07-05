import re
import json
from typing import Dict, List, Any


def parse_authors(authors_string: str) -> List[Dict[str, str]]:
    authors = []
    author_pattern = re.compile(r'([\w-]+(?:\s+[\w-]+)*),\s*([A-Z](?:\.\s*[A-Z])*\.?)')
    matches = author_pattern.findall(authors_string)

    for last_name, initials in matches:
        authors.append({
            "last_name": last_name.strip(),
            "first_name": initials.strip()
        })

    return authors


def parse_standard_journal_citation(citation: str) -> Dict[str, Any]:
    match = re.search(r'([\w\s]+),\s*(\d+)\((\d+)\),\s*(\d+(?:-\d+)?)', citation)
    if match:
        return {
            "journal_name": match.group(1).strip(),
            "volume": match.group(2),
            "issue": match.group(3),
            "page_range": match.group(4)
        }
    return None

def parse_journal_citation_with_volume(citation: str) -> Dict[str, Any]:
    match = re.search(r'([\w\s]+),\s*(\d+),\s*(\d+(?:-\d+)?)', citation)
    if match:
        return {
            "journal_name": match.group(1).strip(),
            "volume": match.group(2),
            "issue": "",
            "page_range": match.group(3)
        }
    return None

def parse_journal_citation_without_volume(citation: str) -> Dict[str, Any]:
    match = re.search(r'([\w\s]+),\s*(\d+(?:-\d+)?)', citation)
    if match:
        return {
            "journal_name": match.group(1).strip(),
            "volume": "",
            "issue": "",
            "page_range": match.group(2)
        }
    return None

def parse_journal_citation(citation: str) -> Dict[str, Any]:
    result = {
        "source_type": "journal",
        "authors": [],
        "title": "",
        "year": "",
        "publisher": "",
        "volume": "",
        "issue": "",
        "page_range": "",
        "journal_name": "",
        "url": "",
        "doi": ""
    }

    # Extract authors and year
    author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
    if author_year_match:
        result["authors"] = parse_authors(author_year_match.group(1))
        result["year"] = author_year_match.group(2)

    # Extract title
    title_match = re.search(r'\)\.\s*(.*?)\.\s', citation)
    if title_match:
        result["title"] = title_match.group(1).strip()

    # Try different journal citation formats
    journal_info = parse_standard_journal_citation(citation) or \
                   parse_journal_citation_with_volume(citation) or \
                   parse_journal_citation_without_volume(citation)

    if journal_info:
        result.update(journal_info)

    # Extract DOI if present
    doi_match = re.search(r'https?://doi\.org/(10\.\d{4,}[\w\d\.\-\/]+)', citation)
    if doi_match:
        result["doi"] = doi_match.group(1)
        result["url"] = f"https://doi.org/{result['doi']}"

    return result

def parse_standard_book_citation(citation: str) -> Dict[str, Any]:
    result = {
        "source_type": "book",
        "authors": [],
        "title": "",
        "year": "",
        "publisher": "",
        "volume": "",
        "issue": "",
        "page_range": "",
        "journal_name": "",
        "url": "",
        "doi": ""
    }

    # Extract authors and year
    author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
    if author_year_match:
        result["authors"] = parse_authors(author_year_match.group(1))
        result["year"] = author_year_match.group(2)

    # Extract title, publisher, and page range
    title_publisher_match = re.search(r'\)\.\s*(.*?)\.\s*(.*?)(?:,\s*(\d+))?\.$', citation)
    if title_publisher_match:
        result["title"] = title_publisher_match.group(1).strip()
        result["publisher"] = title_publisher_match.group(2).strip()
        if title_publisher_match.group(3):
            result["page_range"] = title_publisher_match.group(3)

    return result


def parse_edited_book_citation(citation: str) -> Dict[str, Any]:
    result = {
        "source_type": "book",
        "authors": [],
        "title": "",
        "year": "",
        "publisher": "",
        "volume": "",
        "issue": "",
        "page_range": "",
        "journal_name": "",
        "url": "",
        "doi": ""
    }

    # Extract authors, editor status, and year
    author_year_match = re.match(r'(.*?)\s*\((Ed\.?|Eds\.?)\)\.\s*\((\d{4})\)', citation)
    if author_year_match:
        result["authors"] = parse_authors(author_year_match.group(1))
        result["year"] = author_year_match.group(3)

    # Split the remaining citation
    remaining_citation = citation.split(f"{result['year']}).")[-1].strip()

    # Extract volume from parentheses
    volume_match = re.search(r'\(Vol\.\s*(\d+)\)', remaining_citation)
    if volume_match:
        result["volume"] = volume_match.group(1)
        # Split by volume information
        title_publisher_parts = re.split(r'\s*\(Vol\.\s*\d+\)\.\s*', remaining_citation)
        if len(title_publisher_parts) == 2:
            result["title"] = title_publisher_parts[0].strip()
            result["publisher"] = title_publisher_parts[1].strip()
    else:
        # If there's no volume, split by the last period
        parts = remaining_citation.rsplit('.', 1)
        if len(parts) == 2:
            result["title"] = parts[0].strip()
            result["publisher"] = parts[1].strip()
        else:
            result["title"] = remaining_citation.strip()

    # Clean up any trailing periods in title and publisher
    result["title"] = result["title"].rstrip('.')
    result["publisher"] = result["publisher"].rstrip('.')

    # If publisher is empty, try to extract it from the title
    if not result["publisher"] and '.' in result["title"]:
        title_parts = result["title"].rsplit('.', 1)
        result["title"] = title_parts[0].strip()
        result["publisher"] = title_parts[1].strip()

    return result


def parse_book_section_citation(citation: str) -> Dict[str, Any]:
    result = {
        "source_type": "book",
        "authors": [],
        "title": "",
        "year": "",
        "publisher": "",
        "volume": "",
        "issue": "",
        "page_range": "",
        "journal_name": "",
        "url": "",
        "doi": ""
    }

    # Extract authors and year
    author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
    if author_year_match:
        result["authors"] = parse_authors(author_year_match.group(1))
        result["year"] = author_year_match.group(2)

    # Extract title, page range, and publisher
    remaining_citation = citation.split(f"{result['year']}).")[-1].strip()
    parts = re.split(r'\s*\(pp\.\s*(\d+[-–]\d+)\)\.\s*', remaining_citation)

    if len(parts) == 3:
        result["title"] = parts[0].strip()
        result["page_range"] = parts[1]
        result["publisher"] = parts[2].strip().rstrip('.')
    elif len(parts) == 2:
        result["title"] = parts[0].strip()
        result["publisher"] = parts[1].strip().rstrip('.')

    return result

def parse_book_chapter_citation(citation: str) -> Dict[str, Any]:
    result = {
        "source_type": "book",
        "authors": [],
        "title": "",
        "year": "",
        "publisher": "",
        "volume": "",
        "page_range": "",
        "url": "",
        "doi": ""
    }

    # Extract authors and year
    author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
    if author_year_match:
        result["authors"] = parse_authors(author_year_match.group(1))
        result["year"] = author_year_match.group(2)

    # Extract book title, volume, and page range
    book_info_match = re.search(r'In\s+(.*?)\s*(?:\(((?:Vol\.|Vols\.)\s*\d+[,–-]*\d*)\s*,?)?\s*(?:pp\.\s*(\d+[-–]\d+)\))', citation)
    if book_info_match:
        result["title"] = book_info_match.group(1).strip().rstrip(' (')
        if book_info_match.group(2):
            result["volume"] = book_info_match.group(2).strip()
        if book_info_match.group(3):
            result["page_range"] = book_info_match.group(3)

    # Extract publisher
    publisher_match = re.search(r'(?:pp\.\s*\d+[-–]\d+\))\.?\s*(.*?)\.$', citation)
    if publisher_match:
        result["publisher"] = publisher_match.group(1).strip()
        # Remove location if present
        result["publisher"] = re.sub(r'^.*?:\s*', '', result["publisher"])

    return result

def parse_book_citation(citation: str) -> Dict[str, Any]:
    if re.search(r'\((Ed\.?|Eds\.?)\)', citation):
        print("Parsing as edited book citation")
        return parse_edited_book_citation(citation)
    elif re.search(r'\(pp\.\s*\d+[-–]\d+\)', citation):
        print("Parsing as book section citation")
        return parse_book_section_citation(citation)
    else:
        print("Parsing as standard book citation")
        return parse_standard_book_citation(citation)


def parse_apa_citation(citation: str) -> Dict[str, Any]:
    # Check for book chapter citation
    if re.search(r'\.\s+In\s+', citation):
        print("Parsing as book chapter citation")
        return parse_book_chapter_citation(citation)
    # Check for journal citation patterns
    elif re.search(r'\d+\(\d+\),', citation) or \
         re.search(r',\s*\d+,\s*\d+[-–]\d+', citation) or \
         re.search(r'[\w\s]+,\s*\d+[-–]\d+', citation):
        print("Parsing as journal citation")
        return parse_journal_citation(citation)
    # Check for book citation patterns
    elif re.search(r'\((Ed\.?|Eds\.?)\)', citation) or re.search(r'\(pp\.\s*\d+[-–]\d+\)', citation):
        print("Parsing as book citation")
        return parse_book_citation(citation)
    else:
        print("Parsing as standard book citation")
        return parse_standard_book_citation(citation)


def main():
    print("APA Citation Parser with Robust Edited Book Handling")
    print("Enter your APA citation below (or 'q' to quit):")

    while True:
        citation = input().strip()
        if citation.lower() == 'q':
            break

        if not citation:
            print("Please enter a citation or 'q' to quit.")
            continue

        parsed_result = parse_apa_citation(citation)
        print("\nParsed Result:")
        print(json.dumps(parsed_result, indent=2))
        print("\nEnter another citation or 'q' to quit:")


if __name__ == "__main__":
    main()