#!/usr/bin/env python3
"""
API文档采集工具运行脚本

功能描述：
- 提供命令行接口来运行API文档采集
- 支持通过category、outline_id、article_id或默认模式四种方式获取文档
- 支持自定义输出目录
- 简化采集的使用流程
- 默认模式：无参数时自动获取所有可用的API文档

使用方法：
    python run_collector.py [--category CATEGORY] [--outline-id OUTLINE_ID] [--article-id ARTICLE_ID] [--output-dir OUTPUT_DIR]
    
参数说明：
    无参数: 默认模式，获取所有可用的API文档
    --category: 文档分类ID（可选）
               获取方法：在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
    --outline-id: 文档大纲ID（可选，优先级高于category）
    --article-id: 文章ID（可选，优先级最高，用于直接获取单个文档）
    --output-dir: 输出目录名称（可选，默认为"api_docs"）
    
采集模式优先级：article_id > outline_id > category > 默认模式

示例：
    python run_collector.py                                    # 默认模式，获取所有可用文档
    python run_collector.py --output-dir all_docs              # 默认模式，指定输出目录
    python run_collector.py --category 729                     # 指定分类ID
    python run_collector.py --outline-id 12345                 # 指定大纲ID
    python run_collector.py --article-id "abc123"              # 直接获取单个文章
    python run_collector.py --category 729 --output-dir my_docs # 指定分类ID和输出目录
    python run_collector.py --article-id "abc123" --output-dir my_docs # 指定文章ID和输出目录
"""

from api_doc_collector import APIDocCollector
import sys
import argparse

def main():
    """
    主函数 - 处理命令行参数并运行采集
    
    支持的采集模式：
    - 默认模式: 无参数时获取所有可用文档（优先级最低）
    - --category: 分类ID（可选）
    - --outline-id: 大纲ID（可选，优先级高于category）
    - --article-id: 文章ID（可选，优先级最高）
    - --output-dir: 输出目录（可选）
    
    采集模式优先级：article_id > outline_id > category > 默认模式
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="API文档采集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python run_collector.py                                    # 默认模式，获取所有可用文档
  python run_collector.py --output-dir all_docs              # 默认模式，指定输出目录
  python run_collector.py --category 729                     # 指定分类ID
  python run_collector.py --outline-id 12345                 # 指定大纲ID
  python run_collector.py --article-id "abc123"              # 直接获取单个文章
  python run_collector.py --category 729 --output-dir my_docs # 指定分类ID和输出目录
  python run_collector.py --article-id "abc123" --output-dir my_docs # 指定文章ID和输出目录

采集模式优先级：article_id > outline_id > category > 默认模式

获取category ID的方法：
  在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729

获取article ID的方法：
  在文档页面的浏览器地址栏查看，或通过API接口获取
        """
    )
    
    parser.add_argument('--category', type=int, 
                       help='文档分类ID，从浏览器地址栏获取')
    parser.add_argument('--outline-id', type=int,
                       help='文档大纲ID，优先级高于category')
    parser.add_argument('--article-id', type=str,
                       help='文章ID，优先级最高，用于直接获取单个文档')
    parser.add_argument('--output-dir', default='api_docs',
                       help='输出目录名称（默认：api_docs）')
    
    args = parser.parse_args()
    
    # 验证参数 - 支持默认模式
    if not args.category and not args.outline_id and not args.article_id:
        print("使用默认模式: 获取所有可用的API文档")
    
    # 显示配置信息
    if args.article_id:
        print(f"采集模式: 单个文章")
        print(f"文章ID: {args.article_id}")
    elif args.outline_id:
        print(f"采集模式: 大纲文档")
        print(f"大纲ID: {args.outline_id}")
    elif args.category:
        print(f"采集模式: 分类文档")
        print(f"分类ID: {args.category}")
    else:
        print(f"采集模式: 默认模式（全量文档）")
    print(f"输出目录: {args.output_dir}")
    print("-" * 50)
    
    # 创建采集实例并开始采集
    try:
        collector = APIDocCollector(category=args.category, outline_id=args.outline_id, article_id=args.article_id, output_dir=args.output_dir)
        collector.collect()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()