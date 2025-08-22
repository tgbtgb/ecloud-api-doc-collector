#!/usr/bin/env python3
"""
API文档采集工具 - 将树形结构的API文档转换为Markdown文件

功能描述：
- 支持四种采集模式：category（分类）、outline_id（大纲）、article_id（单个文章）、默认模式（全量文档）
- 通过API接口获取文档大纲树结构
- 递归下载所有文档内容并转换为Markdown格式
- 支持直接根据article_id获取单个文档
- 支持默认模式：无参数时自动获取所有可用的API文档
- 同时下载PDF文件（如果可用）
- 保持原有的目录结构
- 支持错误处理和重试机制

作者：AI Assistant
版本：1.2
"""

import requests
import os
import re
import time
import html2text
import json
import html
from urllib.parse import quote


class APIDocCollector:
    """
    API文档采集类
    
    主要功能：
    1. 支持通过category、outline_id、article_id或默认模式四种方式获取文档
    2. 通过API获取文档大纲树结构
    3. 递归下载文档内容
    4. 将HTML内容转换为Markdown格式
    5. 下载PDF文件（如果可用）
    6. 保持原有的目录结构保存文件
    7. 默认模式：当所有参数都为None时，自动获取所有可用的API文档
    
    属性：
        category (int, optional): 文档分类ID，用于获取outline_id
        outline_id (int, optional): 文档大纲ID，可直接指定或通过category获取
        article_id (str, optional): 文章ID，用于直接获取单个文档
        output_dir (str): 输出目录路径
        base_api_url (str): API基础URL
        session (requests.Session): HTTP会话对象
        h (html2text.HTML2Text): HTML转Markdown转换器
    
    采集模式优先级：
        article_id > outline_id > category > 默认模式（全量文档）
    """
    
    def __init__(self, category=None, outline_id=None, article_id=None, output_dir="api_docs"):
        """
        初始化采集对象
        
        Args:
            category (int, optional): 文档分类ID，用于获取outline_id和文档树结构
                                    获取方法：在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
            outline_id (int, optional): 文档大纲ID，可直接指定，优先级高于category
            article_id (str, optional): 文章ID，用于直接获取单个文档，优先级最高
            output_dir (str): 输出目录路径，默认为"api_docs"
            
        注意：
            - 如果所有参数都为None，将进入默认模式，获取所有可用的API文档
            - 参数优先级：article_id > outline_id > category > 默认模式
        """
        # 移除必须提供参数的限制，支持默认模式
        
        self.category = category
        self.outline_id = outline_id  # 可直接指定或通过API获取
        self.article_id = article_id  # 直接指定文章ID
        self.output_dir = output_dir
        # 移动云API文档的基础URL
        self.base_api_url = "https://ecloud.10086.cn/op-help-center/request-api/service-api"
        
        # 创建HTTP会话并设置请求头
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
        })

        # 初始化HTML转Markdown转换器
        self.h = html2text.HTML2Text()
        self.h.ignore_links = False  # 保留链接
        self.h.ignore_images = False  # 保留图片

    def get_category_info(self):
        """
        通过category获取outline_id
        
        说明：
        - category可以从浏览器地址栏获取，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
        - 通过API接口 /category/info/{category} 获取分类信息，包含outline_id
        
        Returns:
            dict/None: 分类信息，包含outline_id，失败时返回None
        """
        if not self.category:
            print("未提供category，跳过获取分类信息")
            return None
            
        url = f"{self.base_api_url}/category/info/{self.category}"
        print(f"获取分类信息: {url}")

        data = self.get_api_data(url)
        if not data:
            print("获取分类信息失败")
            return None

        # 提取outline_id
        outline_id = data.get('outlineId')
        if outline_id:
            self.outline_id = outline_id
            print(f"获取到outline_id: {outline_id}")
            return data
        else:
            print("分类信息中未找到outline_id")
            return None

    def get_api_data(self, url):
        """
        获取API数据，包含错误处理
        
        Args:
            url (str): API请求URL
            
        Returns:
            dict/None: API返回的数据，失败时返回None
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()  # 检查HTTP状态码
            data = response.json()

            # 检查API返回的业务状态码
            if data.get('code') == 200:
                return data.get('data')
            else:
                print(f"API错误 {url}: {data.get('msg', '未知错误')}")
                return None
        except Exception as e:
            print(f"获取数据失败 {url}: {e}")
            return None

    def sanitize_filename(self, name):
        """
        清理文件名，确保文件系统兼容性
        
        Args:
            name (str): 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        # 移除HTML标签并解码HTML实体
        name = re.sub(r'<[^>]+>', '', name)
        name = html.unescape(name).strip()

        # 替换无效字符为下划线
        invalid_chars = r'[<>:"/\\|?*]'
        name = re.sub(invalid_chars, '_', name)

        # 限制长度并移除多余空格
        name = re.sub(r'\s+', ' ', name)[:100]
        return name.strip()

    def get_outline_tree(self):
        """
        从API获取文档大纲树结构
        
        Returns:
            dict/None: 大纲树数据，失败时返回None
        """
        url = f"{self.base_api_url}/outline/tree?outlineId={self.outline_id}"
        print(f"获取大纲树: {url}")

        data = self.get_api_data(url)
        if data:
            return data
        
        # 如果直接获取失败，尝试备用方案：获取全量目录树并查找对应节点
        print(f"直接获取outline_id {self.outline_id} 的目录树失败，尝试从全量目录树中查找")
        return self.get_outline_tree_fallback()

    def get_outline_tree_fallback(self):
        """
        备用方案：从全量目录树中查找指定outline_id的子树
        
        Returns:
            dict/None: 找到的子树数据，失败时返回None
        """
        url = f"{self.base_api_url}/outline/api/tree"
        print(f"获取全量目录树: {url}")
        
        data = self.get_api_data(url)
        if not data:
            print("获取全量目录树失败")
            return None
        
        # 在全量树中查找指定的outline_id节点
        target_node = self.find_node_by_outline_id(data, self.outline_id)
        if target_node:
            print(f"在全量目录树中找到outline_id {self.outline_id} 对应的节点: {target_node.get('name', '未知')}")
            return target_node
        else:
            print(f"在全量目录树中未找到outline_id {self.outline_id} 对应的节点")
            return None
    
    def get_full_outline_tree(self):
        """
        获取全量文档树，用于默认模式
        
        当没有提供任何参数时，使用此方法获取所有可用的API文档树结构
        
        Returns:
            dict/None: 全量文档树数据，失败时返回None
        """
        url = f"{self.base_api_url}/outline/api/tree"
        print(f"默认模式：获取全量文档树: {url}")
        
        data = self.get_api_data(url)
        if data:
            print("成功获取全量文档树")
            return data
        else:
            print("获取全量文档树失败")
            return None
    

    

    
    def find_node_by_outline_id(self, node, target_outline_id):
        """
        递归查找指定outline_id的节点 - 深度优先遍历整个JSON树
        
        Args:
            node (dict/list): 当前节点或节点列表
            target_outline_id (int/str): 目标outline_id
            
        Returns:
            dict/None: 找到的节点，未找到时返回None
        """
        if not node:
            return None
        
        # 确保target_outline_id为字符串和整数两种格式都能匹配
        target_id_str = str(target_outline_id)
        target_id_int = None
        try:
            target_id_int = int(target_outline_id)
        except (ValueError, TypeError):
            pass
        
        # 处理单个节点或节点列表
        nodes = [node] if isinstance(node, dict) else node
        
        for item in nodes:
            if not isinstance(item, dict):
                continue
            
            current_id = item.get('id')
            
            # 检查当前节点的id（支持字符串和整数比较）
            if (current_id == target_outline_id or 
                current_id == target_id_str or 
                (target_id_int is not None and current_id == target_id_int)):
                return item
            
            # 递归查找子节点 - 确保深度优先遍历所有子节点
            children = item.get('children', [])
            if children and isinstance(children, list) and len(children) > 0:
                result = self.find_node_by_outline_id(children, target_outline_id)
                if result:
                    return result
        
        return None

    def parse_tree_node(self, node, level=0):
        """
        解析API树节点结构，递归处理
        
        Args:
            node (dict/list): 树节点数据
            level (int): 当前层级深度
            
        Returns:
            list: 解析后的节点列表
        """
        if not node:
            return []

        items = []

        # 处理单个节点或节点列表
        nodes = [node] if isinstance(node, dict) else node

        for item in nodes:
            if not isinstance(item, dict):
                continue

            title = item.get('name', '')
            article_id = item.get('articleId')
            children_data = item.get('children', [])

            # 递归解析子节点
            children = []
            if children_data:
                children = self.parse_tree_node(children_data, level + 1)

            # 创建节点结构
            parsed_item = {
                'title': title,
                'article_id': article_id,
                'level': level,
                'children': children,
                'is_leaf': len(children) == 0 and article_id is not None,  # 判断是否为叶子节点
                'raw_data': item  # 保留原始数据用于调试
            }

            items.append(parsed_item)
            print(f"{'  ' * level}发现: {title} (文章ID: {article_id}, 叶子节点: {parsed_item['is_leaf']})")

        return items

    def get_article_info(self, article_id):
        """
        获取文章信息
        
        Args:
            article_id (str): 文章ID
            
        Returns:
            dict/None: 文章信息，失败时返回None
        """
        url = f"{self.base_api_url}/article/info/{article_id}"
        print(f"获取文章信息: {url}")

        return self.get_api_data(url)

    def get_article_content(self, content_uid):
        """
        获取文章内容
        
        Args:
            content_uid (str): 内容UID
            
        Returns:
            str/None: HTML内容，失败时返回None
        """
        url = f"{self.base_api_url}/article/content/{content_uid}"
        print(f"获取文章内容: {url}")

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取内容失败 {url}: {e}")
            return None

    def download_pdf_file(self, pdf_uid, pdf_filename, file_path):
        """
        下载PDF文件
        
        Args:
            pdf_uid (str): PDF文件UID
            pdf_filename (str): PDF文件名
            file_path (str): 保存路径
            
        Returns:
            bool: 下载是否成功
        """
        url = f"{self.base_api_url}/resource/file/{pdf_uid}/filename/{pdf_filename}"
        print(f"下载PDF文件: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            # 检查响应是否为PDF文件
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' in content_type or response.content.startswith(b'%PDF'):
                # 保存PDF内容
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"PDF已保存: {file_path}")
                return True
            else:
                print(f"响应不是PDF文件，内容类型: {content_type}")
                return False
                
        except Exception as e:
            print(f"下载PDF失败 {url}: {e}")
            return False

    def extract_content_and_pdf(self, article_id, base_file_path):
        """
        提取文章内容并下载PDF（如果可用）
        
        使用多重回退机制：
        1. 优先尝试pdfPublished（通常格式更好）
        2. 尝试contentPublished
        3. 尝试content字段
        
        Args:
            article_id (str): 文章ID
            base_file_path (str): 基础文件路径（不含扩展名）
            
        Returns:
            str/None: Markdown内容，失败时返回None
        """
        # 首先获取文章信息
        article_info = self.get_article_info(article_id)
        if not article_info:
            return None

        # 按优先级尝试多个内容源
        content_sources = []
        pdf_info = None
        
        # 1. 优先尝试pdfPublished（通常格式更好）
        pdf_published = article_info.get('pdfPublished')
        if pdf_published:
            try:
                pdf_data = json.loads(pdf_published)
                pdf_uid = pdf_data.get('uid')
                pdf_filename = pdf_data.get('filename', 'document.pdf')
                if pdf_uid:
                    content_sources.append(('pdfPublished', pdf_uid))
                    pdf_info = {'uid': pdf_uid, 'filename': pdf_filename}
            except:
                pass

        # 2. 尝试contentPublished
        content_published = article_info.get('contentPublished')
        if content_published:
            content_sources.append(('contentPublished', content_published))

        # 3. 尝试content字段
        content = article_info.get('content')
        if content:
            content_sources.append(('content', content))

        # 如果可用，优先下载PDF
        if pdf_info:
            pdf_file_path = f"{base_file_path}.pdf"
            pdf_downloaded = self.download_pdf_file(pdf_info['uid'], pdf_info['filename'], pdf_file_path)
            if pdf_downloaded:
                print(f"PDF下载成功: {pdf_file_path}")
            else:
                print(f"PDF下载失败，继续使用Markdown格式")

        # 尝试每个内容源直到成功获取Markdown内容
        for source_name, content_uid in content_sources:
            print(f"尝试 {source_name} 获取文章 {article_id}: {content_uid}")
            
            html_content = self.get_article_content(content_uid)
            if html_content:
                print(f"成功从 {source_name} 获取内容")
                # 转换为Markdown
                markdown_content = self.h.handle(html_content)
                return markdown_content.strip()
            else:
                print(f"从 {source_name} 获取内容失败")

        print(f"未找到可访问的内容，文章ID: {article_id}")
        return None

    def create_directory_structure(self, items, current_path=""):
        """
        根据树结构创建目录和文件
        
        Args:
            items (list): 节点列表
            current_path (str): 当前路径
        """
        if not items:
            return

        for item in items:
            # 检查项目是否有必需的键
            if not isinstance(item, dict) or 'title' not in item:
                print(f"跳过无效项目: {item}")
                continue

            safe_title = self.sanitize_filename(item['title'])
            item_path = os.path.join(current_path, safe_title)

            # 检查是否为有文章内容的叶子节点
            is_leaf = item.get('is_leaf', False)
            article_id = item.get('article_id')

            if is_leaf and article_id:
                # 这是有内容的叶子节点 - 创建Markdown文件
                print(f"处理叶子节点: {item['title']} (文章ID: {article_id})")

                # 确保目录存在
                dir_path = os.path.join(self.output_dir, current_path)
                os.makedirs(dir_path, exist_ok=True)

                # 基础文件路径（不含扩展名）
                base_file_path = os.path.join(self.output_dir, item_path)
                
                content = self.extract_content_and_pdf(article_id, base_file_path)
                if content:
                    # 写入Markdown文件
                    md_file_path = f"{base_file_path}.md"
                    with open(md_file_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {item['title']}\n\n")
                        f.write(content)

                    print(f"已创建: {md_file_path}")
                else:
                    print(f"未找到内容: {item['title']}")

                # 添加延迟以保持礼貌
                time.sleep(1)

            elif item.get('children'):
                # 这是父节点 - 创建目录并递归处理
                print(f"创建目录: {item['title']}")
                dir_path = os.path.join(self.output_dir, item_path)
                os.makedirs(dir_path, exist_ok=True)

                # 处理子节点
                self.create_directory_structure(item['children'], item_path)

            else:
                print(f"跳过没有内容或子节点的节点: {item['title']}")

    def print_tree_structure(self, items, indent=0):
        """
        调试方法：打印树结构
        
        Args:
            items (list): 节点列表
            indent (int): 缩进级别
        """
        for item in items:
            prefix = "  " * indent
            is_leaf = item.get('is_leaf', False)
            article_id = item.get('article_id', '无文章ID')
            node_type = "叶子" if is_leaf else "分支"
            print(f"{prefix}[{node_type}] {item.get('title', '无标题')} -> 文章ID: {article_id}")

            if item.get('children'):
                self.print_tree_structure(item['children'], indent + 1)

    def collect_single_article(self):
        """
        采集单个文章的函数
        
        执行流程：
        1. 根据article_id获取文章信息
        2. 提取文章内容和PDF
        3. 保存为Markdown文件
        
        Returns:
            bool: 采集是否成功
        """
        if not self.article_id:
            print("错误：未提供article_id")
            return False
        
        print(f"开始采集单个文章，article_id: {self.article_id}")
        
        # 获取文章信息
        article_info = self.get_article_info(self.article_id)
        if not article_info:
            print(f"获取文章信息失败，article_id: {self.article_id}")
            return False
        
        # 获取文章标题
        article_title = article_info.get('title', f'article_{self.article_id}')
        print(f"文章标题: {article_title}")
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 清理文件名
        safe_title = self.sanitize_filename(article_title)
        base_file_path = os.path.join(self.output_dir, safe_title)
        
        # 提取内容和PDF
        content = self.extract_content_and_pdf(self.article_id, base_file_path)
        if content:
            # 写入Markdown文件
            md_file_path = f"{base_file_path}.md"
            with open(md_file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {article_title}\n\n")
                f.write(content)
            
            print(f"文章已保存: {md_file_path}")
            return True
        else:
            print(f"未找到文章内容，article_id: {self.article_id}")
            return False

    def collect(self):
        """
        主要的采集函数
        
        执行流程：
        1. 如果提供了article_id，则直接采集单个文章
        2. 如果提供了category但未提供outline_id，则通过category获取outline_id
        3. 如果没有提供任何参数，则进入默认模式，获取全量文档树
        4. 获取文档大纲树
        5. 解析树结构
        6. 创建输出目录
        7. 递归处理所有节点
        """
        # 优先处理article_id模式
        if self.article_id:
            return self.collect_single_article()
        
        # 确定使用方式
        if self.outline_id:
            print(f"开始API采集，使用outline_id: {self.outline_id}")
        elif self.category:
            print(f"开始API采集，使用category: {self.category}")
        else:
            print("开始API采集，使用默认模式：获取所有可用文档")

        # 获取文档树数据
        tree_data = None
        
        if self.category and not self.outline_id:
            # 通过category获取outline_id，然后获取对应的树
            category_info = self.get_category_info()
            if not category_info:
                print("获取分类信息失败，无法继续")
                return
            print(f"通过category获取到outline_id: {self.outline_id}")
            tree_data = self.get_outline_tree()
        elif self.outline_id:
            # 直接使用outline_id获取树
            print(f"直接使用outline_id: {self.outline_id}")
            tree_data = self.get_outline_tree()
        else:
            # 默认模式：获取全量文档树
            tree_data = self.get_full_outline_tree()
        
        if not tree_data:
            print("获取文档树失败")
            return

        # 解析树结构
        tree_items = self.parse_tree_node(tree_data)
        if not tree_items:
            print("未找到树结构")
            return

        print(f"找到 {len(tree_items)} 个顶级项目")

        # 调试：打印树结构
        print("\n=== 树结构 ===")
        self.print_tree_structure(tree_items)
        print("=============\n")

        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)

        # 处理树结构
        self.create_directory_structure(tree_items)

        print(f"采集完成。文件已保存到: {self.output_dir}")


def main():
    """
    主函数 - 程序入口点
    
    配置说明：
    - category: 文档分类ID，729为对象存储EOS的分类ID
               获取方法：在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
    - outline_id: 文档大纲ID，可直接指定，优先级高于category
    - article_id: 文章ID，用于直接获取单个文档，优先级最高
    - output_directory: 输出目录名称
    
    使用示例：
    1. 默认模式（获取所有文档）: collector = APIDocCollector(output_dir="api_docs")
    2. 使用category: collector = APIDocCollector(category=729, output_dir="api_docs")
    3. 使用outline_id: collector = APIDocCollector(outline_id=12345, output_dir="api_docs")
    4. 使用article_id: collector = APIDocCollector(article_id="article123", output_dir="api_docs")
    5. 同时提供多个参数: collector = APIDocCollector(category=729, outline_id=12345, article_id="article123", output_dir="api_docs")  # article_id优先级最高
    
    采集模式优先级：article_id > outline_id > category > 默认模式
     """
    # 使用示例（三选一）：
    # 1. 按分类采集（推荐）
    # collector = APIDocCollector(category=729, output_dir="api_docs")
    
    # 2. 按大纲ID采集
    # collector = APIDocCollector(outline_id=12345, output_dir="api_docs")
    
    # 3. 按文章ID采集单个文档
    # collector = APIDocCollector(article_id="article123", output_dir="api_docs")
    
    # 配置参数 - 可以选择使用category、outline_id或article_id
    category = 729  # 对象存储 EOS 的 category ID，从浏览器地址栏获取
    outline_id = None  # 可以直接指定outline_id，优先级高于category
    article_id = None  # 可以直接指定article_id，优先级最高
    output_directory = "api_docs"

    # 创建采集器并运行
    collector = APIDocCollector(category=category, outline_id=outline_id, article_id=article_id, output_dir=output_directory)
    collector.collect()


if __name__ == "__main__":
    main()