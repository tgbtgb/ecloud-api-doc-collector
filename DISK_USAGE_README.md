# 磁盘使用量收集器

该工具用于收集所有服务器的磁盘使用量信息，并生成Excel报告。

## 功能特性

- 🔍 **自动发现资源**: 自动获取指定资源池中的所有服务器资源
- 📊 **磁盘监控**: 收集磁盘容量、使用量和使用率数据
- 📁 **分区级别**: 支持多分区磁盘的详细监控
- 📈 **Excel报告**: 生成格式化的Excel报告文件
- ⚡ **批量处理**: 支持大量服务器的批量数据收集
- 🛡️ **错误处理**: 完善的错误处理和日志记录

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置认证

### 移动云API认证机制

本工具使用移动云API的AK/SK（Access Key/Secret Key）对称加密验证方式进行身份认证。每个API请求都会自动生成签名信息以确保安全性。

#### 1. 权限要求

🔑 **必需的API权限：**

使用本工具需要确保您的Access Key具有以下权限：

- **monitor:DescribeMonitor** - 监控数据查询权限
  - 用于获取云主机资源列表
  - 用于获取性能监控指标
  - 用于获取磁盘分区信息
  - 用于获取磁盘使用量数据

**权限配置方法：**

1. 登录移动云控制台
2. 进入「访问控制」→「用户管理」
3. 选择对应的用户或创建新用户
4. 在「权限管理」中添加策略
5. 确保策略包含 `monitor:DescribeMonitor` 权限
6. 保存并应用权限配置

⚠️ **重要提醒：** 如果Access Key缺少必要权限，API调用将返回权限拒绝错误，工具无法正常工作。

#### 2. 获取AK/SK凭证

**获取方式：**
1. 登录移动云控制台
2. 进入「访问控制」→「访问密钥」
3. 创建或查看现有的Access Key
4. 记录Access Key ID（AK）和Secret Access Key（SK）

**凭证格式：**
- Access Key ID：32位字符串，如 `d0742694e5784074af7b2c5ecff21455`
- Secret Access Key：40位字符串，用于签名计算

#### 3. 配置方式

**方式一：使用配置文件（推荐）**

1. 复制配置文件模板：
```bash
cp config_example.py config.py
```

2. 编辑配置文件 `config.py`：
```python
# 移动云API认证配置
ACCESS_KEY = 'd0742694e5784074af7b2c5ecff21455'  # 您的Access Key ID
SECRET_KEY = 'your_40_char_secret_key_here'      # 您的Secret Access Key
BASE_URL = 'https://api-wuxi-1.cmecloud.cn:8443'  # API接入地址
```

**配置文件说明：**

项目提供了 `config_example.py` 配置文件模板，包含以下配置项：

```python
# config_example.py - 配置文件模板

# ===== 移动云API认证配置 =====
# 必填：您的Access Key ID（32位字符串）
ACCESS_KEY = 'your_access_key_id_here'

# 必填：您的Secret Access Key（40位字符串）
SECRET_KEY = 'your_secret_access_key_here'

# 必填：API接入地址，根据资源所在区域选择
BASE_URL = 'https://api-wuxi-1.cmecloud.cn:8443'

# ===== 可选配置 =====
# 默认资源池ID（可通过命令行参数覆盖）
DEFAULT_POOL_ID = 'CIDC-RP-01'

# 默认输出目录
OUTPUT_DIR = './output'

# 日志级别：DEBUG, INFO, WARNING, ERROR
LOG_LEVEL = 'INFO'

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 重试次数
MAX_RETRIES = 3
```

**配置步骤：**
1. 将 `config_example.py` 复制为 `config.py`
2. 填入您的真实AK/SK信息
3. 根据资源所在区域修改 `BASE_URL`
4. 可选：调整其他配置项以满足需求
5. 确保将 `config.py` 添加到 `.gitignore` 中

**方式二：命令行参数**

```bash
python disk_usage_collector.py --pool-id CIDC-RP-01 \
  --access-key d0742694e5784074af7b2c5ecff21455 \
  --secret-key your_secret_key \
  --base-url https://api-wuxi-1.cmecloud.cn:8443
```

