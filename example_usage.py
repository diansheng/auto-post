#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
示例脚本：演示如何使用 auto_post 模块
"""

from rednote_auto_post import publish_post


def example_direct_parameters():
    """使用直接参数调用示例"""
    result = publish_post(
        title="小红书自动发布测试 - 直接参数",
        description="这是一个使用自动化工具发布的小红书笔记。\n\n通过直接传递参数方式调用。",
        image_paths=["images_to_post/Capture.PNG"],
        hashtags=["#自动化工具", "#小红书笔记", "#Python"]
    )
    print(f"发布结果: {result}")


def example_json_file():
    """使用JSON文件调用示例"""
    result = publish_post(json_file="example_post.json")
    print(f"发布结果: {result}")


def example_mixed_parameters():
    """混合使用参数和JSON文件示例（参数优先级：直接参数 > JSON文件）"""
    result = publish_post(
        title="覆盖JSON的标题",  # 这将覆盖JSON中的标题
        json_file="example_post.json"  # 其他字段将从JSON中读取
    )
    print(f"发布结果: {result}")


def example_empty_image_paths():
    """使用空图片列表示例（将从默认目录获取图片）"""
    result = publish_post(
        title="使用默认图片目录",
        description="这个示例将从默认图片目录获取图片。",
        image_paths=[],  # 空列表将触发从默认目录获取图片
        hashtags=["#测试", "#默认图片"]
    )
    print(f"发布结果: {result}")


def example_auto_generate():
    """自动生成标题和描述示例"""
    result = publish_post(
        image_paths=["images_to_post/Capture.PNG"],  # 只提供图片路径
        hashtags=["#自动生成"]  # 标题和描述将自动生成
    )
    print(f"发布结果: {result}")


if __name__ == "__main__":
    # 取消注释以下行来运行示例
    # example_direct_parameters()
    # example_json_file()
    # example_mixed_parameters()
    # example_empty_image_paths()
    # example_auto_generate()
    
    print("这是一个示例脚本，展示如何使用 auto_post 模块。")
    print("请取消注释相应的函数调用来测试不同的使用方式。")