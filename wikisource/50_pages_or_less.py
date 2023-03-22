import re

import pywikibot as pwb

# Structure des données :
# { [0]=a,b,c,d,e,m=f }
# Par exemple :{ [0]=12,1,0,48,18,m=363 }
# a : nombre de pages grises (rang 0)
# b : nombre de pages rouges (rang 1)
# c : nombre de pages avec des erreurs (rang 2)
# d : nombre de pages jaunes (rang 3)
# e : nombre de pages vertes (rang 4)
# f : nombre de pages manquantes (rang 5)

CAT_A_CORRIGER = "[[Catégorie:50 pages ou moins à corriger]]"
CAT_A_VALIDER = "[[Catégorie:50 pages ou moins à valider]]"

pwb._config.put_throttle = 0

site = pwb.Site("fr", "wikisource")

# Prepare data
data_page = pwb.Page(site, "Module:ProofreadStats/Data")
lines = data_page.text.split("\n")[2:-1]
data = {}
for line in lines:
    s = re.split(r"\[ \[\[(Livre:.+)]] ] = { \[0]=(\d+),(\d+),(\d+),(\d+),(\d+),m=(-?\d+) },", line)[1:-1]
    data[s[0]] = list(map(int, s[1:]))


def get_nb_red_pages(title: str) -> int:
    values = data[title]
    return values[1] + values[5]


def get_nb_yellow_pages(title: str) -> int:
    values = data[title]
    return values[3]


def treat_book(book: pwb.Page) -> None:
    title = book.title()
    if title.endswith(".jpg") or title.endswith(".png"):
        return

    if title not in data:
        book.text = book.text.replace(CAT_A_CORRIGER, "").replace(CAT_A_VALIDER, "")
        book.save("Retrait de la catégorie (livre absent des données : [[Module:ProofreadStats/Data]])")
        return

    red_pages = get_nb_red_pages(title)
    yellow_pages = get_nb_yellow_pages(title)

    if red_pages > 50:
        text = book.text.replace(CAT_A_CORRIGER, "").replace(CAT_A_VALIDER, "")
        if book.text != text:
            book.text = text
            book.save("Retrait de la catégorie (plus de 50 pages rouges)")
        return
    if 0 < red_pages <= 50:
        if CAT_A_CORRIGER not in book.text:
            if CAT_A_VALIDER in book.text:
                book.text = book.text.replace(CAT_A_VALIDER, CAT_A_CORRIGER)
            else:
                book.text += f"\n{CAT_A_CORRIGER}"
            book.save(f"Ajout de la catégorie {CAT_A_CORRIGER}")
        return
    if yellow_pages > 50 and CAT_A_VALIDER in book.text:
        book.text = book.text.replace(CAT_A_VALIDER, "")
        book.save("Retrait de la catégorie (plus de 50 pages jaunes)")
    if 0 < yellow_pages <= 50 and CAT_A_VALIDER not in book.text:
        if CAT_A_CORRIGER in book.text:
            book.text = book.text.replace(CAT_A_CORRIGER, CAT_A_VALIDER)
        else:
            book.text += f"\n{CAT_A_VALIDER}"
        book.save(f"Ajout de la catégorie {CAT_A_VALIDER}")


for book_title in data.keys():
    treat_book(pwb.Page(site, book_title))

map(treat_book, pwb.Category(site, "Catégorie:50 pages ou moins à corriger").articles())
map(treat_book, pwb.Category(site, "Catégorie:50 pages ou moins à valider").articles())