**方式三：环境变量**

```bash
# Windows PowerShell
$env:ECLOUD_ACCESS_KEY="your_access_key"
$env:ECLOUD_SECRET_KEY="your_secret_key"
python disk_usage_collector.py --pool-id CIDC-RP-01

# Linux/macOS
export ECLOUD_ACCESS_KEY="your_access_key"
export ECLOUD_SECRET_KEY="your_secret_key"
python disk_usage_collector.py --pool-id CIDC-RP-01
```

#### 4. API接入地址配置

移动云API在不同区域有不同的接入地址，请根据您的资源所在区域选择：

| 区域 | 接入地址 | 说明 |
|------|----------|------|
| 华东-苏州 | `https://api-wuxi-1.cmecloud.cn:8443` | 默认地址 |
| 华北-北京 | `https://api-beijing-1.cmecloud.cn:8443` | 北京区域 |
| 华南-广州 | `https://api-guangzhou-1.cmecloud.cn:8443` | 广州区域 |
| 华东-上海 | `https://api-shanghai-1.cmecloud.cn:8443` | 上海区域 |
| 西南-成都 | `https://api-chengdu-1.cmecloud.cn:8443` | 成都区域 |

**URL格式说明：**
```
{URI-scheme}://{Endpoint}/{resource-path}?{query-string}
```
- `URI-scheme`: 协议（HTTPS/HTTP）
- `Endpoint`: 服务器域名和端口
- `resource-path`: API资源路径
- `query-string`: 查询参数（包含认证信息）

#### 5. 安全注意事项

🔒 **重要安全提醒：**
- ✅ 妥善保管AK/SK，切勿泄露给他人
- ✅ 不要将AK/SK提交到代码仓库
- ✅ 建议使用配置文件方式，并将 `config.py` 加入 `.gitignore`
- ✅ 生产环境建议使用环境变量或密钥管理服务
- ✅ 定期轮换访问密钥
- ✅ 为不同环境使用不同的密钥对

**`.gitignore` 示例：**
```gitignore
# 配置文件
config.py
*.env
.env.*

# 日志文件
*.log

# 输出文件
*.xlsx
*.csv
```

## 使用方法

### 命令行参数说明

| 参数 | 简写 | 类型 | 必选 | 默认值 | 描述 |
|------|------|------|------|--------|---------|
| `--pool-id` | `-p` | String | 是 | - | 资源池ID，如 CIDC-RP-01 |
| `--access-key` | `-ak` | String | 否 | 配置文件 | Access Key ID |
| `--secret-key` | `-sk` | String | 否 | 配置文件 | Secret Access Key |
| `--base-url` | `-u` | String | 否 | 配置文件 | API接入地址 |
| `--start-time` | `-s` | String | 否 | 7天前 | 开始时间，格式：YYYY-MM-DD HH:MM:SS |
| `--end-time` | `-e` | String | 否 | 当前时间 | 结束时间，格式：YYYY-MM-DD HH:MM:SS |
| `--output` | `-o` | String | 否 | 自动生成 | 输出文件名 |
| `--verbose` | `-v` | Flag | 否 | False | 详细输出模式 |
| `--help` | `-h` | Flag | 否 | False | 显示帮助信息 |

### 使用示例

**1. 基本用法（使用配置文件）**
```bash
python disk_usage_collector.py --pool-id CIDC-RP-01
```

**2. 指定认证信息**
```bash
python disk_usage_collector.py --pool-id CIDC-RP-01 \
  --access-key d0742694e5784074af7b2c5ecff21455 \
  --secret-key your_secret_key \
  --base-url https://api-beijing-1.cmecloud.cn:8443
```

**3. 指定时间范围**
```bash
python disk_usage_collector.py --pool-id CIDC-RP-01 \
  --start-time "2024-01-01 00:00:00" \
  --end-time "2024-01-31 23:59:59"
```

