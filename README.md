# API文档采集工具（所有代码均有AI完成）

鉴于目前AI开发越来越多，为了让AI能够快速理解相关API信息，开发了一个API文档采集工具。一个用于采集移动云API文档并转换为Markdown格式的Python工具。该工具能够通过API接口获取文档大纲树结构，递归下载所有文档内容，并保持原有的目录结构保存为Markdown文件和PDF文件。获取文档后，可以让AI根据API文档快速完成开发。

## 功能特性

### API文档采集功能
- 🔍 **API驱动**: 通过官方API接口获取文档，无需解析HTML页面
- 📁 **保持结构**: 完全保持原有的文档目录结构
- 📝 **格式转换**: 自动将HTML内容转换为Markdown格式
- 📄 **PDF下载**: 同时下载PDF文件（如果可用）
- 🛡️ **错误处理**: 完善的错误处理和重试机制
- ⚡ **高效采集**: 支持批量下载，自动处理延迟
- 🎯 **灵活配置**: 支持自定义大纲ID、文章ID和输出目录
- 📄 **单文档采集**: 支持通过文章ID直接获取单个文档（优先级最高）
- 🌐 **默认模式**: 无参数时自动获取所有可用的API文档（全量采集）

### 磁盘使用量收集功能
- 🖥️ **资源监控**: 自动发现并监控指定资源池中的所有云主机
- 💾 **磁盘分析**: 收集磁盘容量、使用量和使用率等详细数据
- 📊 **分区级别**: 支持多分区磁盘的精确监控和统计
- 📈 **Excel报告**: 生成格式化的Excel报告，包含资源ID等详细信息
- 🔐 **安全认证**: 使用移动云AK/SK认证机制，支持多种配置方式
- 🚀 **批量处理**: 支持大量服务器的批量数据收集和导出
- 🛠️ **容错机制**: 即使部分资源获取失败也能生成完整报告

## 项目结构

```
ecloud-api-doc-collector/
├── README.md                    # 项目说明文档
├── DISK_USAGE_README.md        # 磁盘使用量收集器专用文档
├── requirements.txt             # Python依赖包
├── config_example.py           # 配置文件示例
├── api_doc_collector.py        # API文档采集核心类
├── run_collector.py            # API文档采集命令行脚本
├── disk_usage_collector.py     # 磁盘使用量收集器核心类
├── ecloud_auth.py              # 移动云API认证模块
├── run_disk_collector.py       # 磁盘使用量收集交互式脚本
├── test_api_connection.py      # API连接测试脚本
└── api_docs/                   # 采集结果目录
    └── 对象存储 EOS/            # 示例：对象存储文档
        ├── API参考/
        ├── SDK文档/
        ├── 产品描述/
        └── ...
```

## 安装说明

### 环境要求

- Python 3.7+
- pip包管理器

### 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone <repository-url>
   cd EcloudApiDocCollector
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 第一步：获取分类ID

1. 打开移动云帮助中心：https://ecloud.10086.cn/op-help-center/
2. 找到需要采集的文档分类（如"对象存储 EOS"）
3. 点击进入该分类的文档页面
4. 查看浏览器地址栏，格式为：`https://ecloud.10086.cn/op-help-center/doc/category/729`
5. 最后的数字（如729）就是category ID

### 第二步：运行采集

```bash
# 默认模式（获取所有可用文档）
python run_collector.py

# 指定分类ID
python run_collector.py --category 729

# 指定大纲ID
python run_collector.py --outline-id 12345

# 指定文章ID（单个文档）
python run_collector.py --article-id "abc123"

# 指定分类ID和输出目录
python run_collector.py --category 729 --output-dir my_docs

# 指定大纲ID和输出目录
python run_collector.py --outline-id 12345 --output-dir my_docs

# 查看帮助信息
python run_collector.py --help
```

## 使用方法

### API文档采集

#### 方法一：使用运行脚本（推荐）

```bash
# 默认模式（获取所有可用的API文档）
python run_collector.py

# 指定分类ID
python run_collector.py --category 729

# 指定大纲ID
python run_collector.py --outline-id 12345

# 指定文章ID（优先级最高，直接获取单个文档）
python run_collector.py --article-id "abc123"

# 指定分类ID和输出目录
python run_collector.py --category 729 --output-dir my_docs

# 指定文章ID和输出目录
python run_collector.py --article-id "abc123" --output-dir my_docs

# 默认模式指定输出目录
python run_collector.py --output-dir all_docs
```

#### 方法二：直接运行核心脚本

```bash
# 修改api_doc_collector.py中的配置参数
python api_doc_collector.py
```

#### 方法三：在代码中使用

