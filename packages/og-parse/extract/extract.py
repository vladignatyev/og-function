import os
import requests
from http import HTTPStatus


USER_AGENT = os.environ.get('OG_USER_AGENT', 'TelegramBot (like TwitterBot)')


from bs4 import BeautifulSoup


def _og_extract(soup: BeautifulSoup, exts) -> str:
    out = ''
    for ext in exts:
        try:
            e = ext(soup)
            if e is not None and e.strip() != '':
                out = e
                break
        except:
            pass
    return out


def _og_title_from_soup(soup: BeautifulSoup) -> str:
    exts = [
        lambda soup: soup.select('meta[property="og:title"]')[0].attrs['content'],
        lambda soup: soup.find('title').text,
        lambda soup: soup.find('article h1').text,
        lambda soup: soup.find('h1').text,
        lambda soup: soup.find('article h2').text
    ]
    return _og_extract(soup, exts)


def _og_description_from_soup(soup: BeautifulSoup) -> str:
    exts = [
        lambda soup: soup.select('meta[property="og:description"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="twitter:description"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="description"]')[0].attrs['content'],
        lambda soup: soup.find('article p').text
    ]
    return _og_extract(soup, exts)
    

def _og_image_from_soup(soup: BeautifulSoup) -> str:
    exts = [
        lambda soup: soup.select('meta[property="og:image"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="twitter:image"]')[0].attrs['content'],
        lambda soup: soup.find('figure img').attrs['href']
    ]
    return _og_extract(soup, exts)


def _og_author_from_soup(soup: BeautifulSoup) -> str:
    exts = [
        lambda soup: soup.select('meta[property="og:author"]')[0].attrs['content'],
        lambda soup: soup.select('meta[property="twitter:creator"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="twitter:creator"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="creator"]')[0].attrs['content'],
        lambda soup: soup.select('meta[name="author"]')[0].attrs['content'],
    ]
    return _og_extract(soup, exts)


_EXT = {
    'title':       _og_title_from_soup,
    'description': _og_description_from_soup,
    'image':       _og_image_from_soup,
    'author':      _og_author_from_soup
}


def _extract_opengraph_from_soup(soup: BeautifulSoup, exts: dict = _EXT) -> dict:
    out = {}
    for key, extr in exts.items():
        out[key] = extr(soup)
    return out


def extract_opengraph_from_html(html: str, exts: dict = _EXT) -> dict:
    soup = BeautifulSoup(html, features='lxml')
    return _extract_opengraph_from_soup(soup, exts=exts)


def main(args):
      url = args.get("url", "")

      if not url.startswith('http'):
            return { "statusCode": HTTPStatus.BAD_REQUEST }

      res = requests.get(url, headers={ 'User-Agent': USER_AGENT })
      
      if res.status_code != 200:
            return { "statusCode": HTTPStatus.BAD_REQUEST, "body": f"{res.status_code}" }
      
      return {
            "headers": { 
                  "Content-Type": "application/json" 
            },
            "body": extract_opengraph_from_html(res.content)
      }