**4. 指定输出文件和详细模式**
```bash
python disk_usage_collector.py --pool-id CIDC-RP-01 \
  --output disk_usage_report_202401.xlsx \
  --verbose
```

**5. 完整参数示例**
```bash
python disk_usage_collector.py \
  --pool-id CIDC-RP-01 \
  --access-key d0742694e5784074af7b2c5ecff21455 \
  --secret-key your_secret_key \
  --base-url https://api-wuxi-1.cmecloud.cn:8443 \
  --start-time "2024-01-01 00:00:00" \
  --end-time "2024-01-31 23:59:59" \
  --output monthly_disk_report.xlsx \
  --verbose
```

### 交互式脚本

运行交互式脚本，按提示输入参数：

```bash
python run_disk_collector.py
```

交互式脚本会引导您：
1. 输入资源池ID
2. 选择时间范围（最近7天、30天或自定义）
3. 输入输出文件名
4. 确认配置并开始收集

**交互式脚本示例：**
```
=== 移动云磁盘使用量收集工具 ===

请输入资源池ID: CIDC-RP-01

选择时间范围:
1. 最近7天
2. 最近30天
3. 自定义时间范围
请选择 (1-3): 1

请输入输出文件名 (留空使用默认名称): 

=== 配置确认 ===
资源池ID: CIDC-RP-01
时间范围: 2024-01-25 00:00:00 ~ 2024-02-01 23:59:59
输出文件: disk_usage_CIDC-RP-01_20240201_235959.xlsx

确认开始收集? (y/n): y

开始收集磁盘使用量数据...
```

## 输出报告

生成的Excel报告包含以下列：

| 列名 | 描述 | 单位 | 备注 |
|------|------|------|------|
| 资源ID | 云主机的唯一标识符 | - | 用于API调用和资源定位 |
| 资源名称 | 服务器资源名称 | - | 用户自定义的资源名称 |
| 分区 | 磁盘分区路径 | - | 如：C:、D:、/、/home等 |
| 磁盘容量大小 | 分区总容量 | GB | 分区的总存储空间 |
| 已使用大小 | 分区已使用容量 | GB | 分区当前已使用的存储空间 |
| 已使用百分比 | 分区使用率 | % | 使用量占总容量的百分比 |

**注意事项：**
- 如果某个资源无法获取磁盘信息，仍会在报告中显示该资源的ID和名称，磁盘相关数据显示为0或N/A
- 资源ID是移动云平台分配的唯一标识，可用于后续的API调用和资源管理
- 每个云主机可能包含多个磁盘分区，每个分区占用一行数据

## API接口说明

本工具调用以下移动云API接口：

### 1. API接口列表

| 接口名称 | 请求路径 | 方法 | 功能描述 |
|----------|----------|------|----------|
| 获取资源列表 | `/api/edw/openapi/version2/v1/dawn/monitor/resources` | GET | 获取指定资源池中的所有云主机列表 |
| 获取产品性能指标 | `/api/edw/openapi/version2/v1/dawn/monitor/distribute/metricindicators` | GET | 获取云主机支持的性能监控指标 |
| 获取性能指标子节点 | `/api/edw/openapi/version2/v1/dawn/monitor/distribute/metricnode` | GET | 获取指定云主机的磁盘分区信息 |
| 获取性能数据 | `/api/edw/openapi/version2/v1/dawn/monitor/distribute/fetch` | POST | 获取指定时间范围内的磁盘使用量数据 |

### 2. API认证机制

移动云API使用AK/SK对称加密验证方式，每个请求都需要包含签名信息。

#### 请求格式规范

**完整请求URL格式：**
```
https://api-wuxi-1.cmecloud.cn:8443/api/edw/openapi/version2/v1/dawn/monitor/resources?AccessKey=d0742694e5784074af7b2c5ecff21455&SignatureMethod=HmacSHA1&SignatureNonce=f20198f6f88c42728d2e16a47b5df559&SignatureVersion=V2.0&Timestamp=2020-06-02T17%3A10%3A20Z&Version=2016-12-05&Signature=2ec4b467fdc7f342db5cbcd2835e36359549c0f9
```

