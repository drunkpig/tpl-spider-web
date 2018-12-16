import requests,logging
import config


logger = logging.getLogger()


def spider_get(url, header):
    max_retry = config.max_retry
    time_out = config.http_timeout

    for i in range(1,max_retry+1):
        to = time_out*i
        try:
            logger.info("start craw[%s] %s" % (i, url))
            resp = requests.get(url, timeout=to, headers=header)
            return resp
        except Exception as e:
            if i<max_retry:
                continue
            else:
                return None
