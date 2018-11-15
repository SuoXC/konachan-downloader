import os
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat

import requests
from lxml import etree


def download(image_url, to_dir):
    suffix = image_url.split('.')[-1]
    image_id = image_url.split('/')[-1].split('%20')[2]  # 从url里获取id
    filename = os.path.join(to_dir, "%s.%s" % (image_id, suffix))
    if not os.path.exists(filename):
        try:
            response = requests.get(image_url)
            with open(filename, 'wb') as f:
                f.write(response.content)
                print("downloaded:", filename)
        except Exception as e:
            print("WARNING: image download failed: id=%s, url=%s" % (image_id, image_url))
            print(e)


def get_pages(from_page=1, to_page=10000, to_dir=None, search_keyword=''):
    workers = 16
    url_mode = 'http://konachan.net/post?page=%s&tags=' + search_keyword
    xpath_images = "//a[@class='directlink largeimg' or @class='directlink smallimg']/@href"
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for page in range(from_page, to_page):
        time.sleep(1)
        page_url = url_mode % page
        print("view page:", page, page_url)
        try:
            html = requests.get(page_url).text
        except:
            print("WARNING: request page failed, page=%s, url=%s" % (page, page_url))
            continue
        tree = etree.HTML(html)
        image_urls = tree.xpath(xpath_images)
        print("image count of this page:", len(image_urls))

        with ThreadPoolExecutor(workers) as executor:
            executor.map(download, image_urls, repeat(to_dir), timeout=100)


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--to_dir', required=True, help="saving dir")
    parser.add_argument('--keyword', default='', type=str, help="search keyword")
    parser.add_argument('--from_page', default=1, type=int, help="first page to download")
    parser.add_argument('--to_page', default=10000, type=int, help="last page to download")
    args = parser.parse_args()
    get_pages(from_page=args.from_page, to_page=args.to_page, to_dir=args.to_dir, search_keyword=args.keyword)


if __name__ == '__main__':
    main()
