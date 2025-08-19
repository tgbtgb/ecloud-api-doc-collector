#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘使用量收集器运行示例

该脚本提供了运行磁盘使用量收集器的示例，包含常用的参数配置。

使用方法:
python run_disk_collector.py
"""

import subprocess
import sys
import os

def run_disk_collector():
    """运行磁盘使用量收集器"""
    
    # 配置参数
    pool_id = input("请输入资源池ID: ").strip()
    if not pool_id:
        print("错误: 资源池ID不能为空")
        return
    
    # 获取移动云密钥信息
    print("\n⚠️  请提供移动云API密钥信息:")
    print("   这些密钥可以在移动云控制台的【AccessKey管理】模块中获取")
    access_key = input("请输入Access Key ID (AK): ").strip()
    if not access_key:
        print("错误: Access Key ID不能为空")
        return
    
    secret_key = input("请输入Secret Access Key (SK): ").strip()
    if not secret_key:
        print("错误: Secret Access Key不能为空")
        return
    
    product_type = input("\n请输入产品类型 (默认: vm): ").strip() or "vm"
    output_file = input("请输入输出文件名 (默认: disk_usage_report.xlsx): ").strip() or "disk_usage_report.xlsx"
    
    # 构建命令
    cmd = [
        sys.executable,
        "disk_usage_collector.py",
        "--pool-id", pool_id,
        "--product-type", product_type,
        "--output", output_file,
        "--access-key", access_key,
        "--secret-key", secret_key
    ]
    
    print(f"\n正在执行命令: {' '.join(cmd)}")
    print("请稍候...\n")
    
    try:
        # 运行收集器
        result = subprocess.run(cmd, check=True, capture_output=False)
        
        if result.returncode == 0:
            print(f"\n✅ 磁盘使用量报告生成成功!")
            print(f"📁 输出文件: {output_file}")
            
            # 检查文件是否存在
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"📊 文件大小: {file_size} 字节")
            
        else:
            print(f"❌ 程序执行失败，退出码: {result.returncode}")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 程序执行失败: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
    except Exception as e:
        print(f"❌ 发生未知错误: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("🔍 磁盘使用量收集器")
    print("=" * 50)
    print()
    print("该工具将收集所有服务器的磁盘使用量信息，并生成Excel报告。")
    print("报告包含: 资源名称、分区、磁盘容量、已使用大小、已使用百分比")
    print()
    
    # 检查依赖文件
    if not os.path.exists("disk_usage_collector.py"):
        print("❌ 错误: 找不到 disk_usage_collector.py 文件")
        return
    
    try:
        run_disk_collector()
    except KeyboardInterrupt:
        print("\n👋 再见!")

if __name__ == '__main__':
    main()