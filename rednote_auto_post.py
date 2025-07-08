# -*- coding: utf-8 -*-
"""
使用 Selenium 自动发布小红书图文笔记（网页版）
前提：
1. 已登录小红书创作平台（creator.xiaohongshu.com）并保存了登录 Cookie
2. Windows 系统，Python 3.x，已安装 Chrome 浏览器和对应 chromedriver
3. pip install selenium

此模块可以被其他组件调用，支持自定义标题、描述、图片和标签
也可以从JSON文件中读取发布内容
"""

import time
import os
import sys
import datetime
import traceback
import json
from typing import List, Dict, Optional, Union, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

# 导入日志配置
from logging_config import logger

# === 默认配置参数 ===
DEFAULT_CONFIG = {
    'cookie_path': 'cookies.pkl',  # 登录后的 Cookie 文件路径
    'image_dir': 'images_to_post',  # 图片文件夹
    'max_retries': 1,  # 最大重试次数
    'default_json': 'example_post.json'  # 默认JSON配置文件路径
}

# === 初始化浏览器 ===
def init_browser():
    logger.info("初始化浏览器")
    options = Options()
    options.add_argument("--start-maximized")
    # 添加更多选项以提高稳定性
    options.add_argument("--disable-extensions")
    # options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(), options=options)
    logger.debug("浏览器初始化完成")
    return driver

# === 加载 cookies ===
def load_cookies(driver, cookie_path: str) -> None:
    """加载保存的cookies到浏览器"""
    logger.info("加载 cookies")
    driver.get("https://creator.xiaohongshu.com")
    time.sleep(2)
    with open(cookie_path, 'rb') as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    logger.debug("Cookies 加载完成")

# === 检查图片目录和获取图片路径 ===
def check_image_directory_and_get_paths(image_dir: str) -> Optional[List[str]]:
    """检查图片目录是否存在和是否有图片，返回图片路径列表或None"""
    # 检查图片目录是否存在，不存在则创建
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        logger.warning(f"创建了图片目录: {image_dir}")
        logger.info("请在此目录中添加图片文件（.jpg, .png, .jpeg格式）后再运行脚本\n图片文件将按照字母顺序上传到小红书\n")
        return None
        
    # 检查图片目录中是否有图片文件
    image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        logger.warning(f"图片目录 {image_dir} 中没有图片文件")
        return None
    
    # 返回绝对路径列表
    logger.info(f"找到 {len(image_files)} 张图片")
    return [os.path.abspath(os.path.join(image_dir, fname)) for fname in image_files]

# === 验证图片路径 ===
def validate_image_paths(image_paths: List[str]) -> bool:
    """验证图片路径列表是否有效
    
    Args:
        image_paths: 图片路径列表
        
    Returns:
        bool: 所有路径是否有效
    
    Note:
        此函数假设image_paths不为空，因为在publish_post函数中已经处理了空列表的情况
    """
    # 不再检查空列表，因为在调用此函数前已经处理了空列表的情况
    # 并且确保了传入的列表不为空
    
    # 获取所有图片所在的目录
    image_dirs = set()
    for path in image_paths:
        image_dir = os.path.dirname(path)
        if image_dir:
            image_dirs.add(image_dir)
        else:
            # 如果路径没有目录部分，使用当前目录
            image_dirs.add('.')
    
    # 检查目录是否存在
    valid = True
    for dir_path in image_dirs:
        if not os.path.exists(dir_path):
            logger.warning(f"图片目录不存在: {dir_path}")
            logger.info(f"请创建此目录或修改图片路径")
            valid = False
        elif not os.listdir(dir_path):
            logger.warning(f"图片目录为空: {dir_path}")
            logger.info(f"请在此目录中添加图片")
            # 目录为空不影响验证结果，只是警告
    
    # 检查文件扩展名
    for path in image_paths:
        if not path.lower().endswith(('.png', '.jpg', '.jpeg', '.svg')):
            logger.warning(f"文件可能不是图片: {path}")
    
    logger.info(f"验证了 {len(image_paths)} 个图片路径")
    return valid

# === 上传图片并发布 ===
def upload_post_content(driver, image_paths, title, description):
    """上传图片并发布笔记"""
    logger.info("开始上传图片并发布笔记")
    wait = WebDriverWait(driver, 15)
    
    try:
        # 上传图片
        upload_input = wait.until(EC.presence_of_element_located((By.XPATH, '//input[@type="file"]')))
        
        # 确保上传元素可见
        driver.execute_script(
            "arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';", 
            upload_input
        )
        
        # 上传所有图片
        upload_input.send_keys("\n".join(image_paths))
        logger.info(f"正在上传 {len(image_paths)} 张图片")
        
        # 等待图片加载完成
        time.sleep(3)
        logger.debug("等待图片加载完成")
        
        # 输入标题
        title_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="填写标题会有更多赞哦～"]')))
        title_input.send_keys(title)
        logger.debug(f"已输入标题: {title}")
        time.sleep(3)
        
        # 输入正文
        desc_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-placeholder="输入正文描述，真诚有价值的分享予人温暖"]')))
        desc_input.send_keys(description)
        logger.debug("已输入正文")
        time.sleep(15)
        
        # 点击发布
        publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="发布"]')))
        # 实际发布（如果需要测试不发布，可以注释此行）
        publish_btn.click()
        time.sleep(5)
        logger.info("已点击发布按钮")
        
        return True
    except Exception as e:
        logger.error(f"上传图片或发布失败: {str(e)}")
        screenshot_path = "publish_failed.png"
        driver.save_screenshot(screenshot_path)
        logger.debug(f"已保存失败截图: {screenshot_path}")
        return False