**必需的请求头：**
```http
Content-Type: application/json
Accept: application/json
Accept-Charset: utf-8
Accept-Encoding: gzip, deflate
Host: api-wuxi-1.cmecloud.cn:8443
Version: 2016-12-05
AccessKey: d0742694e5784074af7b2c5ecff21455
Timestamp: Wed, 05 Sep 2012 23:00:00 GMT
Signature: 2ec4b467fdc7f342db5cbcd2835e36359549c0f9
SignatureMethod: HmacSHA1
SignatureVersion: V2.0
SignatureNonce: f20198f6f88c42728d2e16a47b5df559
```

#### 签名生成算法

签名生成遵循以下四个步骤：

**步骤1：构造规范化请求字符串**
```python
# 1. 对所有请求参数进行URL编码
# 2. 按参数名字母顺序排序
# 3. 使用&连接参数，格式：key1=value1&key2=value2
canonical_query_string = "AccessKey=d0742694e5784074af7b2c5ecff21455&SignatureMethod=HmacSHA1&..."
```

**步骤2：构造待签名字符串**
```python
# 格式：HTTP方法 + "\n" + URI路径 + "\n" + 规范化请求字符串
string_to_sign = "GET\n/api/edw/openapi/version2/v1/dawn/monitor/resources\n" + canonical_query_string
```

**步骤3：计算HMAC-SHA1签名**
```python
import hmac
import hashlib

# 使用Secret Key对待签名字符串进行HMAC-SHA1加密，并转换为十六进制
signature = hmac.new(
    secret_key.encode('utf-8'),
    string_to_sign.encode('utf-8'),
    hashlib.sha1
).hexdigest()
```

**步骤4：添加签名到请求**
```python
# 将生成的签名添加到请求参数中
params['Signature'] = signature
```

#### 公共请求参数

| 参数名 | 类型 | 必选 | 描述 | 示例值 |
|--------|------|------|------|--------|
| AccessKey | String | 是 | 移动云颁发的Access Key ID | d0742694e5784074af7b2c5ecff21455 |
| SignatureMethod | String | 是 | 签名方式，固定值 | HmacSHA1 |
| SignatureVersion | String | 是 | 签名算法版本，固定值 | V2.0 |
| SignatureNonce | String | 是 | 唯一随机数，防重放攻击 | f20198f6f88c42728d2e16a47b5df559 |
| Timestamp | String | 是 | 请求时间戳（GMT时间） | 2020-06-02T17:10:20Z |
| Version | String | 是 | API版本号，固定值 | 2016-12-05 |
| Signature | String | 是 | 请求签名 | 2ec4b467fdc7f342db5cbcd2835e36359549c0f9 |

#### 公共请求头

```http
Content-Type: application/json
Version: 2016-12-05
AccessKey: your_access_key
Timestamp: 2020-06-02T17:10:20Z
Signature: generated_signature
SignatureMethod: HmacSHA1
SignatureVersion: V2.0
SignatureNonce: unique_random_string
Host: api-wuxi-1.cmecloud.cn:8443
Accept: application/json
Accept-Charset: utf-8
Accept-Encoding: gzip, deflate
```

#### 签名生成过程

1. **构造规范化请求字符串**：对请求参数进行排序和URL编码
2. **构造待签名字符串**：包含HTTP方法、URI、规范化请求字符串
3. **计算签名**：使用HMAC-SHA1算法和Secret Key计算签名
4. **十六进制编码**：对签名结果进行十六进制编码

工具会自动处理所有签名计算过程，用户只需提供AK/SK即可。

## 监控指标

工具收集以下磁盘相关指标：

- `vm_realtime_disk_total`: 单个分区容量（GB）
- `vm_realtime_disk_used`: 单个分区的使用量（GB）
- `vm_realtime_disk_percent`: 单个分区使用率（%）

## 注意事项

