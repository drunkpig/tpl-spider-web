from datetime import datetime
from urllib.parse import urlparse, urljoin
import uuid

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


def get_url_file_name(url):
    """
    http://a.com?main.css?a=b;c=d;
    http://a.com/a/b/c/xx-dd;a=c;b=d

    :param url:
    :return:
    """
    i = url.rfind("?")
    if i>0:
        start_i = url.rfind("/")
        file_name = url[start_i:i]
        return file_name

    i = url.rfind("=")
    if i>0:
        file_name = url[i + 1:]
    else:
        i = url.rfind("/")
        file_name = url[i + 1:]

    return file_name


def get_file_name_by_type(url, suffix):
    raw_name = get_url_file_name(url)
    if not raw_name.endswith(".%s"%suffix):
        return "%s.%s"%(str(uuid.uuid4()), suffix)
    else:
        return raw_name
