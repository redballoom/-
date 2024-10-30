import time
from pathlib import Path

import requests
from loguru import logger
from pyquery import PyQuery as pq

from config import CONFIG, PARAMS


class MKZChapter:
    
    def __init__(self):
        self.base_url = "https://www.mkzhan.com"
        self.headers = {
            "referer": "https://www.mkzhan.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
        }
        self.folder = Path('漫画图片2')
        self.folder.mkdir(exist_ok=True)
        self.timeout = CONFIG['timeout']

    def get_chapter_list(self, manga_id):
        """获取漫画章节列表"""
        try:
            url = f"{self.base_url}/{manga_id}/"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            html_text = response.text

            # 解析章节列表
            doc = pq(html_text)
            chapter_list = doc('li a.j-chapter-link')
            if len(chapter_list) == 0:
                logger.warning(f"漫画 {manga_id} 未找到任何章节")
                return []

            chapter_data = []
            for chapter in chapter_list:
                chapter_title = pq(chapter).text().replace('\ue66e', '').strip()
                chapter_id = pq(chapter).attr('data-chapterid')
                if chapter_id and chapter_title:
                    chapter_data.append({'chapter_id': chapter_id, 'title': chapter_title})

            return chapter_data  # [{},{},...]

        except requests.RequestException as e:
            logger.error(f"获取章节列表失败: {e}")
            return []

    def download_chapter(self, chapter_id, comic_id):
        """下载具体章节内容"""
        try:
            url = "https://comic.mkzcdn.com/chapter/content/v1/"
            params = {
                "chapter_id": chapter_id,
                "comic_id": comic_id,
                "format": 1,
                "quality": 1,
                "type": 1,
            }
            # 验证是否下载VIP章节
            params.update(PARAMS) if CONFIG['is_vip'] else params
            response = requests.get(url, headers=self.headers, params=params, timeout=self.timeout)
            response.raise_for_status()
            chapter_image_data = response.json()

            """
            后续添加到数据库思路：
                1. 将 章节图片接口链接 "https://comic.mkzcdn.com/chapter/content/v1/xxxxxxx" 读取到数据库中
                2. 后续继续获取更多的章节时，先从数据库中读取，如果有则跳过，否则添加到数据库并发起请求
                这样的好处是我们已经下载过的章节接口可以不用重复请求，减少了对方服务器的压力，（增量式爬虫的基础）
            """

            if not chapter_image_data.get('data') or not chapter_image_data['data'].get('page'):
                raise ValueError(f'返回数据格式错误: {chapter_image_data}')

            image_urls = chapter_image_data['data']['page']
            if not image_urls:  # 空列表检查
                raise ValueError(f'未获取到图片链接 chapter_id: {chapter_id}')

            for i, url in enumerate(image_urls):
                pic_url = url['image']
                pic_name = f'image-{chapter_id}-{i}.jpg'
                path = self.folder / pic_name
                self.save_image(pic_url, path)

        except requests.RequestException as e:
            logger.error(f"下载章节网络请求失败: {e}")
            raise
        except Exception as e:
            logger.error(f"下载章节发生其他错误: {e}")
            raise

    def save_image(self, image_url, save_path):
        """保存图片"""
        try:
            if save_path.exists():  # 检查文件是否已存在
                logger.info(f"图片已存在 跳过: {save_path}")
                return
            response = requests.get(image_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"成功保存图片: {save_path}")

            time.sleep(0.5)  # 可以根据实际情况调整休眠时间

        except Exception as e:
            logger.error(f"保存图片失败 {save_path}: {str(e)}")