1. **权限要求**: 需要有访问移动云监控API的权限和有效的AK/SK
2. **网络连接**: 确保能够访问移动云API接入地址（如 `api-wuxi-1.cmecloud.cn:8443`）
3. **资源池ID**: 需要提供正确的资源池ID，可参考[云监控帮助中心](https://ecloud.10086.cn/op-help-center/doc/article/47731)
4. **系统支持**: 磁盘监控指标仅支持Linux系统，且需要qemu-guest-agent支持
5. **数据时效**: 工具获取最近1小时的平均值数据
6. **API限制**: 请遵守移动云API的调用频率限制，避免过于频繁的请求
7. **时区设置**: API请求使用UTC时间，工具会自动处理时区转换

## 错误处理

- 如果某个资源无法获取磁盘数据，会在日志中记录警告，但不会中断整个收集过程
- 无法获取数据的字段在Excel中显示为 "N/A"
- 所有错误和警告都会记录在控制台日志中

## 性能优化

- 工具在API调用之间添加了适当的延迟，避免请求过于频繁
- 支持分页获取资源列表，适用于大量资源的场景
- 使用会话复用，提高网络请求效率

## 示例输出

```
2024-01-15 10:30:00 - INFO - 正在获取资源列表，资源池ID: CIDC-RP-01，产品类型: vm
2024-01-15 10:30:01 - INFO - 共获取到 25 个资源
2024-01-15 10:30:02 - INFO - 正在获取产品性能指标
2024-01-15 10:30:03 - INFO - 找到 3 个磁盘相关指标
2024-01-15 10:30:04 - INFO - 开始收集磁盘使用量数据
2024-01-15 10:30:05 - INFO - 正在处理资源 1/25: ECS-Test1 (f92e3c5f-ea24-4e9c-a7f7-4359d3286448)
2024-01-15 10:30:06 - INFO - 资源 ECS-Test1 找到 2 个分区: ['/sda', '/']
...
2024-01-15 10:35:00 - INFO - 数据收集完成，共收集到 50 条磁盘使用量记录
2024-01-15 10:35:01 - INFO - 正在导出数据到Excel文件: disk_usage_report.xlsx
2024-01-15 10:35:02 - INFO - Excel文件导出成功: disk_usage_report.xlsx
2024-01-15 10:35:02 - INFO - 共导出 50 条记录

磁盘使用量报告已生成: disk_usage_report.xlsx
共收集到 50 条记录
```

## 常见问题与故障排除

### 常见问题 FAQ

**Q1: 如何获取资源池ID？**
A: 资源池ID可以通过移动云控制台获取：
1. 登录移动云控制台
2. 进入「云主机」→「资源池管理」
3. 查看资源池列表中的ID列，格式通常为 `CIDC-RP-XX`

**Q2: 支持哪些时间格式？**
A: 支持以下时间格式：
- `YYYY-MM-DD HH:MM:SS`（如：2024-01-01 00:00:00）
- `YYYY-MM-DD`（如：2024-01-01，自动补充时间为 00:00:00）
- 相对时间：`7d`（7天前）、`30d`（30天前）、`1h`（1小时前）

**Q3: 如何处理大量数据？**
A: 对于大量数据的处理建议：
- 分时间段收集（如按月收集）
- 使用 `--verbose` 参数监控进度
- 确保有足够的磁盘空间存储Excel文件

**Q4: Excel文件过大怎么办？**
A: 当数据量过大时：
- 缩短时间范围
- 考虑导出为CSV格式（修改代码中的导出格式）
- 使用数据透视表进行汇总分析

**Q5: 如何验证API连接？**
A: 可以使用以下方法验证：
```bash
# 测试API连接
curl -X GET "https://api-wuxi-1.cmecloud.cn:8443/api/edw/openapi/version2/v1/dawn/monitor/resources?AccessKey=your_ak&..." \
  -H "Content-Type: application/json"
```

### 错误代码说明

| 错误代码 | 错误信息 | 原因 | 解决方案 |
|----------|----------|------|----------|
| 401 | Unauthorized | AK/SK错误或签名无效 | 检查认证信息和签名算法 |
| 403 | Forbidden | 权限不足 | 确认AK对应的用户有相应权限 |
| 404 | Not Found | 资源不存在 | 检查资源池ID是否正确 |
| 429 | Too Many Requests | 请求频率过高 | 降低请求频率，添加重试机制 |
| 500 | Internal Server Error | 服务器内部错误 | 稍后重试或联系技术支持 |

### 故障排除步骤

**1. 认证相关问题**
```bash
# 检查配置文件
type config.py  # Windows
cat config.py   # Linux/Mac

# 验证AK/SK格式（Windows PowerShell）
$ak = "your_access_key"
$sk = "your_secret_key"
Write-Host "Access Key长度: $($ak.Length)"
Write-Host "Secret Key长度: $($sk.Length)"

# 测试签名生成
python -c "from disk_usage_collector import DiskUsageCollector; print('签名测试通过')"

# 测试API连接
python test_api_connection.py
```

**2. 网络连接问题**
```bash
# 测试网络连通性（Windows）
ping api-wuxi-1.cmecloud.cn

# 测试端口连通性（Windows PowerShell）
Test-NetConnection -ComputerName api-wuxi-1.cmecloud.cn -Port 8443

# 检查DNS解析
nslookup api-wuxi-1.cmecloud.cn

# 测试HTTPS连接
curl -I https://api-wuxi-1.cmecloud.cn:8443
```

**3. 数据收集问题**
```bash
# 启用详细日志
python run_disk_collector.py --pool-id CIDC-RP-01 --verbose

# 检查日志文件（Windows）
Get-Content disk_usage_collector.log -Tail 50 -Wait

# 测试单个API接口
python -c "from disk_usage_collector import DiskUsageCollector; from config import *; collector = DiskUsageCollector(ACCESS_KEY, SECRET_KEY, BASE_URL); print(collector.get_resource_list('CIDC-RP-01'))"

# 检查依赖包
pip list | findstr "pandas\|openpyxl\|requests"
```

**4. 权限验证**
```bash
# 测试基本API权限
python -c "
from disk_usage_collector import DiskUsageCollector
from config import *
collector = DiskUsageCollector(ACCESS_KEY, SECRET_KEY, BASE_URL)
try:
    result = collector.get_resource_list('CIDC-RP-01')
    print(f'权限验证成功，获取到 {len(result)} 个资源')
except Exception as e:
    print(f'权限验证失败: {e}')
"

# 检查时间同步
python -c "import datetime; print(f'本地时间: {datetime.datetime.now()}'); print(f'UTC时间: {datetime.datetime.utcnow()}')"
```

**5. 数据完整性检查**
```bash
# 验证Excel文件
python -c "
import pandas as pd
try:
    df = pd.read_excel('disk_usage_report.xlsx')
    print(f'Excel文件读取成功，共 {len(df)} 行数据')
    print(f'列名: {list(df.columns)}')
    print(f'缺失数据统计:\n{df.isnull().sum()}')
except Exception as e:
    print(f'Excel文件验证失败: {e}')
"

# 检查数据质量
python -c "
import pandas as pd
df = pd.read_excel('disk_usage_report.xlsx')
print('数据质量报告:')
print(f'总记录数: {len(df)}')
print(f'唯一资源数: {df["资源名称"].nunique()}')
print(f'平均磁盘使用率: {df["磁盘使用率(%)"].mean():.2f}%')
print(f'最大磁盘使用率: {df["磁盘使用率(%)"].max():.2f}%')
"

### 调试模式

使用 `--verbose` 参数启用详细日志输出：

```bash
python run_disk_collector.py --pool-id CIDC-RP-01 --verbose
```

**详细日志包含：**
- API请求URL和参数
- 签名生成过程
- 响应状态码和内容
- 数据处理进度
- 错误堆栈信息

**调试技巧：**

1. **分步调试**
```bash
# 仅测试资源列表获取
python -c "from disk_usage_collector import DiskUsageCollector; from config import *; collector = DiskUsageCollector(ACCESS_KEY, SECRET_KEY, BASE_URL); print(len(collector.get_resource_list('CIDC-RP-01')))"

# 仅测试指标获取
python -c "from disk_usage_collector import DiskUsageCollector; from config import *; collector = DiskUsageCollector(ACCESS_KEY, SECRET_KEY, BASE_URL); print(len(collector.get_product_metrics()))"

# 测试单个资源的磁盘数据
python -c "from disk_usage_collector import DiskUsageCollector; from config import *; collector = DiskUsageCollector(ACCESS_KEY, SECRET_KEY, BASE_URL); print(collector.get_disk_usage_for_resource('resource_id', 'CIDC-RP-01'))"
```

2. **环境检查脚本**
```python
# 创建 check_environment.py
import sys
import importlib
import requests
from datetime import datetime

def check_environment():
    print("=== 环境检查报告 ===")
    print(f"Python版本: {sys.version}")
    
    # 检查必需的包
    required_packages = ['pandas', 'openpyxl', 'requests', 'urllib3']
    for package in required_packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, '__version__', 'Unknown')
            print(f"✓ {package}: {version}")
        except ImportError:
            print(f"✗ {package}: 未安装")
    
    # 检查网络连接
    try:
        response = requests.get('https://api-wuxi-1.cmecloud.cn:8443', timeout=5)
        print(f"✓ 网络连接: 正常 (状态码: {response.status_code})")
    except Exception as e:
        print(f"✗ 网络连接: 失败 ({e})")
    
    # 检查配置文件
    try:
        from config import ACCESS_KEY, SECRET_KEY, BASE_URL
        print(f"✓ 配置文件: 正常")
        print(f"  - ACCESS_KEY长度: {len(ACCESS_KEY)}")
        print(f"  - SECRET_KEY长度: {len(SECRET_KEY)}")
        print(f"  - BASE_URL: {BASE_URL}")
    except Exception as e:
        print(f"✗ 配置文件: 错误 ({e})")
    
    print(f"检查时间: {datetime.now()}")

