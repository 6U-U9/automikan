import logging
logger = logging.getLogger(__name__)
import time
import requests

class Request:
    def __init__(self, header, proxy = None):
        self.session = requests.Session()
        self.header = header
        self.proxy = proxy
        if proxy != None:
            self.session.proxies = {
                "http": proxy,
                "https": proxy
            }

    def get(self, url, timeout = 10, retry = 1, retry_interval = 0):
        try_time = 0
        while True:
            try:
                request = self.session.get(url = url, headers = self.header, timeout = timeout)
                logger.debug(f"Send HTTP Get to {url}. Status: {request.status_code}")
                request.raise_for_status()
                return request
            except requests.RequestException:
                logger.debug(f"Cannot connect to {url}. Wait for {retry_interval} seconds.")
                try_time += 1
                if try_time >= retry:
                    break
                time.sleep(retry_interval)
            except Exception as e:
                logger.debug(e, stack_info = True, exc_info = True)
                break
        logger.error(f"Unable to connect to {url}, please check your network")
        return None

    def post(self, url: str, data: dict, timeout = 10, retry = 1, retry_interval = 0):
        try_time = 0
        while True:
            try:
                request = self.session.post(url = url, headers = self.header, data = data, timeout = timeout)
                logger.debug(f"Send HTTP Post to {url}. Status: {request.status_code}")
                request.raise_for_status()
                return request
            except requests.RequestException:
                logger.debug(f"Cannot connect to {url}. Wait for {retry_interval} seconds.")
                try_time += 1
                if try_time >= retry:
                    break
                time.sleep(retry_interval)
            except Exception as e:
                logger.debug(e, stack_info = True, exc_info = True)
                break
        logger.error(f"Unable to connect to {url}, please check your network")
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()