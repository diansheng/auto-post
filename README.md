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
from rednote_auto_post import publish_post as post_note

# 方法1：直接传递参数
result = post_note(
    title="小红书自动发布测试",
    description="这是一个使用自动化工具发布的小红书笔记。",
    image_dir="images_to_post",
    hashtags=["#自动化工具", "#小红书笔记"]
)

print(f"发布结果: {result}")

# 方法2：使用Python字典对象
post_data = {
    "title": "小红书自动发布测试 - Python字典",
    "description": "这是一个使用自动化工具发布的小红书笔记。\n\n通过Python字典对象方式调用，支持更灵活的内容定义，特别适合长文本和复杂格式。",
    "image_dir": "images_to_post",
    "hashtags": ["#自动化工具", "#小红书笔记", "#Python", "#字典对象"]
}

result = post_note(post_data=post_data)
print(f"发布结果: {result}")

# 方法3：使用默认图片目录
result = post_note(
    title="小红书自动发布测试",
    description="这是一个使用自动化工具发布的小红书笔记。",
    # 不指定image_dir，将使用配置中的默认图片目录
    hashtags=["#自动化工具", "#小红书笔记"]
)
print(f"发布结果: {result}")
```

### 示例文件

项目提供了以下示例文件，帮助你快速上手：

1. **example_usage.py**: 展示了各种使用方法的完整示例
2. **example_post.py**: Python字典对象格式的发布内容示例
3. **example_dict_usage.py**: 展示如何使用Python字典对象发布笔记的示例

你可以直接运行这些示例文件来了解不同的使用方法：

```bash
# 查看Python字典对象示例
python example_post.py

# 查看字典对象使用示例
python example_dict_usage.py

