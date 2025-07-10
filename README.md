# Rednote Auto Post Tool

这个工具可以帮助用户自动发布小红书笔记，支持通过函数调用或Python字典对象配置内容。

## 功能特点

- 模块化设计，可以被其他组件调用
- 支持通过变量传递标题、描述、图片和话题标签
- 支持从Python字典对象读取发布内容（适合长文本和复杂格式）
- 自动处理登录和Cookie管理
- 详细的日志记录
- 优化了冗余的None检查，提高了代码效率

## 使用方法

### 作为模块导入

```python
from rednote_auto_post import publish_post

# 方法1：直接传入参数
result = publish_post(
    title="测试标题",
    description="测试描述",
    image_dir="images_to_post",
    hashtags=["#测试标签1", "#测试标签2"]
)

# 方法2：使用Python字典对象
post_data = {
    "title": "小红书自动发布测试",
    "description": "这是一个测试",
    "image_dir": "images_to_post",
    "hashtags": ["#自动化工具"]
}
result = publish_post(post_data=post_data)
```



### 单元测试

如果你需要为项目添加单元测试，可以创建测试文件并通过以下命令运行：

```bash
python -m unittest 你的测试文件.py
```

### 故障排除

如果遇到问题，请尝试以下解决方案：

1. **依赖问题**：
   ```bash
   pip install -r requirements.txt
   ```

2. **ChromeDriver 问题**：
   - 确保已安装 Chrome 浏览器
   - 安装 webdriver-manager 以自动管理 ChromeDriver

3. **输入问题**：
   - 检查元素类型，确保使用正确的属性（value 或 textContent）
   - 启用详细日志以诊断问题：
     ```python
     import logging
     logging.basicConfig(level=logging.DEBUG)
     ```

### 数据格式与参数处理

- **参数优先级**: 直接传入的参数 > Python字典对象中的值 > 默认生成的值
- **图片目录**: 默认使用 `images_to_post` 目录，确保其中有有效的图片文件
- **自动生成**: 如果未提供标题或描述，会自动生成测试值

**Python字典对象格式**示例：

```python
post_data = {
    "title": "小红书自动发布测试",
    "description": "这是一个使用自动化工具发布的小红书笔记。",
    "image_dir": "images_to_post",
    "hashtags": ["#自动化工具", "#小红书笔记"]
}
```

项目中提供了 `example_post.py` 文件，其中包含了一个完整的Python字典对象示例，你可以直接导入使用。

### 直接运行脚本

```bash
python rednote_auto_post.py --title "测试标题" --description "测试描述" --image_dir "images_to_post" --hashtags "#测试标签1" "#测试标签2"
```

## 配置

首次运行时，脚本会自动打开浏览器并要求登录小红书账号。登录后的Cookie将被保存，后续运行将自动使用保存的Cookie。

你可以通过命令行参数 `--config` 指定配置文件路径：
```bash
python rednote_auto_post.py --config my_config.json
```



## 依赖

- Python 3.6+
- Selenium (见requirements.txt)
- Chrome浏览器

## 高级功能

### Emoji 支持

本工具支持在标题和正文中使用 emoji 表情符号。您可以直接在 Python 字典对象或直接参数中包含 emoji：

```python
post_data = {
    "title": "✨ 我的测试标题 🚀",
    "description": "这是一个包含 emoji 的描述 🎉",
    # 其他参数...
}
```

### ContentEditable 元素处理

`safe_set_input_value` 函数能够智能处理不同类型的输入元素：

- **标准表单元素**（如 `<input>` 和 `<textarea>`）：使用 `value` 属性设置内容
- **ContentEditable 元素**（如 `<div contenteditable="true">`）：使用 `textContent` 属性设置内容
- **富文本编辑器**：默认使用 `textContent`，如需保留 HTML 格式可修改为使用 `innerHTML`