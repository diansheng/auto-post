# -*- coding: utf-8 -*-
"""单元测试文件，用于测试rednote_auto_post.py的功能"""

import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# 导入被测试的模块
import rednote_auto_post
from rednote_auto_post import publish_post, load_post_from_json, check_image_directory_and_get_paths, validate_image_paths

class TestRedNoteAutoPost(unittest.TestCase):
    """测试RedNoteAutoPost的功能"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建临时目录和文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = self.temp_dir.name
        
        # 创建测试用的JSON文件
        self.test_json_path = os.path.join(self.temp_path, "test_post.json")
        self.test_json_data = {
            "title": "测试标题",
            "description": "测试描述",
            "image_paths": [os.path.join(self.temp_path, "test_image.jpg")],
            "hashtags": ["#测试标签"]
        }
        
        with open(self.test_json_path, "w", encoding="utf-8") as f:
            json.dump(self.test_json_data, f, ensure_ascii=False)
        
        # 创建测试用的图片文件
        with open(self.test_json_data["image_paths"][0], "w") as f:
            f.write("test image content")
    
    def tearDown(self):
        """测试后的清理工作"""
        self.temp_dir.cleanup()
    
    def test_load_post_from_json(self):
        """测试从JSON文件加载发布内容"""
        result = load_post_from_json(self.test_json_path)
        self.assertEqual(result["title"], "测试标题")
        self.assertEqual(result["description"], "测试描述")
        self.assertEqual(result["image_paths"][0], os.path.join(self.temp_path, "test_image.jpg"))
        self.assertEqual(result["hashtags"][0], "#测试标签")
    
    def test_check_image_directory_and_get_paths(self):
        """测试检查图片目录和获取图片路径"""
        # 创建测试用的图片目录
        image_dir = os.path.join(self.temp_path, "images")
        os.makedirs(image_dir)
        
        # 创建测试用的图片文件
        test_images = ["test1.jpg", "test2.png", "test3.jpeg"]
        for img in test_images:
            with open(os.path.join(image_dir, img), "w") as f:
                f.write("test image content")
        
        # 测试获取图片路径
        paths = check_image_directory_and_get_paths(image_dir)
        self.assertEqual(len(paths), 3)
        
        # 测试空目录
        empty_dir = os.path.join(self.temp_path, "empty")
        os.makedirs(empty_dir)
        self.assertIsNone(check_image_directory_and_get_paths(empty_dir))
        
        # 测试不存在的目录
        non_exist_dir = os.path.join(self.temp_path, "non_exist")
        self.assertIsNone(check_image_directory_and_get_paths(non_exist_dir))
    
    def test_validate_image_paths(self):
        """测试验证图片路径"""
        # 创建测试用的图片文件
        valid_paths = []
        for i in range(3):
            path = os.path.join(self.temp_path, f"valid{i}.jpg")
            with open(path, "w") as f:
                f.write("test image content")
            valid_paths.append(path)
        
        # 测试有效路径
        self.assertTrue(validate_image_paths(valid_paths))
        
        # 创建一个不存在的目录路径
        non_exist_dir = os.path.join(self.temp_path, "non_exist_dir")
        invalid_path = os.path.join(non_exist_dir, "invalid.jpg")
        
        # 测试不存在的目录路径
        self.assertFalse(validate_image_paths([invalid_path]))
        
        # 测试非图片文件
        non_image_path = os.path.join(self.temp_path, "non_image.txt")
        with open(non_image_path, "w") as f:
            f.write("test text content")
        self.assertTrue(validate_image_paths([non_image_path]))  # 应该返回True但有警告
        
        # 测试SVG文件
        svg_path = os.path.join(self.temp_path, "test.svg")
        with open(svg_path, "w") as f:
            f.write("<svg></svg>")
        self.assertTrue(validate_image_paths([svg_path]))  # 应该返回True
    
    @patch("rednote_auto_post.init_browser")
    @patch("rednote_auto_post._publish_post")
    def test_publish_post_with_direct_params(self, mock_publish, mock_init_browser):
        """测试使用直接参数发布笔记"""
        # 模拟浏览器和发布函数
        mock_driver = MagicMock()
        mock_init_browser.return_value = mock_driver
        mock_publish.return_value = True
        
        # 测试使用直接参数
        result = publish_post(
            title="测试标题",
            description="测试描述",
            image_paths=self.test_json_data["image_paths"],
            hashtags=["#测试标签"]
        )
        
        self.assertTrue(result)
        mock_init_browser.assert_called_once()
        mock_publish.assert_called_once()
    
    @patch("rednote_auto_post.init_browser")
    @patch("rednote_auto_post._publish_post")
    def test_publish_post_with_json(self, mock_publish, mock_init_browser):
        """测试使用JSON文件发布笔记"""
        # 模拟浏览器和发布函数
        mock_driver = MagicMock()
        mock_init_browser.return_value = mock_driver
        mock_publish.return_value = True
        
        # 测试使用JSON文件
        result = publish_post(json_file=self.test_json_path)
        
        self.assertTrue(result)
        mock_init_browser.assert_called_once()
        mock_publish.assert_called_once()
    
    @patch("rednote_auto_post.init_browser")
    @patch("rednote_auto_post._publish_post")
    @patch("rednote_auto_post.check_image_directory_and_get_paths")
    def test_publish_post_with_empty_image_paths(self, mock_check, mock_publish, mock_init_browser):
        """测试使用空图片路径列表发布笔记"""
        # 模拟浏览器、发布函数和图片目录检查
        mock_driver = MagicMock()
        mock_init_browser.return_value = mock_driver
        mock_publish.return_value = True
        mock_check.return_value = self.test_json_data["image_paths"]
        
        # 测试使用空图片路径列表
        result = publish_post(
            title="测试标题",
            description="测试描述",
            image_paths=[],
            hashtags=["#测试标签"]
        )
        
        self.assertTrue(result)
        mock_check.assert_called_once()
        mock_init_browser.assert_called_once()
        mock_publish.assert_called_once()

if __name__ == "__main__":
    unittest.main()