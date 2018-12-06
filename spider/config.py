http_timeout = 15
max_retry = 3
template_base_dir = "d:/tpl-spider/temp/"
template_archive_dir="d:/tpl-spider/archive/"
default_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
page_default_encoding='utf-8'

download_thread_per_template = 2   # 下载一个模版开启几个额外的线程
url_download_queue_timeout = 3  # 轮询一个url超时时间
wait_url_sleep_time = 2
max_spider_all_sys = 50  # 一个机器最大可以有多少个模版爬虫同时运行

wait_download_finish_sleep = 5
