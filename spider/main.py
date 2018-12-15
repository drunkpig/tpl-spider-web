import logging
from logging.config import fileConfig
from multiprocessing import Process
import threading
import spider.config as config
import spider.config as dbconfig
import time
import json
from spider.template_crawl import TemplateCrawler
import psycopg2
import random


"""

"""
db = psycopg2.connect(database=dbconfig.db_name, user=dbconfig.db_user, password=dbconfig.db_psw,
                      host=dbconfig.db_url, port=dbconfig.db_port)


def __get_a_task():
    sql = """
        update spider_task set status = 'P' where id in (
            select id
            from spider_task
            where status ='I'
            order by gmt_created DESC 
            limit 1
        )
        returning id, seeds, ip, user_id_str, user_agent, status, is_grab_out_link, gmt_modified, gmt_created;
    """
    cursor = db.cursor()
    cursor.execute(sql)
    row = cursor.fetchone()
    if row is None:
        return None

    r = row
    cursor.close()
    task = {
        'id': r[0],
        'seeds': json.loads(r[1]),
        'ip': r[2],
        'user_id_str': r[3],
        'user_agent':r[4],
        'status': r[5],
        'is_grab_out_link': r[6],
        'gmt_modified':r[7],
        'gmt_created': r[8],
    }

    return task


def __save_crawl_result(task_id,  zip_path):
    sql = f"""
        update spider_task set result='{zip_path}' where id={task_id};
    """
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()


def __get_user_agent(key):
    ua_list = config.ua_list.get(key)
    if ua_list is None:
        ua = config.default_ua
    else:
        return random.choice(ua_list)

    return ua


def __process_thread():
    logger = logging.getLogger()
    while True:
        task = __get_a_task()
        if not task:
            logger.info("no task, wait")
            time.sleep(10)
            continue
        seeds = task['seeds']
        is_grab_out_site_link = task['is_grab_out_link']
        user_agent = __get_user_agent(task['user_agent'])
        spider = TemplateCrawler(seeds, save_base_dir=config.template_base_dir,
                                 header={'User-Agent': user_agent},
                                 grab_out_site_link=is_grab_out_site_link)
        template_zip_file = spider.template_crawl()
        __save_crawl_result(task['id'], template_zip_file)


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
    fileConfig('logging.ini')
    process = __create_process()
    process[0].join()
    db.close()
