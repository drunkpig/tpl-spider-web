import requests,logging

logger = logging.getLogger()


def spider_get(url):
    max_retry = 3
    time_out = 10

    for i in range(1,max_retry+1):
        to = time_out*i
        try:
            logger.info("start craw[%s] %s" % (i, url))
            resp = requests.get(url, timeout=to)
            return resp
        except Exception as e:
            if i<max_retry:
                continue
            else:
                raise e


