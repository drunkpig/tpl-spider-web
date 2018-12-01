import requests


def spider_get(url):
    return requests.get(url, timeout=10)
