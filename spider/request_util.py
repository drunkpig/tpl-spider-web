import requests,logging
import spider.config as config


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


# async def async_spider_get(url, header, file_save_path, file_type='bin'):
#     async with aiohttp.ClientSession() as session:
#         resp = await fetch(session, url, header, file_save_path, file_type)
#         print(resp)
#
#
# async def fetch(session, url, header, file_save_path, file_type):
#     async with session.get(url, headers=header) as response:
#         # TODO 根据文件类型保存二进制或者文本
#         return await response.text()