# 查看完整使用示例
python example_usage.py
```

### 单元测试

项目包含单元测试，可以通过以下命令运行：

```bash
python -m unittest test_rednote_auto_post.py
```

单元测试覆盖了以下功能：
- 检查图片目录和获取图片路径
- 验证图片路径
- 使用直接参数发布笔记
- 使用Python字典对象发布笔记
- 使用空图片路径列表发布笔记

### 故障排除

如果遇到问题，请尝试以下解决方案：

1. **依赖问题**：
   ```bash
   pip install -r requirements.txt
   ```

2. **ChromeDriver 问题**：
   - 确保已安装 Chrome 浏览器
   - 安装 webdriver-manager 以自动管理 ChromeDriver：
     ```bash
     pip install webdriver-manager
     ```

3. **输入问题**：
   - 检查元素类型，确保使用正确的属性（value 或 textContent）
   - 对于富文本编辑器，可能需要修改代码使用 innerHTML 而非 textContent
   - 启用详细日志以诊断问题：
     ```python
     import logging
     logging.basicConfig(level=logging.DEBUG)
     ```

4. **事件触发问题**：
   - 某些网站可能需要特定的事件序列，可以修改 JavaScript 代码添加其他事件
   - 检查网站是否使用自定义事件处理程序

5. **性能考虑**：
   - JavaScript 执行器方法比 send_keys 更快，尤其是对于长文本
   - 对于大量输入操作，可以考虑使用隐式等待减少等待时间：
     ```python
     driver.implicitly_wait(1)  # 设置较短的隐式等待时间
     ```
   - 如果遇到性能问题，可以尝试减少验证步骤或使用更直接的方法

6. **安全考虑**：
   - 使用 JavaScript 执行器时要小心，确保不执行不受信任的代码
   - 避免在 JavaScript 中直接拼接用户输入，以防止 XSS 攻击
   - 对于处理敏感信息的输入字段，考虑使用更安全的方法：
     ```python
     # 对于密码字段，使用安全的输入方法
     password_field = driver.find_element(By.ID, "password")
     driver.execute_script(
         "arguments[0].value = arguments[1]; "
         "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
         password_field, password
     )
     ```

7. **浏览器兼容性**：
   - 当前代码主要针对 Chrome 浏览器优化
   - 对于其他浏览器（如 Firefox、Edge），可能需要调整 JavaScript 代码
   - 如果需要跨浏览器支持，可以添加条件逻辑：
     ```python
     # 根据浏览器类型调整 JavaScript 代码
     browser_name = driver.capabilities['browserName'].lower()
     if browser_name == 'firefox':
         # Firefox 特定代码
         js_code = "arguments[0].textContent = arguments[1];"
     else:
         # Chrome 和其他浏览器
         js_code = "arguments[0].textContent = arguments[1];"
     
     driver.execute_script(js_code, element, value)
     ```

8. **未来改进**：
   - 添加对更多富文本编辑器框架的支持（如 CKEditor、TinyMCE 等）
   - 实现更智能的元素类型检测，自动选择最佳输入方法
   - 添加对 Shadow DOM 元素的支持
   - 优化性能，减少不必要的验证步骤
   - 添加更多单元测试和集成测试

9. **贡献指南**：
   - 欢迎提交 Pull Request 来改进代码
   - 添加新功能时，请同时添加相应的单元测试
   - 修复 bug 时，请先添加一个能重现问题的测试
   - 代码风格请遵循 PEP 8 规范
   - 提交前请运行所有测试确保没有破坏现有功能

### 参数处理逻辑

- **参数优先级**: 直接传入的参数 > Python字典对象中的值 > 默认生成的值
- **图片目录验证**: 图片目录会被验证，确保目录存在且包含有效图片
- **图片目录处理**:
  - 如果提供 `None`：程序会尝试从Python字典对象获取，若仍为None则使用默认配置
  - 如果不指定 `image_dir`：程序会使用配置中的默认图片目录
  - 如果提供有效目录：程序会使用提供的图片目录
  - **命令行调用时**：程序会使用默认目录或通过--image-dir参数指定的目录
- **自动生成**: 如果未提供标题或描述，会自动生成测试值
- **默认目录**: 确保默认图片目录 `images_to_post` 中有有效的图片文件（.jpg, .png, .jpeg）

### 数据格式

#### Python字典对象格式

创建一个Python字典对象，包含以下字段：

```python
post_data = {
    "title": "小红书自动发布测试",
    "description": "这是一个使用自动化工具发布的小红书笔记，通过Python字典对象配置内容。\n\n这个工具可以帮助创作者批量发布内容，提高效率。",
    "image_dir": "images_to_post",
    "hashtags": ["#自动化工具", "#小红书笔记", "#Python", "#Selenium"]
}
```

项目中提供了 `example_post.py` 文件，其中包含了一个完整的Python字典对象示例，你可以直接导入使用：

```python
# 导入示例字典对象
from example_post import post_data

# 使用导入的字典对象发布笔记
result = publish_post(post_data=post_data)
```

更多使用示例请参考 `example_dict_usage.py` 文件。

**注意**：参数优先级为：直接传入的参数 > Python字典对象中的值 > 默认生成的值。只有当某个参数未通过高优先级方式提供时，才会使用低优先级方式中的对应值。

### 直接运行脚本

```bash
# 使用命令行参数
python rednote_auto_post.py --title "标题" --description "描述" --image-dir "images_to_post" --hashtags "#标签1" "#标签2"

# 使用默认图片目录（images_to_post）
python rednote_auto_post.py --title "标题" --description "描述"

# 无参数运行（使用默认Python字典对象）
python rednote_auto_post.py
```

**注意**：
- 当从命令行运行时，如果不指定 `--image-dir` 参数，程序会自动使用默认目录（`images_to_post`）中的图片。确保该目录中有有效的图片文件（.jpg, .png, .jpeg）。
- 当不提供任何参数运行脚本时，程序会自动使用默认Python字典对象 `post_data`（从example_post.py导入）。

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
    "headless": false
}
```

你可以通过以下方式自定义配置：

