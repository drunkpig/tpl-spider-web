from multiprocessing import Process
import threading
import spider.config as config
import spider.config as dbconfig
import time
import json
from spider.template_crawl import TemplateCrawler
import psycopg2


"""

"""

db = psycopg2.connect(database=dbconfig.db_name, user=dbconfig.db_user, password=dbconfig.db_psw,
                      host=dbconfig.db_url, port=dbconfig.db_port)


def __get_a_task():
    sql = """
        select id, seeds, ip , user_id_str, status, is_grab_out_link, gmt_created from spider_task limit 1;
    """
    cursor = db.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    r = row[0]
    cursor.close()
    task = {
        'id': r[0],
        'seeds': json.loads(r[1]),
        'ip': r[2],
        'user_id_str': r[3],
        'status': r[4],
        'is_grab_out_link': r[5],
        'gmt_created': r[6],
    }

    return task


def __process_thread():
    while True:
        task = __get_a_task()
        if not task:
            time.sleep(10)
            continue
        seeds = task['seeds']
        is_grab_out_site_link = task['is_grab_out_link']
        user_agent = task['user_agent']
        spider = TemplateCrawler(seeds, save_base_dir=config.template_base_dir,
                                 header={'User-Agent': user_agent},
                                 grab_out_site_link=is_grab_out_site_link)
        spider.template_crawl()


def __create_thread(n):
    threads = []
    for i in range(0, n):
        t = threading.Thread(target=__process_thread)
        threads.append(t)
        t.start()

    threads[0].join()


def __create_process():
    process = []
    process_cnt = config.max_spider_process
    thread_per_process = config.max_spider_thread_per_process

    for i in range(0, process_cnt):
        p = Process(target=__create_thread, args=(thread_per_process,))
        process.append(p)
        p.start()

    return process


if __name__ == "__main__":
    process = __create_process()
    process[0].join()
