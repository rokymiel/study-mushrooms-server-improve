import hydra as hydra
from bs4 import BeautifulSoup
import requests
import re

from omegaconf import DictConfig

from common.constants import classnames
from parser.managers import MushroomsManager


def read_name_and_classname(article):
    try:
        name = article.find('h2').string
        classname = name[name.index('(') + 1:name.index(')')]
    except Exception:
        head = article.find('h2')
        name = head.get_text()
        classname = name[name.index('(') + 1:name.index(')')]
    return name, classname


def read_picture_link(article, soup):
    try:
        picture_link = soup.find('div', {'class': 'google_imgs'}).find('href')
    except:
        picture_link = article.find('img')['src']
    if picture_link is None:
        picture_link = article.find('img')['src']
    return picture_link


def read_description(article):
    k = filter(None.__ne__, [el.string for el in article.findAll('p')])
    try:
        description = article.text
    except:
        description = "\n".join(k)
    return description


def read_soup_and_article(item):
    # ex. "https://wikigrib.ru/ejovik-belyj/"
    soup = BeautifulSoup(requests.get(item, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    }).content, 'html.parser')
    article = soup.find('div', {'class': 'entry'})

    return soup, article


def read_links(url, page_num):
    page = requests.get(url + 'page/' + str(page_num), headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
    })
    page_soup = BeautifulSoup(page.content, 'html.parser')
    mushroom_list = page_soup.find('div', {'class': 'catcont-list'})

    if mushroom_list is None:
        return None

    return list(
        map(lambda x: x.find('a').get('href'),
            mushroom_list.findAll('section', {'class': re.compile('post post*')})))


def load_mushrooms(base_urls, classnames, m_manager):
    m_manager.reset_mushrooms()

    error_links = []
    for url, type in base_urls:
        for i in range(1, 100):
            links = read_links(url, i)

            if links is None: break

            for item in links:
                print("link:", item)

                try:
                    soup, article = read_soup_and_article(item)
                    name, classname = read_name_and_classname(article)

                    if classname not in classnames:
                        continue

                    picture_link = read_picture_link(article, soup)
                    description = read_description(article)

                    m_manager.save_new_mushroom(name, classname, picture_link, description, type)
                except Exception:
                    print('exc caught')
                    error_links.append(item)


@hydra.main(config_path="configs", config_name="parse")
def main(cfg: DictConfig) -> None:
    base_urls = cfg.base_urls

    load_mushrooms(base_urls, classnames, MushroomsManager())


if __name__ == "__main__":
    main()
