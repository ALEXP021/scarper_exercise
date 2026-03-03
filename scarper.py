import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
from fake_useragent import UserAgent

def get_random_headers():
    ua = UserAgent()
    return {'User-Agent': ua.random}

def parse_page(url):
    """parses one page and returns a list of quotes."""
    try:
        response = requests.get(url, headers=get_random_headers(), timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
        return [], None

    soup = BeautifulSoup(response.text, 'lxml')
    quotes = []

    for quote_block in soup.find_all('div', class_='quote'):
        text = quote_block.find('span', class_='text').get_text(strip=True)
        author = quote_block.find('small', class_='author').get_text(strip=True)
        tags = [tag.get_text(strip=True) for tag in quote_block.find_all('a', class_='tag')]

        quotes.append({
            'text': text,
            'author': author,
            'tags': ', '.join(tags)
        })

    # Ищем ссылку на следующую страницу
    next_btn = soup.find('li', class_='next')
    next_url = None
    if next_btn:
        next_page = next_btn.find('a')['href']
        # формируем полный URL
        if 'page' in url:
            base_url = url[:url.rfind('/')]
            next_url = base_url + '/' + next_page
        else:
            next_url = url.rstrip('/') + '/' + next_page

    return quotes, next_url

def scrape_all(base_url='http://quotes.toscrape.com'):
    """Collects all quotes from all pages."""
    all_quotes = []
    url = base_url
    page_num = 1

    while url:
        print(f"Page parsing {page_num}: {url}")
        quotes, next_url = parse_page(url)
        if not quotes:
            print("No data on page, stopping.")
            break

        all_quotes.extend(quotes)
        url = next_url
        page_num += 1

        time.sleep(1)  # polite delay

    return all_quotes

if __name__ == "__main__":
    data = scrape_all()
    print(f"Total quotes collected: {len(data)}")

    # Save in CSV
    df = pd.DataFrame(data)
    df.to_csv('quotes.csv', index=False, encoding='utf-8')
    print("Data saved in quotes.csv")