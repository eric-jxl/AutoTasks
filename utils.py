import time
import requests
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retry_on_exception(max_retries=3, initial_delay=1, backoff_factor=2, exceptions=(Exception,)):
    """
    装饰器：在遇到指定异常时重试函数调用。

    :param max_retries: 最大重试次数
    :param initial_delay: 初始延迟时间（秒）
    :param backoff_factor: 退避因子，每次重试后延迟时间乘以该因子
    :param exceptions: 需要捕获并重试的异常类型
    :return: 装饰器
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    retries += 1
                    logger.warning(
                        f"函数 '{func.__name__}' 抛出异常: {e}. 正在重试 ({retries}/{max_retries})...")
                    time.sleep(delay)
                    delay *= backoff_factor
            logger.error(
                f"函数 '{func.__name__}' 达到最大重试次数 ({max_retries})，最终失败。")

        return wrapper
    return decorator


@retry_on_exception(max_retries=5, initial_delay=1, backoff_factor=2, exceptions=(requests.exceptions.RequestException,))
def fetch_data(url):
    """
    发送GET请求到指定的URL并返回JSON响应。

    :param url: 请求的URL
    :return: JSON响应
    """
    response = requests.get(url)
    response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError
    return response.json()


if __name__ == "__main__":
    url = "http://sec-eversec.bilibili.co/api/util/open-api/list"
    try:
        data = fetch_data(url)
        logger.info(f"请求成功，数据如下：{data}")
    except requests.exceptions.RequestException as e:
        logger.error(f"请求最终失败: {e}")
