CONFIG = {
    'timeout': 10,
    'sleep_time': 0.5,  # 下载图片休眠时间
    'max_retries': 3,  # 最大重试请求数
    'image_folder': '漫画图片2',
    "manga_id": "207622",  # 下载漫画的id值
    "get_page": 6,  # 下载章节数
    "is_first_sort": False,  # 是否从第一章开始
    "is_vip": True  # 想开启必须填写下方的PARAMS参数内容
}

PARAMS = {
    # 有这两个参数可以下载VIP的章节
    "sign": "00d06ad18cda8d3300cb1a46440c6400",  # 缓存数据，用户登录token 疑似服务器直接返回，可能有时效
    "uid": "76512682"  # 缓存数据
}

"""
一个小的猜测，这个数据sign是通过服务器返回的，并且有一定的失效性，或许是打开的标签关闭就销毁，如果是这种情况，就必须
保持漫客栈的标签处于打开状态。
"""
