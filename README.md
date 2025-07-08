# Rednote Auto Post Tool

这个工具可以帮助用户自动发布小红书笔记，支持通过函数调用或JSON文件配置内容。

## 功能特点

- 模块化设计，可以被其他组件调用
- 支持通过变量传递标题、描述、图片和话题标签
- 支持从JSON格式的文本文件读取发布内容
- 自动处理登录和Cookie管理
- 详细的日志记录
- 优化了冗余的None检查，提高了代码效率

## 使用方法

### 作为模块导入

```python
from rednote_auto_post import publish_post as post_note

# 方法1：直接传递参数
result = post_note(
    title="小红书自动发布测试",
    description="这是一个使用自动化工具发布的小红书笔记。",
    image_paths=["images_to_post/Capture.PNG"],
    hashtags=["#自动化工具", "#小红书笔记"]
)

print(f"发布结果: {result}")

# 方法2：使用JSON文件
result = post_note(json_file="example_post.json")
print(f"发布结果: {result}")

# 方法3：使用默认图片目录
result = post_note(
    title="小红书自动发布测试",
    description="这是一个使用自动化工具发布的小红书笔记。",
    image_paths=[],  # 空列表将触发从默认目录获取图片
    hashtags=["#自动化工具", "#小红书笔记"]
)
print(f"发布结果: {result}")
```

### 单元测试

项目包含单元测试，可以通过以下命令运行：

```bash
python -m unittest test_rednote_auto_post.py
```

单元测试覆盖了以下功能：
- 从JSON文件加载发布内容
- 检查图片目录和获取图片路径
- 验证图片路径
- 使用直接参数发布笔记
- 使用JSON文件发布笔记
- 使用空图片路径列表发布笔记

### 参数处理逻辑

- **参数优先级**: 直接传入的参数 > JSON文件中的值 > 默认生成的值
- **图片路径验证**: 所有图片路径都会被验证，确保文件存在且为有效图片
- **图片路径处理**:
  - 如果提供 `None`：程序会尝试从JSON文件获取，若仍为None则报错
  - 如果提供空列表 `image_paths=[]`：程序会尝试从默认目录获取图片
  - 如果提供非空列表：程序会使用提供的图片路径
  - **命令行调用时**：程序会自动使用空列表并从默认目录获取图片
- **自动生成**: 如果未提供标题或描述，会自动生成测试值
- **默认目录**: 确保默认图片目录 `images_to_post` 中有有效的图片文件（.jpg, .png, .jpeg）

### JSON文件格式

创建一个JSON文件，包含以下字段：

```json
{
    "title": "小红书自动发布测试",
    "description": "这是一个使用自动化工具发布的小红书笔记，通过JSON文件配置内容。\n\n这个工具可以帮助创作者批量发布内容，提高效率。",
    "image_paths": ["images_to_post/Capture.PNG"],
    "hashtags": ["#自动化工具", "#小红书笔记", "#Python", "#Selenium"]
}
```

**注意**：当同时提供函数参数和JSON文件时，函数参数优先级更高。只有当某个参数未通过函数参数提供时（值为None），才会使用JSON文件中的对应值。

### 直接运行脚本

```bash
# 使用命令行参数
python rednote_auto_post.py --title "标题" --description "描述" --image-dir "images_to_post" --hashtags "#标签1" "#标签2"

# 使用JSON文件
python rednote_auto_post.py --json example_post.json

# 使用默认图片目录（images_to_post）
python rednote_auto_post.py --title "标题" --description "描述"

# 无参数运行（使用默认JSON文件）
python rednote_auto_post.py

# 指定默认JSON文件
python rednote_auto_post.py --default-json "my_post.json"
```

**注意**：
- 当从命令行运行时，如果不指定 `--image-dir` 参数，程序会自动使用默认目录（`images_to_post`）中的图片。确保该目录中有有效的图片文件（.jpg, .png, .jpeg）。
- 当不提供任何参数运行脚本时，程序会自动使用默认JSON文件 `example_post.json`。你可以通过`--default-json`参数指定其他默认JSON文件。确保此文件存在且包含有效的配置。

## 配置

首次运行时，脚本会自动打开浏览器并要求登录小红书账号。登录后的Cookie将被保存，后续运行将自动使用保存的Cookie。

程序使用以下默认配置：

```json
{
    "cookie_path": "cookies.pkl",
    "image_dir": "images_to_post",
    "max_retries": 3,
    "timeout": 30,
    "upload_timeout": 120,
    "scroll_pause_time": 1,
    "wait_after_upload": 3,
    "wait_after_publish": 5,
    "headless": false,
    "default_json": "example_post.json"
}
```

你可以通过以下方式自定义配置：

1. 创建一个`config.json`文件（已在项目中提供示例）
2. 使用命令行参数 `--config` 指定配置文件路径：
   ```bash
   python rednote_auto_post.py --config my_config.json
   ```

### 默认JSON文件

你可以通过以下方式指定默认JSON文件：
1. 使用命令行参数 `--default-json`
2. 在配置文件中设置 `default_json` 值
3. 如果都未指定，将使用默认值 `example_post.json`

## 依赖

- Python 3.6+
- Selenium
- Chrome浏览器和对应版本的ChromeDriver