#!/usr/bin/env python3
"""
API文档采集工具运行脚本

功能描述：
- 提供命令行接口来运行API文档采集
- 支持通过category或outline_id两种方式获取文档
- 支持自定义输出目录
- 简化采集的使用流程

使用方法：
    python run_collector.py [--category CATEGORY] [--outline-id OUTLINE_ID] [--output-dir OUTPUT_DIR]
    
参数说明：
    --category: 文档分类ID（可选）
               获取方法：在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
    --outline-id: 文档大纲ID（可选，优先级高于category）
    --output-dir: 输出目录名称（可选，默认为"api_docs"）

示例：
    python run_collector.py                                    # 使用默认参数（category=729）
    python run_collector.py --category 729                     # 指定分类ID
    python run_collector.py --outline-id 12345                 # 指定大纲ID
    python run_collector.py --category 729 --output-dir my_docs # 指定分类ID和输出目录
    python run_collector.py --outline-id 12345 --output-dir my_docs # 指定大纲ID和输出目录
"""

from api_doc_collector import APIDocCollector
import sys
import argparse

def main():
    """
    主函数 - 处理命令行参数并运行采集
    
    支持的参数：
    - --category: 分类ID（可选）
    - --outline-id: 大纲ID（可选，优先级高于category）
    - --output-dir: 输出目录（可选）
    """
    # 创建参数解析器
    parser = argparse.ArgumentParser(
        description="API文档采集工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python run_collector.py                                    # 使用默认参数（category=729）
  python run_collector.py --category 729                     # 指定分类ID
  python run_collector.py --outline-id 12345                 # 指定大纲ID
  python run_collector.py --category 729 --output-dir my_docs # 指定分类ID和输出目录
  python run_collector.py --outline-id 12345 --output-dir my_docs # 指定大纲ID和输出目录

获取category ID的方法：
  在浏览器地址栏查看，如 https://ecloud.10086.cn/op-help-center/doc/category/729 中的729
        """
    )
    
    parser.add_argument('--category', type=int, 
                       help='文档分类ID，从浏览器地址栏获取')
    parser.add_argument('--outline-id', type=int,
                       help='文档大纲ID，优先级高于category')
    parser.add_argument('--output-dir', default='api_docs',
                       help='输出目录名称（默认：api_docs）')
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.category and not args.outline_id:
        print("使用默认分类ID: 729 (对象存储EOS)")
        args.category = 729
    
    # 显示配置信息
    if args.outline_id:
        print(f"大纲ID: {args.outline_id}")
    if args.category:
        print(f"分类ID: {args.category}")
    print(f"输出目录: {args.output_dir}")
    print("-" * 50)
    
    # 创建采集实例并开始采集
    try:
        collector = APIDocCollector(category=args.category, outline_id=args.outline_id, output_dir=args.output_dir)
        collector.collect()
    except KeyboardInterrupt:
        print("\n用户中断操作")
        sys.exit(0)
    except Exception as e:
        print(f"运行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()