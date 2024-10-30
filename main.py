from pathlib import Path

from loguru import logger

from mkz_get_chapter import MKZChapter
from config import CONFIG

"""
程序运行有给小BUG，原因是最新的章节是要钱购买的，但不影响获取其他章节
"""


def main():
    try:
        # 配置日志
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logger.add(log_dir / "mkz_{time}.log", rotation="50 MB", encoding="utf-8")

        # 实例化章节爬取类
        mkz = MKZChapter()
        chapter_data_list = mkz.get_chapter_list(CONFIG["manga_id"])

        if not chapter_data_list:
            logger.warning("未获取到任何章节数据")
            return

        # 自然排序逻辑
        if CONFIG["is_first_sort"]:
            chapter_data_list.sort(key=lambda x: int(x['chapter_id']))  # 根据章节的id值进行排序从小 -> 大
        chapter_data_list = chapter_data_list[:CONFIG["get_page"]]

        total_chapters = len(chapter_data_list)
        for index, chapter_data in enumerate(chapter_data_list, 1):
            chapter_id = chapter_data['chapter_id']
            chapter_name = chapter_data['title']

            logger.info(f'下载进度: [{index}/{total_chapters}] {chapter_name} 开始')
            try:
                mkz.download_chapter(chapter_id, CONFIG["manga_id"])
                logger.info(f'下载进度: [{index}/{total_chapters}] {chapter_name} 完成')
            except Exception as e:
                logger.error(f'下载章节 {chapter_name} 失败: {str(e)}')
                continue

    except Exception as e:
        logger.error(f"运行出错: {str(e)}")


if __name__ == "__main__":
    main()
