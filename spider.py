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


def get_pages(total_pages, to_dir):
    workers = 16
    url_mode = 'http://konachan.net/post?page=%s&tags='
    xpath_images = "//a[@class='directlink largeimg' or @class='directlink smallimg']/@href"
    if not os.path.exists(to_dir):
        os.makedirs(to_dir)

    for page in range(1, total_pages):
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


if __name__ == '__main__':
    get_pages(total_pages=10000, to_dir='./images_download')