1. 创建一个`config.json`文件（已在项目中提供示例）
2. 使用命令行参数 `--config` 指定配置文件路径：
   ```bash
   python rednote_auto_post.py --config my_config.json
   ```



## 依赖

- Python 3.6+
- Selenium
- Chrome浏览器和对应版本的ChromeDriver

## Emoji 支持

本工具现已支持在标题和正文中使用 emoji 表情符号。您可以直接在 Python 字典对象或直接参数中包含 emoji，系统将使用 JavaScript 执行器确保它们能正确显示在小红书笔记中。

### 基本用法

示例：
```python
post_data = {
    "title": "✨ 我的测试标题 🚀",
    "description": "这是一个包含 emoji 的描述 🎉 很酷吧？ 🔥",
    # 其他参数...
}
```

### 技术实现

本工具使用 JavaScript 执行器来设置包含 emoji 的文本，并触发必要的 DOM 事件（input 和 change），确保网站能正确识别输入内容。这解决了 ChromeDriver 对非 BMP 字符（如 emoji）的限制问题。

工具能够智能识别不同类型的输入元素：
- 对于标准表单元素（如 `<input>` 和 `<textarea>`），使用 `value` 属性设置内容
- 对于富文本编辑器和 contentEditable 元素（如 `<div contenteditable="true">`），使用 `textContent` 属性设置内容

工具内置了多层错误处理和备用机制：

1. **主要方法**：使用 JavaScript 执行器设置值并触发 DOM 事件，自动检测元素类型
2. **备用方法 1**：如果主要方法失败，尝试使用 InputEvent 替代 Event 对象，同样自动检测元素类型
3. **备用方法 2**：如果 JavaScript 方法都失败，回退到 send_keys 方法（会自动移除 emoji）

每一步都有详细的日志记录，帮助诊断可能的问题。

### 高级 Emoji 处理

如果您需要对包含 emoji 的文本进行特殊处理，可以使用 `process_emoji_text` 函数：

```python
from rednote_auto_post import process_emoji_text

# 保留所有 emoji（默认模式，用于 JavaScript 执行器）
text_with_emoji = process_emoji_text("Hello 😊 World 🌍", mode='keep')

# 移除所有非 BMP 字符（用于 ChromeDriver 直接输入）
text_without_emoji = process_emoji_text("Hello 😊 World 🌍", mode='remove')

# 将 emoji 替换为文本描述
text_with_emoji_replaced = process_emoji_text("Hello 😊 World 🌍", mode='replace')
# 输出: "Hello [笑脸] World [emoji]"
```

### ContentEditable 元素处理

`safe_set_input_value` 函数现在能够智能处理 contentEditable 元素（如富文本编辑器）。查看示例脚本了解详细用法：

```python
# 运行示例脚本
python example_contenteditable.py
```

示例脚本演示了：

1. 如何处理简单的 contentEditable div 元素
2. 如何处理更复杂的富文本编辑器
3. 如何在不同类型的元素中输入包含 emoji 的文本

脚本会自动检测所需依赖并提供安装指导。

#### 最佳实践

处理不同类型的元素时，请注意以下最佳实践：

1. **标准表单元素**（如 `<input>` 和 `<textarea>`）：
   - 使用 `value` 属性设置内容
   - 可以直接使用 `element.clear()` 方法清空内容

2. **ContentEditable 元素**（如 `<div contenteditable="true">`）：
   - 使用 `textContent` 属性设置纯文本内容
   - 如果需要保留 HTML 格式，修改代码使用 `innerHTML` 属性
   - 不能使用 `element.clear()` 方法，应使用 JavaScript 清空内容

3. **富文本编辑器**：
   - 默认使用 `textContent` 设置内容（HTML 标记会被当作纯文本）
   - 如果需要保留格式（如粗体、链接等），需要修改代码使用 `innerHTML`
   - 参考 `rednote_auto_post.py` 中的注释了解如何切换

查看 `example_emoji_usage.py` 获取更多使用 emoji 的示例。