# -*- coding: utf-8 -*-
"""
使用 Selenium 自动发布小红书图文笔记（网页版）
前提：
1. 已登录小红书创作平台（creator.xiaohongshu.com）并保存了登录 Cookie
2. Windows 系统，Python 3.x，已安装 Chrome 浏览器和对应 chromedriver
3. pip install selenium

此模块可以被其他组件调用，支持自定义标题、描述、图片和标签
支持通过Python字典对象配置发布内容
支持在标题和描述中使用emoji表情符号，具有多层错误处理和备用机制：
- 主要使用JavaScript执行器设置文本并触发DOM事件
- 如果主要方法失败，会尝试备用JavaScript方法
- 如果JavaScript方法都失败，会回退到send_keys方法（自动移除emoji）
"""

import time
import os
import sys
import datetime
import traceback
import json
import re
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
from example_post import post_data

# === 默认配置参数 ===
DEFAULT_CONFIG = {
    'cookie_path': 'cookies.pkl',  # 登录后的 Cookie 文件路径
    'image_dir': 'images_to_post',  # 图片文件夹
    'max_retries': 1,  # 最大重试次数
    'default_content': post_data,
    'debug': False  # 调试模式
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

# === 安全地设置输入框的值 ===
def safe_set_input_value(driver, element, value, field_name="输入框"):
    """安全地设置输入框的值，包含多层错误处理和备用方案
    
    此函数提供了一个健壮的方式来设置输入字段的值，特别是当值包含emoji等特殊字符时。
    它使用三层策略来确保文本能够被正确输入：
    1. 首先尝试使用JavaScript执行器设置值并触发标准DOM事件
    2. 如果第一种方法失败，尝试使用InputEvent替代Event对象
    3. 如果JavaScript方法都失败，回退到send_keys方法（自动移除emoji）
    
    每一步都有验证和详细的日志记录，以便于调试问题。
    
    此函数支持两种类型的输入元素：
    - 标准表单元素（如input、textarea）：使用value属性设置值
    - contentEditable元素（如div）：使用textContent属性设置值
    
    Args:
        driver: Selenium WebDriver实例
        element: 输入元素（WebElement对象）
        value: 要设置的值（可以包含emoji等特殊字符）
        field_name: 字段名称，用于日志记录，默认为"输入框"
        
    Returns:
        bool: 是否成功设置值（True表示成功，False表示所有方法都失败）
    
    Example:
        ```python
        # 设置标题（包含emoji）
        title_input = driver.find_element(By.XPATH, '//input[@placeholder="标题"]')
        safe_set_input_value(driver, title_input, "✨ 测试标题 🚀", "标题")
        ```
    """
    # 主要方法：使用JavaScript执行器处理包含emoji的文本并触发必要的事件
    # 注意：如果需要保留HTML格式（如粗体、链接等），请取消注释innerHTML行并注释textContent行
    # 例如：当处理富文本编辑器且需要保留格式化内容时，应使用innerHTML
    js_set_value_with_events = """
    // 检测元素类型并使用适当的属性设置值
    if (arguments[0].tagName === 'DIV' || arguments[0].getAttribute('contenteditable') === 'true') {
        // 对于contentEditable元素，使用textContent或innerHTML
        // 注意：
        // - textContent适用于纯文本内容，会移除所有HTML标签
        // - innerHTML适用于需要保留HTML格式的情况（如粗体、链接等）
        // 默认使用textContent，因为它更安全（防止XSS）且适合大多数情况
        // 如果输入内容包含HTML标记且需要保留格式，请修改此处使用innerHTML
        arguments[0].textContent = arguments[1];
        // arguments[0].innerHTML = arguments[1];
    } else {
        // 对于标准表单元素，使用value属性
        arguments[0].value = arguments[1];
    }
    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    return true; // 返回值以确认执行成功
    """
    
    try:
        result = driver.execute_script(js_set_value_with_events, element, value)
        if result:
            logger.debug(f"已成功输入{field_name}: {value}")
            # 验证文本是否已输入 - 根据元素类型检查不同属性
            js_verify = """
            if (arguments[0].tagName === 'DIV' || arguments[0].getAttribute('contenteditable') === 'true') {
                return arguments[0].textContent || arguments[0].innerHTML;
            } else {
                return arguments[0].value;
            }
            """
            actual_value = driver.execute_script(js_verify, element)
            if actual_value:
                return True
            else:
                logger.warning(f"{field_name}可能未成功输入，尝试备用方法")
        else:
            logger.warning(f"JavaScript执行器未返回成功状态（{field_name}）")
        
        # 备用方法1：尝试使用InputEvent
        logger.debug(f"尝试使用备用方法输入{field_name}")
        # 先清空输入框 - 根据元素类型使用不同的清空方法
        js_clear = """
        if (arguments[0].tagName === 'DIV' || arguments[0].getAttribute('contenteditable') === 'true') {
            arguments[0].textContent = '';
        } else {
            arguments[0].value = '';
        }
        return true;
        """
        driver.execute_script(js_clear, element)
        # 使用更直接的DOM操作方法
        # 对于contentEditable元素使用textContent，对于标准表单元素使用value
        js_alternative = """
        if (arguments[0].tagName === 'DIV' || arguments[0].getAttribute('contenteditable') === 'true') {
            arguments[0].textContent = arguments[1];
        } else {
            arguments[0].value = arguments[1];
        }
        arguments[0].dispatchEvent(new InputEvent('input', {bubbles: true, cancelable: true, composed: true}));
        arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
        return true;
        """
        driver.execute_script(js_alternative, element, value)
        
        # 再次验证 - 使用相同的验证逻辑
        actual_value = driver.execute_script(js_verify, element)
        if actual_value:
            logger.debug(f"已使用备用方法成功输入{field_name}")
            return True
        else:
            logger.warning(f"备用方法1也未能成功输入{field_name}")
    except Exception as e:
        logger.error(f"输入{field_name}时发生错误: {str(e)}")
    
    # 备用方法2：使用send_keys方法作为最后的备用
    # 注意：send_keys方法会自动移除emoji等非BMP字符
    # 这是最后的备用方法，只有在JavaScript方法都失败时才会使用
    try:
        # 检查元素类型，对contentEditable元素使用JavaScript清空内容
        # 这是必要的，因为element.clear()方法对contentEditable元素无效
        if driver.execute_script("return arguments[0].tagName === 'DIV' || arguments[0].getAttribute('contenteditable') === 'true'", element):
            # 对于contentEditable元素，使用JavaScript清空内容
            driver.execute_script("arguments[0].textContent = '';", element)
        else:
            # 对于标准表单元素，使用clear方法
            element.clear()
            
        # 移除非BMP字符以避免ChromeDriver错误
        # send_keys方法不能处理emoji等非BMP字符，所以需要移除它们
        safe_value = process_emoji_text(value, mode='remove')
        element.send_keys(safe_value)
        logger.debug(f"已使用send_keys方法输入{field_name}（已移除emoji）: {safe_value}")
        return True
    except Exception as inner_e:
        logger.error(f"所有输入{field_name}的方法都失败: {str(inner_e)}")
        return False

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

# 移除未使用的validate_image_paths函数，其功能已在check_image_directory_and_get_paths中实现

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
    """    
    logger.info("开始发布笔记流程")
    wait = WebDriverWait(driver, 15)
    hashtags = hashtags or []

    # 尝试直接访问创建页面
    creation_url = "https://creator.xiaohongshu.com/publish/publish?from=menu&target=post"
    try:
        logger.info(f"尝试访问创建页面: {creation_url}")
        driver.get(creation_url)
        time.sleep(5)
        
        # 上传图片
        try:
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
            
            # 输入标题
            title_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="填写标题会有更多赞哦～"]')))
            # 使用安全的输入方法设置标题
            safe_set_input_value(driver, title_input, title, field_name="标题")
            time.sleep(3)
            
            # 将标签添加到描述中
            full_description = f"{description}\n{' '.join(hashtags)}"
            
            # 输入正文
            desc_input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-placeholder="输入正文描述，真诚有价值的分享予人温暖"]')))
            # 使用安全的输入方法设置正文
            safe_set_input_value(driver, desc_input, full_description, field_name="正文")
            time.sleep(15)
            
            # 点击发布
            publish_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[text()="发布"]')))
            if config['debug']:
                publish_btn.click()
            time.sleep(5)
            logger.info("已点击发布按钮")
            logger.info("流程执行完成")
            
            return True
        except Exception as e:
            logger.error(f"上传图片或发布失败: {str(e)}")
            screenshot_path = "publish_failed.png"
            driver.save_screenshot(screenshot_path)
            logger.debug(f"已保存失败截图: {screenshot_path}")
            return False
    except Exception as e:
        logger.error(f"访问创建页面出错: {str(e)}")
        screenshot_path = "debug_screenshot.png"
        driver.save_screenshot(screenshot_path)
        logger.error("无法进入创建页面，请检查网站结构是否变化")
        return False

# === 处理Emoji和验证Python字典对象 ===

def process_emoji_text(text: str, mode: str = 'keep') -> str:
    """处理包含emoji的文本
    
    Args:
        text: 包含emoji的文本
        mode: 处理模式，可选值：
            - 'keep': 保留emoji（默认，用于JavaScript执行器）
            - 'remove': 移除所有非BMP字符（用于ChromeDriver直接输入）
            - 'replace': 将emoji替换为其描述（例如：😊 -> [笑脸]）
    
    Returns:
        str: 处理后的文本
    """
    if not text:
        return ""
        
    if mode == 'keep':
        return text
    elif mode == 'remove':
        return ''.join(c for c in text if ord(c) < 0x10000)
    elif mode == 'replace':
        # 简单替换常见emoji，可根据需要扩展
        emoji_map = {
            '😊': '[笑脸]',
            '😂': '[笑哭]',
            '❤️': '[爱心]',
            '👍': '[赞]',
            '🎉': '[庆祝]',
            '🔥': '[火]',
            '✨': '[闪光]',
            '🚀': '[火箭]',
            # 可以根据需要添加更多映射
        }
        
        for emoji, replacement in emoji_map.items():
            text = text.replace(emoji, replacement)
            
        # 对于未定义的emoji，使用通用替换
        # 匹配大多数emoji的正则表达式
        emoji_pattern = re.compile(
            "["  
            "\U0001F600-\U0001F64F"  # 表情符号
            "\U0001F300-\U0001F5FF"  # 符号和象形文字
            "\U0001F680-\U0001F6FF"  # 交通和地图
            "\U0001F700-\U0001F77F"  # 警告符号
            "\U0001F780-\U0001F7FF"  # 几何图形
            "\U0001F800-\U0001F8FF"  # 补充箭头
            "\U0001F900-\U0001F9FF"  # 补充符号和象形文字
            "\U0001FA00-\U0001FA6F"  # 棋子符号
            "\U0001FA70-\U0001FAFF"  # 符号和象形文字扩展
            "\U00002702-\U000027B0"  # 装饰符号
            "\U000024C2-\U0000257F"  # 封闭字母数字
            "\U00002600-\U000026FF"  # 杂项符号
            "\U00002700-\U000027BF"  # 装饰符号
            "\U0000FE00-\U0000FE0F"  # 变体选择器
            "\U0001F900-\U0001F9FF"  # 补充符号和象形文字
            "\U00002B50"             # 星形
            "\U00002B55"             # 圆形
            "\U00002B1B-\U00002B1C"  # 黑白方块
            "\U0000200D"             # 零宽连接符
            "\U00002640-\U00002642"  # 性别符号
            "\U00002600-\U00002B55"  # 杂项符号和箭头
            "]", 
            flags=re.UNICODE
        )
        
        return emoji_pattern.sub(r'[emoji]', text)
    else:
        raise ValueError(f"不支持的处理模式: {mode}")

def validate_post_data(data: Dict[str, Any]) -> bool:
    """验证发布内容数据是否有效
    
    Args:
        data: 包含发布内容的字典
        
    Returns:
        bool: 数据是否有效
    """
    # 验证必要字段
    required_fields = ['title', 'description']
    for field in required_fields:
        if field not in data:
            logger.error(f"发布数据缺少必要字段: {field}")
            return False
    return True

# === 主函数 ===
def publish_post(title: Optional[str] = None, description: Optional[str] = None,  
                image_dir: Optional[str] = None, hashtags: Optional[List[str]] = None,
                post_data: Optional[Dict[str, Any]] = None,
                config: Optional[Dict[str, Any]] = None) -> bool:
    """发布小红书笔记的主函数
    
    Args:
        title: 笔记标题，如果为None则尝试从post_data获取，若仍为None则生成测试标题
        description: 笔记描述，如果为None则尝试从post_data获取，若仍为None则生成测试描述
        image_dir: 图片目录路径
        hashtags: 标签列表
        post_data: Python字典对象，包含发布内容
        config: 配置字典
        
    Returns:
        bool: 发布是否成功
    """
    # 初始化配置
    tmp_conf = DEFAULT_CONFIG.copy()
    tmp_conf.update(config or {})
    config = tmp_conf
    post_data = post_data or config.get('default_content')
    image_dir = image_dir or config.get('image_dir')
    max_retries = config.get('max_retries', 1)
    
    # 从Python字典对象加载数据
    if post_data and validate_post_data(post_data):
        logger.info("使用Python字典对象作为发布内容")
        title = title or post_data.get('title')    
        description = description or post_data.get('description')
        image_dir = image_dir or post_data.get('image_dir')
        hashtags = hashtags or post_data.get('hashtags',[])
    elif not title or not description:
        logger.error("发布内容无效：未提供有效的post_data或直接参数")
        return False
        
    # 获取图片路径
    if not image_dir:
        logger.error("未指定图片目录")
        return False
        
    image_paths = check_image_directory_and_get_paths(image_dir)
    if not image_paths:
        logger.error(f"图片路径{image_dir}下无图片，无法发布笔记")
        return False
    
    # 设置默认值
    if title is None:
        title = "测试笔记" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        logger.info(f"未提供标题，使用自动生成的标题: {title}")
    
    if description is None:
        description = "这是一个自动发布的测试笔记，发布时间：" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"未提供描述，使用自动生成的描述")
    
    # 执行发布流程，支持重试
    for retry_count in range(max_retries):
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
            if _publish_post(driver, image_paths, title, description, hashtags, config):
                logger.info("任务完成")
                driver.quit()
                return True
                
            logger.warning(f"发布失败 (尝试 {retry_count + 1}/{max_retries})")
            
        except Exception as e:
            logger.error(f"发生错误 (尝试 {retry_count + 1}/{max_retries}): {str(e)}")
            logger.debug(traceback.format_exc())
            
            # 保存错误截图
            if driver:
                try:
                    driver.save_screenshot(f"error_{retry_count + 1}.png")
                    driver.quit()
                except:
                    pass
        
        # 如果不是最后一次尝试，等待后重试
        if retry_count < max_retries - 1:
            logger.info(f"将在 10 秒后重试...")
            time.sleep(10)
    
    logger.error(f"已达到最大重试次数 ({max_retries})，放弃任务")
    return False

# === 命令行入口和配置加载 ===
def load_config(config_path='config.json'):
    """加载配置文件"""
    config = dict()
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.update(json.load(f))
            logger.info(f"已加载配置文件: {config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
    return config

# 导出的函数和变量
__all__ = [
    'publish_post',
    'validate_post_data',
    'check_image_directory_and_get_paths',
    'process_emoji_text',
    'safe_set_input_value'
]

# === 主流程 ===
if __name__ == '__main__':
    logger.info("=== 小红书自动发布工具启动 ===")
    try:
        # 解析命令行参数
        import argparse
        parser = argparse.ArgumentParser(description='小红书自动发布工具')
        parser.add_argument('--title', type=str, help='笔记标题')
        parser.add_argument('--description', type=str, help='笔记描述')
        parser.add_argument('--image-dir', type=str, help='图片目录')
        parser.add_argument('--hashtags', type=str, nargs='+', help='标签列表')
        parser.add_argument('--cookie-path', type=str, help='Cookie文件路径')
        args = parser.parse_args()
        
        # 加载配置并发布
        config = load_config()
        if args.cookie_path:
            config['cookie_path'] = args.cookie_path
            
        result = publish_post(
            title=args.title,
            description=args.description,
            image_dir=args.image_dir,
            hashtags=args.hashtags,
            config=config
        )
        
        exit_code = 0 if result else 1
        logger.info(f"=== 小红书自动发布工具{'正常' if result else '异常'}退出 ===")
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {str(e)}")
        logger.debug(traceback.format_exc())
        logger.info("=== 小红书自动发布工具异常退出 ===")
        sys.exit(1)