# === 自动化发布流程 ===
def _publish_post(driver, image_paths: List[str], title: str, 
                description: str, hashtags: Optional[List[str]] = None, 
                config: Optional[Dict[str, Any]] = None) -> bool:
    """发布笔记的主要流程
    
    Args:
        driver: Selenium WebDriver实例
        image_paths: 图片路径列表，必须提供有效的图片路径列表
        title: 笔记标题，必须提供
        description: 笔记描述，必须提供
        hashtags: 标签列表，如果为None则使用空列表
        config: 配置字典，包含cookie_path, image_dir等参数
        
    Returns:
        bool: 发布是否成功
        
    Note:
        此函数假设所有必要参数已经过验证，不应传入None值
    """    
    logger.info("开始发布笔记流程")
    wait = WebDriverWait(driver, 15)

    # 尝试直接访问创建页面
    creation_urls = [
        "https://creator.xiaohongshu.com/publish/publish?from=menu&target=post", # 创建图文
        # "https://creator.xiaohongshu.com/publish/publish?from=menu&target=video", # 创建video
        # "https://creator.xiaohongshu.com/publish"
    ]

    # 尝试访问创建页面URL
    for url in creation_urls:
        try:
            logger.info(f"尝试访问创建页面: {url}")
            driver.get(url)
            time.sleep(5)
            
            try:
                file_input = driver.find_element(By.XPATH, '//input[@type="file"]')
                logger.info(f"成功进入创建页面: {url}")
                break
            except:
                logger.error(f"在 {url} 未找到上传元素")
        except Exception as e:
            logger.error(f"访问 {url} 出错: {str(e)}")
    else:  # 如果所有URL都失败
        # 保存截图帮助调试
        screenshot_path = "debug_screenshot.png"
        driver.save_screenshot(screenshot_path)
        logger.error("无法进入创建页面，请检查网站结构是否变化")
        return False
    
    # 将标签添加到描述中
    full_description = f"{description}\n{' '.join(hashtags)}"
    
    # 调用上传图片并发布函数
    result = upload_post_content(driver, image_paths, title, full_description)
    
    if result:
        logger.info("流程执行完成")
    
    return result

