import os

from spider.request_util import spider_get
from spider.utils import get_date, get_domain, get_abs_url, format_url, get_url_file_name, get_file_name_by_type, \
    is_same_web_site_link
from datetime import datetime
from bs4 import BeautifulSoup
import logging


logger = logging.getLogger()


def __save_text_file(content, file_abs_path, encoding='utf-8'):
    with open(file_abs_path, "w+", encoding=encoding) as f:
        f.writelines(content)


def __save_bin_file(rsp, file_abs_path):
    with open(file_abs_path, 'wb') as f:
        for chunk in rsp.iter_content(512):
            f.write(chunk)


def __prepare_dirs(save_path, one_url):
    """
    TODO 根据域名命名这个目录
    :param one_url:
    :return:
    """
    template_dir = "%s_%s"%(get_domain(one_url), datetime.now().timestamp())
    tpl_dir = "%s/%s/%s" % (save_path, get_date(), template_dir)
    dirs = [tpl_dir, "%s/js"%tpl_dir, "%s/img"%tpl_dir, "%s/css"%tpl_dir]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)

    return tpl_dir, "js", "img", "css"


def __get_file_name(url, i):
    return "index_%s.html"%i


def __get_tpl_replace_url(url_list):
    """
    模版中的链接地址要替换掉
    :param url_list:
    :return:
    """
    url_mp = {}
    i = 0
    for u in url_list:
        url_mp[u] = __get_file_name(u, i)
        i += 1

    return url_mp


def __make_template(soup, url, tpl_mapping, url_list):
    for base_tag in soup.find_all("base"):
        base_tag.decompose()

    a_list = soup.find_all("a")

    """
        遍历全部的链接：
        如果链接的绝对路径在url_list里：
            替换为模版的最终保存的地址
    """
    try:
        for a in a_list:
            raw_link = a.get("href")
            if raw_link is None:
                continue
            abs_link = get_abs_url(url, raw_link)
            if abs_link in url_list:
                tpl_link = tpl_mapping.get(abs_link)
                a['href'] = tpl_link
    except Exception as e:
        logger.info("%s: %s", a, e)
        logger.exception(e)
        raise e


def __dl_js(soup, url, tpl_mapping, url_list, tpl_dir, js_dir):
    scripts_urls = soup.find_all("script")
    for scripts in scripts_urls:
        raw_link = scripts.get("src")
        if raw_link is None:
            continue
        abs_link = get_abs_url(url, raw_link)

        if is_same_web_site_link(url, abs_link) is True:
            """
            如果是外链引入的js就不管了
            """
            file_name = get_file_name_by_type(abs_link, 'js')
            ctx = spider_get(abs_link)
            __save_text_file(ctx.text, "%s/%s/%s" % (tpl_dir, js_dir, file_name))  #存储js文件

            scripts['src'] = "%s/%s"%(js_dir, file_name)


def __dl_img(soup, url, tpl_mapping, url_list, tpl_dir, img_dir):
    images = soup.find_all("img")
    for img in images:
        raw_link = img.get("src")
        if raw_link is None:
            continue
        abs_link = get_abs_url(url, raw_link)
        file_name = get_url_file_name(abs_link)
        resp = spider_get(abs_link)
        __save_bin_file(resp, "%s/%s/%s" % (tpl_dir, img_dir, file_name))  #存储图片文件

        img['src'] = "%s/%s"%(img_dir, file_name)


def __dl_css(soup, url, tpl_mapping, url_list, tpl_dir, css_dir):
    css_src = soup.find_all("link", rel="stylesheet")
    for css in css_src:
        raw_link = css.get("href")
        if raw_link is None:
            continue
        abs_link = get_abs_url(url, raw_link)
        if is_same_web_site_link(url, abs_link) is True:
            file_name = get_file_name_by_type(abs_link, 'css')
            ctx = spider_get(abs_link)
            __save_text_file(ctx.text, "%s/%s/%s" % (tpl_dir, css_dir, file_name))  #存储js文件

            css['href'] = "%s/%s"%(css_dir, file_name)


def __rend_template(url, html, tpl_mapping, url_list, tpl_dir, js_dir, img_dir, css_dir):
    soup = BeautifulSoup(html, "lxml")
    __make_template(soup, url, tpl_mapping, url_list)
    __dl_js(soup, url, tpl_mapping, url_list, tpl_dir, js_dir)
    __dl_img(soup, url, tpl_mapping, url_list, tpl_dir, img_dir)
    __dl_css(soup, url, tpl_mapping, url_list, tpl_dir, css_dir)

    return soup.prettify()


def template_crawl(url_list, save_path):
    """
    把url_list里的网页全部抓出来当做模版，
    存储到save_path/${date}/目录下

    :param url_list:
    :param save_path:
    :return:
    """
    tpl_mapping = __get_tpl_replace_url(url_list)
    tpl_dir, js_dir, img_dir, css_dir = __prepare_dirs(save_path, url_list[0])

    i = 0
    for url in url_list:
        ctx = spider_get(url)
        html = ctx.text
        tpl_html = __rend_template(url, html, tpl_mapping, url_list, tpl_dir=tpl_dir, js_dir=js_dir, img_dir=img_dir, css_dir=css_dir)
        save_file_path = "%s/%s"%(tpl_dir, __get_file_name(url, i) )
        __save_text_file(str(tpl_html), save_file_path)
        i += 1


if __name__=="__main__":
    """
    动态渲染的： 'https://docs.python.org/3/library/os.html',http://www.gd-n-tax.gov.cn/gdsw/index.shtml
    需要UA：'https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests',
    """
    url_list=[
        'https://www.mi.com/',

    ]

    url_list = list(map(lambda x: format_url(x), url_list))
    save_path = "d:/"
    template_crawl(url_list, save_path)