```python
from api_doc_collector import APIDocCollector

# 方式1：默认模式（获取所有可用文档）
collector = APIDocCollector(output_dir="api_docs")

# 方式2：使用category
collector = APIDocCollector(category=729, output_dir="api_docs")

# 方式3：使用outline_id
collector = APIDocCollector(outline_id=12345, output_dir="api_docs")

# 方式4：使用article_id（单个文档）
collector = APIDocCollector(article_id="abc123", output_dir="api_docs")

# 开始采集
collector.collect()
```

### 磁盘使用量收集

#### 1. 配置认证信息

复制 `config_example.py` 为 `config.py` 并配置正确的API认证信息：

```python
# 移动云API配置
ACCESS_KEY = "your_access_key"
SECRET_KEY = "your_secret_key"
BASE_URL = "https://api-wuxi-1.cmecloud.cn:8443"
DEFAULT_POOL_ID = "CIDC-RP-01"
```

#### 2. 运行磁盘使用量收集器

```bash
# 使用默认配置运行
python run_disk_collector.py

# 指定自定义配置文件
python run_disk_collector.py --config custom_config.py

# 指定输出文件名
python run_disk_collector.py --output disk_usage_report.xlsx
```

#### 3. 查看报告

收集完成后，会在当前目录生成Excel报告文件，包含以下信息：
- 资源ID和名称
- 磁盘分区信息
- 磁盘容量、使用量和使用率
- 数据收集时间

详细使用说明请参考：[磁盘使用量收集器文档](DISK_USAGE_README.md)

## 完整示例

### 示例1：默认模式（全量采集）

```bash
# 获取所有可用的API文档
python run_collector.py --output-dir all_api_docs
```

### 示例2：采集对象存储EOS文档

```bash
# 采集对象存储EOS分类下的所有文档
python run_collector.py --category 729 --output-dir eos_docs
```

### 示例3：采集特定大纲的文档

```bash
# 采集指定大纲ID的文档
python run_collector.py --outline-id 12345 --output-dir specific_docs
```

### 示例4：采集单个文章

```bash
# 直接获取指定文章ID的单个文档
python run_collector.py --article-id "abc123" --output-dir single_doc
```

### 采集对象存储EOS文档

1. **获取分类ID**：
   - 访问：https://ecloud.10086.cn/op-help-center/doc/category/729
   - 确认category ID为：729

2. **运行采集**：
   ```bash
   python run_collector.py --category 729
   ```

3. **查看结果**：
   - 文档将保存在 `api_docs/对象存储 EOS/` 目录下
   - 包含Markdown文件和PDF文件（如果可用）

## 配置说明

### 主要参数

- **默认模式** (无参数): 获取所有可用的API文档
  - 当不提供任何参数时，程序会自动使用全量文档树接口
  - 使用API: `https://ecloud.10086.cn/op-help-center/request-api/service-api/outline/api/tree`
  - 适用于需要获取所有API文档的场景

- **category** (optional): 文档分类ID，用于指定要采集的文档类型
  - `729`: 对象存储 EOS
  - 其他ID: 根据实际需要设置
  - **获取方法**：
    1. 打开移动云帮助中心：https://ecloud.10086.cn/op-help-center/
    2. 找到需要采集的文档分类（如"对象存储 EOS"）
    3. 点击进入该分类的文档页面
    4. 查看浏览器地址栏，格式为：`https://ecloud.10086.cn/op-help-center/doc/category/729`
    5. 最后的数字（如729）就是category ID

- **outline_id** (optional): 文档大纲ID，可直接指定，优先级高于category
  - 如果同时提供category和outline_id，程序会优先使用outline_id
  - 适用于已知outline_id的情况，可以跳过category到outline_id的转换步骤

- **article_id** (optional): 文章ID，优先级最高
  - 用于直接获取单个文档
  - 获取方法：在文档页面的浏览器地址栏查看，或通过API接口获取
  - 当指定此参数时，将忽略category和outline-id参数

- **output_dir**: 输出目录名称
  - 默认: `api_docs`
  - 自定义: 任意有效的目录名

### 采集模式优先级

程序支持四种采集模式，优先级从高到低为：
1. **article_id模式**: 直接获取单个文档（优先级最高）
2. **outline_id模式**: 根据大纲ID获取文档树
3. **category模式**: 根据分类ID获取文档树
4. **默认模式**: 获取所有可用的API文档（优先级最低）

### API配置

程序使用移动云的官方API接口：
- 基础URL: `https://ecloud.10086.cn/op-help-center/request-api/service-api`
- 分类信息API: `/category/info/{category}` - 获取outline_id
- 大纲树API: `/outline/tree?outlineId={outline_id}` - 获取文档结构
- 全量文档树API: `/outline/api/tree` - 获取所有可用文档（默认模式）
- 请求头: 模拟浏览器访问，包含User-Agent等信息

## 输出格式

### 文件结构

