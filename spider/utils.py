from datetime import datetime
from urllib.parse import urlparse, urljoin

"""
urlparse.urlparse("http://some.page.pl/nothing.py;someparam=some;otherparam=other?query1=val1&query2=val2#frag")
ParseResult(scheme='http', netloc='some.page.pl', path='/nothing.py', params='someparam=some;otherparam=other', query='query1=val1&query2=val2', fragment='frag')
"""


def get_date():
    return datetime.now().strftime("%Y-%m-%d")


def get_domain(url):
    """
    some.page.pl
    :param url:
    :return:
    """
    ret = urlparse(url)
    return format_url(ret.netloc)


def get_base_url(url):
    """
    http://some.page.pl
    :param url:
    :return:
    """
    ret = urlparse(url)
    u = "%s://%s"%(ret.schema, ret.netloc)
    return format_url(u)


def format_url(url):
    """
    除去末尾的/, #
    :param url:
    :return:
    """
    ret = urlparse(url)
    fragments = ret.fragment
    url = url[0:len(url)-len(fragments)]
    if url.endswith('/') or url.endswith("#"):
        url = url[:-1]

    return url


def get_abs_url(base_url, raw_link):
    u = urljoin(base_url, raw_link)
    return format_url(u)


def get_url_file_name(script_url):
    """

    :param script_url:
    :return:
    """
    script_file = ""
    i = script_url.rfind("=")
    if i>0:
        script_file = script_url[i+1:]
    else:
        i = script_url.rfind("/")
        script_file = script_url[i+1:]
    return script_file

