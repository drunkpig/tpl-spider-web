import os,re
import zipfile
from logging.config import fileConfig

import chardet,shutil

from spider.request_util import spider_get
from spider.utils import get_date, get_domain, get_abs_url, format_url, get_url_file_name, get_file_name_by_type, \
    is_same_web_site_link, is_img_ext
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import spider.config as config


class TemplateCrawler(object):
    logger = logging.getLogger()

    def __init__(self, url_list, save_base_dir, header, encoding='utf-8', grab_out_site_link=False):
        self.url_list = list(set(list(map(lambda x: format_url(x), url_list))))
        self.save_base_dir = "%s/%s"%(save_base_dir, get_date())
        self.tpl_mapping = self.__get_tpl_replace_url(url_list)
        self.domain = get_domain(url_list[0])
        self.tpl_dir, self.js_dir, self.img_dir, self.css_dir, self.other_dir = self.__prepare_dirs()
        self.dl_urls = {}  #去重使用,存储 url=>磁盘绝对路径
        self.header=header
        self.charset=encoding
        self.is_grab_outer_link = grab_out_site_link

    def template_crawl(self):
        """
        把url_list里的网页全部抓出来当做模版，
        存储到save_path/${date}/目录下

        :param url_list:
        :param save_path:
        :return:
        """
        i = 0
        for url in url_list:
            ctx = self.__get_request(url)
            self.charset = chardet.detect(ctx.content)['encoding']
            html = ctx.text
            tpl_html = self.__rend_template(url, html)
            tpl_file_name = self.__get_file_name(url, i)
            save_file_path = "%s/%s" % (self.__get_tpl_full_path(), tpl_file_name)
            self.__save_text_file(str(tpl_html), save_file_path, encoding=self.charset)
            self.dl_urls[url] = save_file_path
            i += 1

        self.__make_zip(self.__get_zip_full_path())

    def __is_dup(self, url, save_path):
        """
        放置重复抓取
        :param url:
        :param save_path:
        :return:
        """
        if url in self.dl_urls.keys():
            save_path2 = self.dl_urls.get(url)
            if save_path == save_path2:
                self.logger.info("cached %s", url)
                return True

        return False

    def __get_tpl_full_path(self):
        return "%s/%s"%(self.save_base_dir, self.tpl_dir)

    def __get_tpl_dir(self):
        return self.tpl_dir

    def __get_save_base_dir(self):
        return self.save_base_dir

    def __get_zip_full_path(self):
        zip_base_dir = "%s/%s"%(config.template_archive_dir, get_date())
        if not os.path.exists(zip_base_dir):
            os.makedirs(zip_base_dir)
        zip_file_path = "%s/%s"%(zip_base_dir, self.tpl_dir)

        return zip_file_path

    def __get_img_full_path(self):
        return "%s/%s"%(self.__get_tpl_full_path(), self.img_dir)

    def __get_css_full_path(self):
        return "%s/%s" % (self.__get_tpl_full_path(), self.css_dir)

    def __get_js_full_path(self):
        return "%s/%s" % (self.__get_tpl_full_path(), self.js_dir)

    @staticmethod
    def __save_text_file(content, file_abs_path, encoding='utf-8'):
        with open(file_abs_path, "w+", encoding=encoding) as f:
            f.writelines(content)

    @staticmethod
    def __save_bin_file(rsp, file_abs_path):
        with open(file_abs_path, 'wb') as f:
            for chunk in rsp.iter_content(512):
                f.write(chunk)

    def __prepare_dirs(self):
        """
        根据域名+ts命名这个目录
        :return:
        """
        template_dir = "%s_%s"%(self.domain, datetime.now().timestamp())
        tpl_full_dir = "%s/%s" % (self.save_base_dir, template_dir)
        dirs = [tpl_full_dir, "%s/js"%tpl_full_dir, "%s/img"%tpl_full_dir, "%s/css"%tpl_full_dir, "%s/other"%tpl_full_dir]
        for d in dirs:
            if not os.path.exists(d):
                os.makedirs(d)

        return template_dir, "js", "img", "css", "other"

    def __get_file_name(self, url, i):
        return "index_%s.html"%i

    def __get_tpl_replace_url(self, url_list):
        """
        模版中的链接地址要替换掉,生成一份 url全路径->磁盘路径的映射替换表
        :param url_list:
        :return:
        """
        url_mp = {}
        i = 0
        for u in url_list:
            url_mp[u] = self.__get_file_name(u, i)
            i += 1

        return url_mp

    def __make_template(self, soup, url):
        """
        下载到的网页里把模版链接替换掉如果有。
        :param soup:
        :param url:
        :return:
        """
        for base_tag in soup.find_all("base"):  # 删除<base>标签
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
                    tpl_link = self.tpl_mapping.get(abs_link)
                    a['href'] = tpl_link
        except Exception as e:
            self.logger.info("%s: %s", a, e)
            self.logger.exception(e)
            raise e

    def __dl_js(self, soup, url):
        """
        下载js，替换html里js文件的地址
        :param soup:
        :param url:
        :return:
        """
        scripts_urls = soup.find_all("script")
        for scripts in scripts_urls:
            raw_link = scripts.get("src")
            if raw_link is None:
                continue
            abs_link = get_abs_url(url, raw_link)

            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link:
                """
                如果是外链引入的js就不管了
                """
                file_name = get_file_name_by_type(abs_link, ['js'])
                file_save_path = "%s/%s" % (self.__get_js_full_path(), file_name)

                if not self.__is_dup(abs_link, file_save_path):
                    resp = self.__get_request(abs_link)
                    if resp is None:
                        self.logger.error("get %s error", abs_link)
                        file_name = "%s.txt" % file_name
                        file_save_path = "%s/%s" % (self.__get_js_full_path(), file_name)
                        self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                              file_save_path)
                    self.__save_text_file(resp.text, file_save_path)  #存储js文件
                    self.dl_urls[abs_link] = file_save_path

                scripts['src'] = "%s/%s"%(self.js_dir, file_name)

    def __dl_img(self, soup, url):
        """
        下载图片，并替换html里图片的地址
        :param soup:
        :param url:
        :return:
        """
        images = soup.find_all("img")
        for img in images:
            raw_link = img.get("src")
            if raw_link is None:
                continue
            abs_link = get_abs_url(url, raw_link)
            file_name = get_url_file_name(abs_link)
            file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)

            if not self.__is_dup(abs_link, file_save_path):
                resp = self.__get_request(abs_link)
                if resp is None:
                    self.logger.error("get %s error", abs_link)
                    file_name = "%s.txt"%file_name
                    file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                    self.__save_text_file("crawl error, please get the link content yourself: %s "%abs_link, file_save_path)
                else:
                    self.__save_bin_file(resp, file_save_path)  #存储图片文件
                    self.dl_urls[abs_link] = file_save_path

            img['src'] = "%s/%s"%(self.img_dir, file_name)

    def __dl_inner_style_img(self, soup, url):
        """
        获取到内嵌样式的图片资源
        :param soup:
        :param url:
        :return:
        """
        inner_style_node = soup.find_all(style=re.compile("url(.*?)"))
        for style in inner_style_node:
            reource_url = re.findall('url\(.*?\)', style.get("style"))[0][5:-2]
            abs_link = get_abs_url(url, reource_url)
            file_name = get_url_file_name(abs_link)
            file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)

            if not self.__is_dup(abs_link, file_save_path):
                resp = self.__get_request(abs_link)
                if resp is None:
                    self.logger.error("get %s error", abs_link)
                    file_name = "%s.txt" % file_name
                    file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                    self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                          file_save_path)
                else:
                    self.__save_bin_file(resp, file_save_path)  # 存储图片文件
                    self.dl_urls[abs_link] = file_save_path

            style['style'] = style['style'].replace(reource_url, "%s/%s"%(self.img_dir, file_name))

    def __dl_link(self, soup, url):
        """
        下载<link>标签里的资源，并替换html里的地址
        :param soup:
        :param url:
        :return:
        """
        css_src = soup.find_all("link")
        for css in css_src:
            raw_link = css.get("href")
            if raw_link is None:
                continue
            abs_link = get_abs_url(url, raw_link)
            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link: # 不是外链
                file_name = get_url_file_name(abs_link)

                resp = self.__get_request(abs_link)
                if resp is not None:
                    if "image" in resp.headers.get("Content-Type"):
                        self.__save_bin_file(resp, "%s/%s" % (self.__get_img_full_path(), file_name))  # 存储图片文件
                        css['href'] = "%s/%s"%(self.img_dir, file_name)
                    else:
                        text_content = resp.text
                        text_content = self.__replace_and_grab_css_url(abs_link, text_content)
                        self.__save_text_file(text_content, "%s/%s" % (self.__get_css_full_path(), file_name))  # 存储css文件
                        css['href'] = "%s/%s" % (self.css_dir, file_name)
                else:
                    self.logger.error("get %s error", abs_link)
                    file_name = "%s.txt" % file_name
                    file_save_path = "%s/%s" % (self.__get_css_full_path(), file_name)
                    self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                          file_save_path)
                    css['href'] = "%s/%s" % (self.css_dir, file_name)

    def __replace_and_grab_css_url(self, url, text):
        urls = re.findall("url\(.*?\)", text)
        for u in urls:
            relative_u = u.strip()[5:-2]
            abs_url = get_abs_url(url, relative_u)
            file_name = get_url_file_name(abs_url)
            file_save_path = "%s/%s" % (self.__get_css_full_path(), file_name)
            replace_url = "%s/%s" % (self.css_dir, file_save_path)
            is_img = is_img_ext(file_name)
            if is_img:
                file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                replace_url = "%s/%s" % (self.img_dir, file_save_path)

            if not self.__is_dup(abs_url, file_save_path):
                resp = self.__get_request(abs_url)
                if resp is None:
                    self.logger.error("get %s error", abs_url)
                    file_name = "%s.txt" % file_name
                    file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                    self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_url,
                                          file_save_path)
                    replace_url = "%s/%s"%(self.img_dir, file_name)
                else:
                    self.__save_bin_file(resp, file_save_path)  # 存储图片文件
                    text = text.replace(relative_u, replace_url)
                self.dl_urls[abs_url] = replace_url

        return text


    def __rend_template(self, url, html):
        """
        把从url抓到的html原始页面进行链接加工，图片，css,js下载
        :param url:
        :param html:
        :return:
        """
        soup = BeautifulSoup(html, "lxml")
        self.__make_template(soup, url)
        self.__dl_inner_style_img(soup, url)
        self.__dl_js(soup, url)
        self.__dl_img(soup, url)
        self.__dl_link(soup, url)

        return soup.prettify()

    def __get_request(self, url):
        return spider_get(url, self.header)

    def __make_zip(self, zip_full_path):
        shutil.make_archive(zip_full_path, 'zip', self.__get_save_base_dir(), base_dir=self.__get_tpl_dir())
        self.logger.info("zip file %s make ok", zip_full_path)
        shutil.rmtree(self.__get_tpl_full_path())


if __name__=="__main__":
    fileConfig('logging.ini')
    """
    动态渲染的： 'https://docs.python.org/3/library/os.html',http://www.gd-n-tax.gov.cn/gdsw/index.shtml
    需要UA：'https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests',
    """
    url_list=[
        # 'http://boke1.wscso.com/'
        'https://www.sfmotors.com/',
        # 'https://www.sfmotors.com/company',
        # 'https://www.sfmotors.com/technology',
        # 'https://www.sfmotors.com/vehicles',
        # 'https://www.sfmotors.com/manufacturing'
    ]

    spider = TemplateCrawler(url_list, save_base_dir=config.template_base_dir, header={'User-Agent':config.default_ua}, grab_out_site_link=False)
    spider.template_crawl()