采集完成后，会在输出目录中创建以下结构：

```
output_dir/
├── 文档标题1/
│   ├── 子文档1.md
│   ├── 子文档1.pdf (如果可用)
│   └── 子目录/
│       └── 子文档2.md
└── 文档标题2/
    └── ...
```

### 文件格式

- **Markdown文件 (.md)**: 转换后的文档内容，包含标题、正文、链接等
- **PDF文件 (.pdf)**: 原始PDF文档（如果API提供）

## 核心类说明

### APIDocCollector类

主要的采集类，提供以下核心方法：

- `__init__(category, outline_id, article_id, output_dir)`: 初始化采集器，支持四种模式
- `collect()`: 执行采集流程，自动根据参数选择采集模式
- `collect_single_article(article_id)`: 采集单个文章（根据文章ID）
- `get_outline_tree()`: 获取文档大纲树（category/outline_id模式）
- `get_full_outline_tree()`: 获取全量文档树（默认模式）
- `parse_tree_node(node, level)`: 解析树节点结构
- `extract_content_and_pdf(article_id, base_file_path)`: 提取内容和PDF
- `create_directory_structure(items, current_path)`: 创建目录结构

### 工作流程

1. **参数验证**: 检查采集模式（article_id > outline_id > category > 默认模式）
2. **模式选择**: 根据提供的参数选择相应的采集模式
   - **article_id模式**: 直接采集单个文档
   - **outline_id模式**: 通过outline_id获取文档树
   - **category模式**: 通过category获取outline_id，再获取文档树
   - **默认模式**: 使用全量文档树API获取所有文档
3. **获取文档结构**: 根据模式获取相应的文档树结构
4. **解析节点**: 递归解析所有节点，识别叶子节点和分支节点
5. **下载内容**: 对叶子节点下载文档内容和PDF文件
6. **格式转换**: 将HTML内容转换为Markdown格式
7. **保存文件**: 按原有结构保存到本地目录

## 错误处理

程序包含完善的错误处理机制：

- **网络错误**: 自动重试，超时处理
- **API错误**: 检查状态码，输出错误信息
- **文件错误**: 创建目录失败时的处理
- **格式错误**: HTML解析失败时的回退机制

## 注意事项

1. **访问频率**: 程序在请求间添加1秒延迟，避免对服务器造成压力
2. **文件命名**: 自动清理文件名中的特殊字符，确保文件系统兼容性
3. **编码处理**: 统一使用UTF-8编码处理中文内容
4. **内容回退**: 如果主要内容源失败，会尝试其他可用的内容源

## 依赖包说明

### API文档采集相关依赖
- `requests`: HTTP请求库，用于API调用
- `html2text`: HTML转Markdown转换库
- `beautifulsoup4`: HTML解析库（备用）
- `lxml`: XML/HTML解析器

### 磁盘使用量收集相关依赖
- `pandas`: 数据处理和分析库，用于数据整理和Excel导出
- `openpyxl`: Excel文件读写库，用于生成格式化的Excel报告
- `argparse`: 命令行参数解析库（Python标准库）
- `datetime`: 日期时间处理库（Python标准库）
- `hashlib`: 哈希算法库，用于API签名生成（Python标准库）
- `hmac`: HMAC算法库，用于API认证（Python标准库）
- `urllib.parse`: URL编码解析库（Python标准库）

## 常见问题

### Q: 如何获取其他文档的分类ID？
A: 按照以下步骤获取：
1. 打开移动云帮助中心：https://ecloud.10086.cn/op-help-center/
2. 找到需要采集的文档分类
3. 点击进入该分类的文档页面
4. 查看浏览器地址栏，格式为：`https://ecloud.10086.cn/op-help-center/doc/category/729`
5. 最后的数字（如729）就是category ID

### Q: 下载的PDF文件无法打开？
A: 检查网络连接和API权限，某些PDF可能需要特殊权限才能下载。

### Q: 如何处理大量文档的采集？
A: 程序已经包含延迟机制，对于大量文档建议分批处理。

### Q: 如何自定义输出格式？
A: 可以修改`extract_content_and_pdf`方法来自定义内容处理逻辑。

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款。

## 更新日志

- v1.2: 新增默认模式功能
  - 支持无参数时自动获取所有可用的API文档
  - 添加`get_full_outline_tree`方法
  - 更新文档说明和使用示例
  - 完善采集模式优先级说明
- v1.1: 新增article_id功能
  - 支持通过文章ID直接获取单个文档
  - 添加`collect_single_article`方法
  - 更新run_collector.py支持--article-id参数
- v1.0: 初始版本，支持基本的API文档采集功能
  - 添加了详细的中文注释和错误处理
  - 完善了README文档和使用说明

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 联系方式

如有问题或建议，请通过GitHub Issues联系。
