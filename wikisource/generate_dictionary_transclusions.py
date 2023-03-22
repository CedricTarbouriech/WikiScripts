"""
    This script generates transclusion pages for a dictionary based on the sections.
"""
import re
from typing import Callable, Tuple, List, Dict

import pywikibot as pwb
from unidecode import unidecode


def extract_entries_and_spans(index_title, start, end, ignore_sections) -> Tuple[List[str], Dict[str, List[int]]]:
    """
    Iterate through the pages of the given index, from page `start` to page `end` (included).
    Extract the entry list based on the sections. Extract the spans of the section.

    :param index_title: the name of the index to search through, without the namespace prefix
        and with the extension suffix (.pdf, .djvu, etc.)
    :param start: the page from which to start the extraction
    :param end: the page to reach to end the extraction
    :param ignore_sections: a function to filter sections, i.e. if the function returns `True`, the section is ignored

    :return: the entry list and the section span
    """
    entries = []
    section_spans = {}
    for page_number in range(start, end + 1):
        page = pwb.Page(site, f"Page:{index_title}/{page_number}")
        for section_name in re.findall(r'<section begin="(.+)"', page.text):
            if ignore_sections(section_name):
                continue
            if section_name not in entries:
                entries.append(section_name)
            if section_name not in section_spans:
                section_spans[section_name] = []
            if page_number in section_spans[section_name]:
                print(f"Erreur sur la page {page_number} avec la section {section_name}")
            section_spans[section_name].append(page_number)
    return entries, section_spans


def generate_transclusions(index_title: str, book_title: str, entries: List[str], section_spans: Dict[str, List[int]],
                           apply_label_style: Callable[[str], str]) -> None:
    number_of_entries = len(entries)
    for entry_index, section_name in enumerate(entries):
        title = section_name
        span = section_spans[section_name]
        page = pwb.Page(site, f"{book_title}/{title}")
        if title[0].lower() != 'D':
            continue
        res = f'<pages index="{index_title}"\n' \
              f'from={span[0]} to={span[-1]}\n' \
              f'fromsection="{section_name}" tosection="{section_name}"'
        if entry_index != 0:
            res += f'prev="[[../{apply_label_style(entries[entry_index - 1])}]]" '
        if entry_index != number_of_entries - 1:
            res += f'next="[[../{apply_label_style(entries[entry_index + 1])}]]" '
        sort_key = unidecode(section_name.lower())
        res += f"header=1 />\n\n[[Catégorie:Articles du {book_title}|{sort_key}]]"
        page.text = res
        page.save("Génération de la page")


def main():
    index_title = "Dictionnaire pratique et historique de la musique.pdf"
    entries, section_spans = extract_entries_and_spans(index_title, 127, 150, lambda x: "Lettre " in x)
    generate_transclusions(index_title, "Dictionnaire pratique et historique de la musique",
                           entries, section_spans, lambda x: x.capitalize())


if __name__ == "__main__":
    site = pwb.Site("fr", "wikisource")
    main()
