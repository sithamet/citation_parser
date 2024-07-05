import re
from typing import Dict, List, Any, Optional, Callable, Tuple


class AuthorParser:
    @staticmethod
    def parse(authors_string: str) -> List[Dict[str, str]]:
        authors = []
        author_pattern = re.compile(r'([\w-]+(?:\s+[\w-]+)*),\s*([A-Z](?:\.\s*[A-Z])*\.?)')
        matches = author_pattern.findall(authors_string)

        for last_name, initials in matches:
            authors.append({
                "last_name": last_name.strip(),
                "first_name": initials.strip()
            })

        return authors

class JournalCitationParser:
    @staticmethod
    def parse_standard(citation: str) -> Optional[Dict[str, str]]:
        match = re.search(r'([\w\s&]+?),\s*(\d+)\((\d+)\),\s*(\d+(?:-\d+)?)', citation)
        if match:
            return {
                "journal_name": match.group(1).strip(),
                "volume": match.group(2),
                "issue": match.group(3),
                "page_range": match.group(4)
            }
        return None

    @staticmethod
    def parse_with_issue(citation: str) -> Optional[Dict[str, str]]:
        match = re.search(r'([\w\s&]+?),\s*(\d+),\s*(\d+(?:-\d+)?)', citation)
        if match:
            return {
                "journal_name": match.group(1).strip(),
                "volume": "",
                "issue": match.group(2),
                "page_range": match.group(3)
            }
        return None

    @staticmethod
    def parse_without_volume(citation: str) -> Optional[Dict[str, str]]:
        match = re.search(r'([\w\s&]+?),\s*(\d+(?:-\d+)?)', citation)
        if match:
            return {
                "journal_name": match.group(1).strip(),
                "volume": "",
                "issue": "",
                "page_range": match.group(2)
            }
        return None

    @classmethod
    def parse(cls, citation: str) -> Dict[str, Any]:
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

        author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
        if author_year_match:
            result["authors"] = AuthorParser.parse(author_year_match.group(1))
            result["year"] = author_year_match.group(2)

        title_match = re.search(r'\)\.\s*(.*?)\.\s', citation)
        if title_match:
            result["title"] = title_match.group(1).strip()

        journal_info = cls.parse_standard(citation) or \
                       cls.parse_with_issue(citation) or \
                       cls.parse_without_volume(citation)

        if journal_info:
            result.update(journal_info)

        doi_match = re.search(r'https?://doi\.org/(10\.\d{4,}[\w\d\.\-\/]+)', citation)
        if doi_match:
            result["doi"] = doi_match.group(1)
            result["url"] = f"https://doi.org/{result['doi']}"

        return result


class BookCitationParser:
    @staticmethod
    def parse_standard(citation: str) -> Dict[str, Any]:
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

        author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
        if author_year_match:
            result["authors"] = AuthorParser.parse(author_year_match.group(1))
            result["year"] = author_year_match.group(2)

        title_publisher_match = re.search(r'\)\.\s*(.*?)\.\s*(.*?)(?:,\s*(\d+))?\.$', citation)
        if title_publisher_match:
            result["title"] = title_publisher_match.group(1).strip()
            result["publisher"] = title_publisher_match.group(2).strip()
            if title_publisher_match.group(3):
                result["page_range"] = title_publisher_match.group(3)

        return result

    @staticmethod
    def parse_edited(citation: str) -> Dict[str, Any]:
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

        author_year_match = re.match(r'(.*?)\s*\((Ed\.?|Eds\.?)\)\.\s*\((\d{4})\)', citation)
        if author_year_match:
            result["authors"] = AuthorParser.parse(author_year_match.group(1))
            result["year"] = author_year_match.group(3)

        remaining_citation = citation.split(f"{result['year']}).")[-1].strip()

        volume_match = re.search(r'\(Vol\.\s*(\d+)\)', remaining_citation)
        if volume_match:
            result["volume"] = volume_match.group(1)
            title_publisher_parts = re.split(r'\s*\(Vol\.\s*\d+\)\.\s*', remaining_citation)
            if len(title_publisher_parts) == 2:
                result["title"] = title_publisher_parts[0].strip()
                result["publisher"] = title_publisher_parts[1].strip()
        else:
            parts = remaining_citation.rsplit('.', 1)
            if len(parts) == 2:
                result["title"] = parts[0].strip()
                result["publisher"] = parts[1].strip()
            else:
                result["title"] = remaining_citation.strip()

        result["title"] = result["title"].rstrip('.')
        result["publisher"] = result["publisher"].rstrip('.')

        if not result["publisher"] and '.' in result["title"]:
            title_parts = result["title"].rsplit('.', 1)
            result["title"] = title_parts[0].strip()
            result["publisher"] = title_parts[1].strip()

        return result

    @staticmethod
    def parse_section(citation: str) -> Dict[str, Any]:
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

        author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
        if author_year_match:
            result["authors"] = AuthorParser.parse(author_year_match.group(1))
            result["year"] = author_year_match.group(2)

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

    @staticmethod
    def parse_chapter(citation: str) -> Dict[str, Any]:
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

        author_year_match = re.match(r'(.*?)\s*\((\d{4})\)', citation)
        if author_year_match:
            result["authors"] = AuthorParser.parse(author_year_match.group(1))
            result["year"] = author_year_match.group(2)

        book_info_match = re.search(r'In\s+(.*?)\s*(?:\(((?:Vol\.|Vols\.)\s*\d+[,–-]*\d*)\s*,?)?\s*(?:pp\.\s*(\d+[-–]\d+)\))', citation)
        if book_info_match:
            result["title"] = book_info_match.group(1).strip().rstrip(' (')
            if book_info_match.group(2):
                result["volume"] = book_info_match.group(2).strip()
            if book_info_match.group(3):
                result["page_range"] = book_info_match.group(3)

        publisher_match = re.search(r'(?:pp\.\s*\d+[-–]\d+\))\.?\s*(.*?)\.$', citation)
        if publisher_match:
            result["publisher"] = publisher_match.group(1).strip()
            result["publisher"] = re.sub(r'^.*?:\s*', '', result["publisher"])

        return result

class APACitationParser:
    @staticmethod
    def parse(citation: str) -> Dict[str, Any]:
        parsers: List[Tuple[Callable[[str], bool], Callable[[str], Dict[str, Any]]]] = [
            (lambda c: re.search(r'\.\s+In\s+', c) is not None, BookCitationParser.parse_chapter),
            (lambda c: re.search(r'\d+\(\d+\),', c) is not None or
                       re.search(r',\s*\d+,\s*\d+[-–]\d+', c) is not None or
                       re.search(r'[\w\s]+,\s*\d+[-–]\d+', c) is not None, JournalCitationParser.parse),
            (lambda c: re.search(r'\((Ed\.?|Eds\.?)\)', c) is not None, BookCitationParser.parse_edited),
            (lambda c: re.search(r'\(pp\.\s*\d+[-–]\d+\)', c) is not None, BookCitationParser.parse_section),
        ]

        for condition, parser in parsers:
            if condition(citation):
                return parser(citation)

        return BookCitationParser.parse_standard(citation)