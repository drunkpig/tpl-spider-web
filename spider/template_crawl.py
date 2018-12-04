import os,re
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

    def __init__(self, url_list, save_base_dir, header, encoding=None, grab_out_site_link=False):
        self.url_list = list(set(list(map(lambda x: format_url(x), url_list))))
        self.save_base_dir = "%s/%s"%(save_base_dir, get_date())
        self.tpl_mapping = self.__get_tpl_replace_url(url_list)
        self.domain = get_domain(url_list[0])
        self.tpl_dir, self.js_dir, self.img_dir, self.css_dir, self.other_dir = self.__prepare_dirs()
        self.dl_urls = {}  # 去重使用,存储 url=>磁盘绝对路径
        self.error_grab_resource = {}  # 记录 http url => relative url ，最后生成一个报告打包
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
            if self.charset is None:
                self.charset = chardet.detect(ctx.content)['encoding']

            ctx.encoding = self.charset
            html = ctx.text

            # html = html.encode()
            tpl_html = self.__rend_template(url, html)
            tpl_file_name = self.__get_file_name(url, i)
            save_file_path = "%s/%s" % (self.__get_tpl_full_path(), tpl_file_name)
            self.__save_text_file(str(tpl_html), save_file_path)
            self.dl_urls[url] = save_file_path
            i += 1

        self.__make_report()
        self.__make_zip(self.__get_zip_full_path())

    def __get_relative_report_file_path(self, path):
        return path[len(self.__get_tpl_full_path())+1:]

    def __make_report(self):
        """
        1，标题
        2，源url
        3，error url
        4，ok url
        :return:
        """
        report_file = "%s/_report.html"%(self.__get_tpl_full_path())
        with open(report_file, 'w+', encoding='utf-8') as f:
            f.writelines("""
                <center><h1>TEMPLATE REPORT</h1></center><br>\n
                
                <h2 style='color: red;'>1. Error report</h2><br>\n
            """)
            if len(self.error_grab_resource.keys()) >0:
                for url, path in self.error_grab_resource.items():
                    f.writelines("%s &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; => &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; %s <br>\n"%(url, path))
                f.writelines("""
                    <b>To fix this error: download the url content and put them in the directory followed.</b><br>\n
                """)
            else:
                f.writelines("All things is ok!")

            f.writelines("""
                <hr /><br>
                <h2>2. Template source url</h2><br>\n
            """)
            for u in self.url_list:
                f.writelines("<a href='%s'>%s</a><br>\n"%(u, u))

            f.writelines("""
                <hr />
                <h2>3. Spider report (%s files)</h2><br>\n
            """ % len(self.dl_urls.keys()))

            for url, path in self.dl_urls.items():
                f.writelines("<a href='%s'>%s</a> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; =>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; %s<br>\n" % (url, url, self.__get_relative_report_file_path(path)))

            f.writelines("""
                <br><br>
                <hr/>
                <center><a href='http://template-spider.com'>web template spider</a>&nbsp;|&nbsp;<a href=''>report bug</a></center>
            """)

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

    def __log_error_resource(self, url, path):
        self.error_grab_resource[url] = path

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
                如果是外链引入的js就不管了,除非打开了开关
                """
                file_name = get_file_name_by_type(abs_link, ['js'])
                file_save_path = "%s/%s" % (self.__get_js_full_path(), file_name)
                replace_url = "%s/%s"%(self.js_dir, file_name)
                scripts['src'] = replace_url

                if not self.__is_dup(abs_link, file_save_path):
                    resp = self.__get_request(abs_link)
                    file_content = ""
                    if resp is None:    # 抓取失败了
                        self.logger.error("get %s error", abs_link)
                        file_content = "crawl error, please get the link content yourself: %s " % abs_link
                        self.__log_error_resource(abs_link, replace_url)
                    else:
                        file_content = resp.text

                    self.__save_text_file(file_content, file_save_path)   # 存储js文件
                    self.dl_urls[abs_link] = file_save_path

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
            if raw_link is None or raw_link.lower().strip().startswith('data:image'):  # 跳过base64内嵌图片 <img src='data:image...'/>
                continue
            abs_link = get_abs_url(url, raw_link)

            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link:
                file_name = get_url_file_name(abs_link)
                file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                replace_url = "%s/%s" % (self.img_dir, file_name)
                img['src'] = replace_url

                if not self.__is_dup(abs_link, file_save_path):
                    resp = self.__get_request(abs_link)
                    if resp is None:
                        self.logger.error("get %s error", abs_link)
                        self.__save_text_file("crawl error, please get the link content yourself: %s "%abs_link, file_save_path)
                        self.__log_error_resource(abs_link, replace_url)
                    else:
                        self.__save_bin_file(resp, file_save_path)  #存储图片文件

                    self.dl_urls[abs_link] = file_save_path

    def __get_style_url_link(self, url_src):
        """
        url('xxxx')
        url("xxxx")
        url(xxxx)
        :param url_src:
        :return:  xxxx
        """
        url_src = url_src.strip()
        if '"' in url_src or "'" in url_src:
            return url_src[5: -2].strip()
        else:
            return url_src[4: -1].strip()

    def __dl_inner_style_img(self, soup, url):
        """
        获取到html页面内嵌样式的图片资源
        <xx style='background: url(xxxxx.jpg)'>
        :param soup:
        :param url:
        :return:
        """
        inner_style_node = soup.find_all(style=re.compile("url(.*?)"))  # TODO url/URL 大小写
        for style in inner_style_node:
            resource_url = re.findall('url\(.*?\)', style.get("style"))[0] # TODO 便利匹配到的全部
            resource_url = self.__get_style_url_link(resource_url)
            if resource_url.lower().startswith("data:image"):  # 内嵌base64图片
                continue
            abs_link = get_abs_url(url, resource_url)

            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link:
                file_name = get_url_file_name(abs_link)
                file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                replace_url = "%s/%s"%(self.img_dir, file_name)
                style['style'] = style['style'].replace(resource_url, replace_url)

                if not self.__is_dup(abs_link, file_save_path):
                    resp = self.__get_request(abs_link)
                    if resp is None:
                        self.logger.error("get %s error", abs_link)
                        self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                              file_save_path)
                        self.__log_error_resource(abs_link, replace_url)
                    else:
                        self.__save_bin_file(resp, file_save_path)  # 存储图片文件

                    self.dl_urls[abs_link] = file_save_path

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
            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link:  # 控制是否抓外链资源
                file_name = get_url_file_name(abs_link)

                resp = self.__get_request(abs_link)
                if resp is not None:
                    if "image" in resp.headers.get("Content-Type"):
                        self.__save_bin_file(resp, "%s/%s" % (self.__get_img_full_path(), file_name))  # 存储图片文件
                        replace_url = "%s/%s"%(self.img_dir, file_name)
                    else:
                        text_content = resp.text
                        text_content = self.__replace_and_grab_css_url(abs_link, text_content)
                        self.__save_text_file(text_content, "%s/%s" % (self.__get_css_full_path(), file_name))  # 存储css文件
                        replace_url = "%s/%s" % (self.css_dir, file_name)
                else:
                    self.logger.error("get %s error", abs_link)
                    self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                          "%s/%s" % (self.__get_css_full_path(), file_name))
                    replace_url = "%s/%s" % (self.css_dir, file_name)
                    self.__log_error_resource(abs_link, replace_url)
                css['href'] = replace_url

    def __replace_and_grab_css_url(self, url, text):
        urls = re.findall("url\(.*?\)", text)
        for u in urls:
            relative_u = self.__get_style_url_link(u)
            if relative_u.lower().startswith("data:image"):  # 内嵌base64图片
                continue
            abs_link = get_abs_url(url, relative_u)
            if is_same_web_site_link(url, abs_link) is True or self.is_grab_outer_link:  # 控制是否抓外链资源
                file_name = get_url_file_name(abs_link)
                file_save_path = "%s/%s" % (self.__get_css_full_path(), file_name)
                replace_url = "%s" % (file_name) # 由于是相对于css文件的引入,因此是平级关系, 如果是图片就需要从../img目录下
                is_img = is_img_ext(file_name)
                if is_img:
                    file_save_path = "%s/%s" % (self.__get_img_full_path(), file_name)
                    replace_url = "../%s/%s" % (self.img_dir, file_name)

                if not self.__is_dup(abs_link, file_save_path):
                    resp = self.__get_request(abs_link)
                    if resp is None:
                        self.logger.error("get %s error", abs_link)
                        self.__save_text_file("crawl error, please get the link content yourself: %s " % abs_link,
                                              file_save_path)
                        self.__log_error_resource(abs_link, replace_url)
                    else:
                        self.__save_bin_file(resp, file_save_path)  # 存储二进制文件
                        text = text.replace(relative_u, replace_url)

                    self.dl_urls[abs_link] = file_save_path

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
    gb2312 : https://www.jb51.net/web/25623.html
    """
    url_list=[
        'https://stackoverflow.com/questions/13137817/how-to-download-image-using-requests',
        # 'http://boke1.wscso.com/',
        # 'https://www.sfmotors.com/',
        # 'https://www.sfmotors.com/company',
        # 'https://www.sfmotors.com/technology',
        # 'https://www.sfmotors.com/vehicles',
        # 'https://www.sfmotors.com/manufacturing'
    ]

    spider = TemplateCrawler(url_list, save_base_dir=config.template_base_dir, header={'User-Agent':config.default_ua}, grab_out_site_link=True)
    spider.template_crawl()
