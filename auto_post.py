# -*- coding: utf-8 -*-
"""
使用 Selenium 自动发布小红书图文笔记（网页版）
前提：
1. 已登录小红书创作平台（creator.xiaohongshu.com）并保存了登录 Cookie
2. Windows 系统，Python 3.x，已安装 Chrome 浏览器和对应 chromedriver
3. pip install selenium
"""

import time
import os
import datetime
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle

# 导入日志配置
from logging_config import logger

# === 配置参数 ===
COOKIE_PATH = 'cookies.pkl'  # 登录后的 Cookie 文件路径
IMAGE_DIR = 'images_to_post'  # 图片文件夹
TITLE = '这是自动发布的标题'
DESCRIPTION = '这是一段笔记描述内容'
HASHTAGS = ['#自动化', '#小红书', '#selenium发布']

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
def load_cookies(driver):
    logger.info("加载 cookies")
    driver.get("https://creator.xiaohongshu.com")
    time.sleep(2)
    with open(COOKIE_PATH, 'rb') as f:
        cookies = pickle.load(f)
    for cookie in cookies:
        driver.add_cookie(cookie)
    driver.refresh()
    logger.debug("Cookies 加载完成")

# === 上传图片并发布 ===
def upload_images_and_publish(driver, image_paths, title, description):
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
        time.sleep(3)
        
        # 点击发布
        publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="发布"]')))
        # 实际发布（如果需要测试不发布，可以注释此行）
        publish_btn.click()
        time.sleep(30)
        logger.info("已点击发布按钮")
        
        return True
    except Exception as e:
        logger.error(f"上传图片或发布失败: {str(e)}")
        screenshot_path = "publish_failed.png"
        driver.save_screenshot(screenshot_path)
        logger.debug(f"已保存失败截图: {screenshot_path}")
        return False

# === 检查图片目录和获取图片路径 ===
def check_image_directory_and_get_paths():
    """检查图片目录是否存在和是否有图片，返回图片路径列表或None"""
    # 检查图片目录是否存在，不存在则创建
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)
        logger.warning(f"创建了图片目录: {IMAGE_DIR}")
        logger.warning("请在此目录中添加图片后再运行脚本")
        return None
        
    # 检查图片目录中是否有图片文件
    image_files = [f for f in os.listdir(IMAGE_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        logger.error(f"图片目录 {IMAGE_DIR} 中没有图片文件")
        return None
    
    # 返回绝对路径列表
    logger.info(f"找到 {len(image_files)} 张图片")
    return [os.path.abspath(os.path.join(IMAGE_DIR, fname)) for fname in image_files]

# === 自动化发布流程 ===
def publish_note(driver, image_paths=None, title=None, description=None):
    logger.info("开始发布笔记流程")
    wait = WebDriverWait(driver, 15)

    # 尝试直接访问创建页面
    creation_urls = [
        "https://creator.xiaohongshu.com/publish/publish?from=menu&target=post", # 创建图文
        "https://creator.xiaohongshu.com/publish/publish?from=menu&target=video", # 创建video
        "https://creator.xiaohongshu.com/publish"
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
    
    # 准备参数
    if image_paths is None:
        # 获取图片路径
        image_paths = check_image_directory_and_get_paths()
        if image_paths is None:
            return False
    
    if title is None:
        title = TITLE
    
    if description is None:
        description = f"{DESCRIPTION}\n{' '.join(HASHTAGS)}"
    
    # 调用上传图片并发布函数
    result = upload_images_and_publish(driver, image_paths, title, description)
    
    if result:
        logger.info("流程执行完成")
    
    return result

# === 主函数 ===
def main():
    """主函数"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        driver = None
        try:
            # 检查图片目录并获取图片路径
            image_paths = check_image_directory_and_get_paths()
            if image_paths is None:
                return
            
            # 初始化浏览器
            driver = init_browser()
            
            # 处理Cookie
            if not os.path.exists(COOKIE_PATH):
                logger.info("未找到 Cookie 文件，需要手动登录")
                driver.get("https://creator.xiaohongshu.com")
                input("登录后按 Enter 保存 Cookie...")
                pickle.dump(driver.get_cookies(), open(COOKIE_PATH, "wb"))
                logger.info(f"已保存 Cookie 到 {COOKIE_PATH}")
            else:
                logger.info(f"使用已保存的 Cookie: {COOKIE_PATH}")
                load_cookies(driver)
            
            # 准备标题和描述
            title = "测试笔记" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            description = "这是一个自动发布的测试笔记，发布时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 发布笔记
            success = publish_note(driver, image_paths, title, description)
            
            # 关闭浏览器
            driver.quit()
            
            if success:
                logger.info("任务完成")
                break  # 成功完成，跳出重试循环
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

# === 主流程 ===
if __name__ == '__main__':
    logger.info("=== 小红书自动发布工具启动 ===")
    main()