if __name__ == '__main__':
    check_environment()
```

3. **性能监控**
```bash
# 监控内存使用
python -c "import psutil; import time; 
while True: 
    mem = psutil.virtual_memory(); 
    print(f'内存使用: {mem.percent}%'); 
    time.sleep(5)"

# 监控网络请求
python -c "import requests; import time; 
start = time.time(); 
response = requests.get('https://api-wuxi-1.cmecloud.cn:8443'); 
print(f'请求耗时: {time.time() - start:.2f}秒')"
```

### 日志文件

程序运行时会生成日志文件 `disk_usage_collector.log`，包含：
- 执行时间戳
- 详细的API调用信息
- 错误详情和堆栈跟踪
- 数据处理统计信息

**日志文件示例：**
```
2024-02-01 10:30:15,123 - INFO - 开始收集资源池 CIDC-RP-01 的磁盘使用量数据
2024-02-01 10:30:15,456 - DEBUG - 生成签名: GET\n/api/edw/openapi/version2/v1/dawn/monitor/resources\nAccessKey=xxx...
2024-02-01 10:30:16,789 - INFO - 获取到 15 台云主机资源
2024-02-01 10:30:17,012 - INFO - 开始获取磁盘分区信息
2024-02-01 10:30:20,345 - INFO - 数据收集完成，共处理 45 个磁盘分区
2024-02-01 10:30:21,678 - INFO - Excel报告已生成: disk_usage_CIDC-RP-01_20240201_103021.xlsx
```

### 性能优化建议

1. **并发处理**：对于大量云主机，可以考虑并发获取数据
2. **缓存机制**：对于重复查询，可以实现本地缓存
3. **分页处理**：对于大量数据，实现分页获取
4. **压缩传输**：启用gzip压缩减少网络传输时间

### 联系支持

如果遇到无法解决的问题，请提供以下信息：
- 完整的错误日志
- 使用的命令行参数
- 系统环境信息（Python版本、操作系统等）
- 问题复现步骤

## 许可证

本工具仅供内部使用，请遵守相关API使用条款。