# === 从JSON文件读取发布内容 ===
def load_post_from_json(json_file_path: str) -> Dict[str, Any]:
    """从JSON文件中读取发布内容
    
    JSON文件格式示例:
    {
        "title": "笔记标题",
        "description": "笔记描述内容",
        "image_dir": "path_to_image",
        "hashtags": ["#标签1", "#标签2"]
    }
    
    Args:
        json_file_path: JSON文件路径
        
    Returns:
        包含发布内容的字典
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 验证必要字段
        required_fields = ['title', 'description']
        for field in required_fields:
            if field not in data:
                logger.error(f"JSON文件缺少必要字段: {field}")
                return {}
        
        logger.info(f"成功从 {json_file_path} 加载发布内容")
        return data
    
    except Exception as e:
        logger.error(f"读取JSON文件失败: {str(e)}")
        return {}

# === 主函数 ===
def publish_post(title: Optional[str] = None, description: Optional[str] = None,  
                image_dir: Optional[str] = None, hashtags: Optional[List[str]] = None,
             json_file: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> bool:
    """发布小红书笔记的主函数。负责验证参数，加载JSON内容，处理图片路径，调用发布流程。
    1. 验证参数：检查标题、描述、图片路径、标签是否为空，以及JSON文件路径是否存在。
    2. 加载JSON内容：如果提供了JSON文件路径，就读取其中的内容。
    3. 处理图片路径：根据提供的图片路径或JSON文件中的路径，获取实际的图片文件路径。
    4. 调用发布流程：使用处理后的参数（标题、描述、图片路径、标签）调用发布函数。
    
    Args:
        title: 笔记标题，如果为None则尝试从JSON文件获取，若仍为None则生成测试标题
        description: 笔记描述，如果为None则尝试从JSON文件获取，若仍为None则生成测试描述
        image_dir: 
        hashtags: 标签列表，如果为None则尝试从JSON文件获取，若仍为None则使用空列表
        json_file: JSON文件路径，如果提供则从中读取内容，但传入的参数优先级更高
        config: 配置字典，包含cookie_path, image_dir等参数，如果为None则使用默认配置
        
    Returns:
        bool: 发布是否成功
        
    Note:
        - 参数优先级：直接传入的参数 > JSON文件中的值 > 默认生成的值
        - 图片路径会进行验证，确保所有图片都存在且为有效文件
        - 空的图片路径列表[]会触发从默认目录获取图片的逻辑
    """
    
    # 使用默认配置或传入的配置
    config = config or DEFAULT_CONFIG.copy()

    json_file = json_file or config['default_json']
    if not os.path.exists(json_file):
        logger.error(f"配置文件{json_file}不存在")
        return False

    # 优先使用传入的参数，只有当参数为None时才使用JSON文件中的值
    json_data = load_post_from_json(json_file)
    if json_data:
        title = title or json_data.get('title')    
        description = description or json_data.get('description')
        image_dir = image_dir or json_data.get('image_dir')
        hashtags = hashtags or json_data.get('hashtags',[])
    else:
        logger.error(f"配置文件{json_file}有损坏。退出")
        return False

    # 解析出image_dir下的图片文件
    image_paths = check_image_directory_and_get_paths(image_dir)
    logger.info(f"从{image_dir}获取图片路径: {len(image_paths)}张图片")

    # validate variables
    # 如果没有提供标题和描述，生成测试值
    if title is None:
        title = "测试笔记" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logger.info(f"未提供标题，使用自动生成的标题: {title}")
    
    if description is None:
        description = "这是一个自动发布的测试笔记，发布时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"未提供描述，使用自动生成的描述")
    
    if hashtags is None:
        hashtags = []    
        
    if len(image_paths)==0:
        logger.error(f"图片路径{image_dir}下无图片，无法发布笔记")
        logger.info(f"请在 {image_dir} 目录中添加图片后再运行脚本")
        return False
    
    max_retries = config.get('max_retries', 3)
    retry_count = 0
    
    while retry_count < max_retries:
        driver = None
        try:
            # 初始化浏览器
            driver = init_browser()
            
            # 处理Cookie
            cookie_path = config['cookie_path']
            if not os.path.exists(cookie_path):
                logger.info("未找到 Cookie 文件，需要手动登录")
                driver.get("https://creator.xiaohongshu.com")
                input("登录后按 Enter 保存 Cookie...")
                pickle.dump(driver.get_cookies(), open(cookie_path, "wb"))
                logger.info(f"已保存 Cookie 到 {cookie_path}")
            else:
                logger.info(f"使用已保存的 Cookie: {cookie_path}")
                load_cookies(driver, cookie_path)
            
            # 发布笔记
            success = _publish_post(driver, image_paths, title, description, hashtags, config)
            
            # 关闭浏览器
            driver.quit()
            
            if success:
                logger.info("任务完成")
                return True  # 成功完成，返回True
            else:
                retry_count += 1
                logger.warning(f"发布失败 (尝试 {retry_count}/{max_retries})")
            
        except Exception as e:
            retry_count += 1
            logger.error(f"发生错误 (尝试 {retry_count}/{max_retries}): {str(e)}")
            logger.debug(traceback.format_exc())
            
            # 保存错误截图
            if driver:
                try:
                    screenshot_path = f"error_{retry_count}.png"
                    driver.save_screenshot(screenshot_path)
                    logger.debug(f"已保存错误截图: {screenshot_path}")
                    driver.quit()
                except:
                    pass
            
            if retry_count < max_retries:
                logger.info(f"将在 10 秒后重试...")
                time.sleep(10)
            else:
                logger.error(f"已达到最大重试次数 ({max_retries})，放弃任务")
                return False

# === 命令行入口 ===
def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='小红书自动发布工具')
    parser.add_argument('--content-json', type=str, help='content json, same format as example.json')
    parser.add_argument('--title', type=str, help='笔记标题')
    parser.add_argument('--description', type=str, help='笔记描述')
    parser.add_argument('--image-dir', type=str, help='图片目录')
    parser.add_argument('--hashtags', type=str, nargs='+', help='标签列表')
    parser.add_argument('--cookie-path', type=str, help='Cookie文件路径')
    
    return parser.parse_args()

def load_config(config_path='config.json'):
    """加载配置文件"""
    config = dict()
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            config.update(user_config)
            logger.info(f"已加载配置文件: {config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    return config

def main():
    """命令行入口函数"""


# === 主流程 ===
if __name__ == '__main__':
    logger.info("=== 小红书自动发布工具启动 ===")
    try:
        # 解析命令行参数
        args = parse_args()
        # 加载配置
        config = load_config()
        publish_post(
            title=args.title,
            description=args.description,
            image_dir=args.image_dir,
            hashtags=args.hashtags,
            json_file=args.content_json,
            config=config
        )
        logger.info("=== 小红书自动发布工具正常退出 ===")
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        logger.debug(traceback.format_exc())
        logger.info("=== 小红书自动发布工具异常退出 ===")
        sys.exit(1)
