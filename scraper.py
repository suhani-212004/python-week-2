

import csv
import time
import logging
import requests
from bs4 import BeautifulSoup



BASE_URL   = "http://books.toscrape.com/catalogue/"
START_URL  = "http://books.toscrape.com/catalogue/page-1.html"
OUTPUT_CSV = "books.csv"
DELAY_SEC  = 1.0
TIMEOUT    = 10       

FIELDNAMES = ["title", "price", "rating", "availability", "category", "url"]

# Map word-ratings to numbers
RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s"
)



def get_page(url: str) -> BeautifulSoup | None:
    """
    Fetch a URL and return a BeautifulSoup object.
    Returns None on HTTP or connection errors.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.HTTPError as e:
        logging.error("HTTP error for %s: %s", url, e)
    except requests.exceptions.ConnectionError:
        logging.error("Connection error for %s", url)
    except requests.exceptions.Timeout:
        logging.error("Timeout for %s", url)
    return None



def get_book_category(book_url: str) -> str:
    """
    Fetch the individual book page to extract its breadcrumb category.
    Returns 'Unknown' if anything goes wrong.
    """
    soup = get_page(book_url)
    if not soup:
        return "Unknown"
    breadcrumbs = soup.select("ul.breadcrumb li")
   
    if len(breadcrumbs) >= 3:
        return breadcrumbs[-2].get_text(strip=True)
    return "Unknown"


def parse_books(soup: BeautifulSoup) -> list[dict]:
    """Extract all books from a single catalogue page."""
    books = []
    articles = soup.select("article.product_pod")

    for article in articles:
       
        title_tag = article.select_one("h3 > a")
        title = title_tag["title"] if title_tag else "N/A"

        price_tag = article.select_one("p.price_color")
        price = price_tag.get_text(strip=True) if price_tag else "N/A"

        rating_tag = article.select_one("p.star-rating")
        rating_word = rating_tag["class"][1] if rating_tag else "Zero"
        rating = RATING_MAP.get(rating_word, 0)

        avail_tag = article.select_one("p.availability")
        availability = avail_tag.get_text(strip=True) if avail_tag else "N/A"

 
        href = title_tag["href"] if title_tag else ""
     
        book_url = BASE_URL + href.replace("../../", "")

        category = get_book_category(book_url)
        logging.info("  Scraped: %s [★%s | %s]", title[:50], rating, category)
        time.sleep(DELAY_SEC)   
        books.append({
            "title":        title,
            "price":        price,
            "rating":       rating,
            "availability": availability,
            "category":     category,
            "url":          book_url,
        })

    return books


def get_next_page_url(soup: BeautifulSoup) -> str | None:
    """Return the URL of the next page, or None if we're on the last page."""
    next_btn = soup.select_one("li.next > a")
    if next_btn:
        return BASE_URL + next_btn["href"]
    return None




def save_to_csv(books: list[dict], filename: str):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(books)
    logging.info("Saved %d records to %s", len(books), filename)



def main():
    all_books  = []
    page_url   = START_URL
    page_num   = 1

    logging.info("Starting scrape of books.toscrape.com …")

    while page_url:
        logging.info("── Page %d: %s", page_num, page_url)
        soup = get_page(page_url)
        if not soup:
            logging.warning("Could not load page %d — stopping.", page_num)
            break

        books = parse_books(soup)
        all_books.extend(books)
        logging.info("Page %d done. Books so far: %d", page_num, len(all_books))

        page_url = get_next_page_url(soup)
        page_num += 1
        time.sleep(DELAY_SEC)

    if all_books:
        save_to_csv(all_books, OUTPUT_CSV)
        print(f"\n✓ Scraping complete. {len(all_books)} books saved to {OUTPUT_CSV}")
    else:
        print("No data scraped. Check your network connection.")


if __name__ == "__main__":
    main()
