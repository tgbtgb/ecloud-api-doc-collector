#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
磁盘使用量收集器

该脚本用于收集所有服务器的磁盘使用量信息，并生成Excel报告。
包含以下信息：resourceName、分区、磁盘容量大小、已使用大小、已使用百分比

使用方法:
python disk_usage_collector.py --pool-id <资源池ID> [--product-type vm] [--output disk_usage_report.xlsx]
"""

import argparse
import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import logging
from ecloud_auth import ECloudAuth

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DiskUsageCollector:
    """磁盘使用量收集器类"""
    
    def __init__(self, pool_id: str, access_key: str, secret_key: str, product_type: str = "vm", base_url: str = "https://api-wuxi-1.cmecloud.cn:8443"):
        self.pool_id = pool_id
        self.product_type = product_type
        self.access_key = access_key
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = requests.Session()
        
        # 初始化鉴权实例
        self.auth = ECloudAuth(access_key, secret_key)
        
        # 设置请求头
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Accept-Charset': 'utf-8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'DiskUsageCollector/1.0'
        })
        
        # 磁盘相关指标
        self.disk_metrics = {
            'vm_realtime_disk_total': '单个分区容量',
            'vm_realtime_disk_used': '单个分区的使用量', 
            'vm_realtime_disk_percent': '单个分区使用率'
        }
    

    
    def get_resource_list(self, page_size: int = 100) -> List[Dict]:
        """获取资源列表"""
        logger.info(f"正在获取资源列表，资源池ID: {self.pool_id}，产品类型: {self.product_type}")
        
        all_resources = []
        page_num = 1
        
        while True:
            servlet_path = "/api/edw/openapi/version2/v1/dawn/monitor/resources"
            params = {
                'poolId': self.pool_id,
                'productType': self.product_type,
                'pageNum': str(page_num),
                'pageSize': str(page_size)
            }
            
            try:
                # 对请求进行签名
                signed_params = self.auth.sign_request('GET', servlet_path, params)
                
                # 手动构建查询字符串，避免requests再次编码
                query_string = self.auth.create_canonical_query_string(signed_params)
                
                # 构建完整URL
                url = f"{self.base_url}{servlet_path}?{query_string}"
                
                # 添加完整的请求头
                host = self.base_url.replace('https://', '').replace('http://', '').split('/')[0]
                headers = {
                    'Host': host,
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Accept-Charset': 'utf-8'
                }
                
                logger.debug(f"请求URL: {url}")
                logger.debug(f"请求头: {headers}")
                logger.debug(f"查询字符串: {query_string}")
                
                response = self.session.get(url, headers=headers)
                logger.debug(f"响应状态码: {response.status_code}")
                logger.debug(f"响应内容: {response.text}")
                
                # 如果响应不是200，记录详细错误信息
                if response.status_code != 200:
                    logger.error(f"API请求失败 - 状态码: {response.status_code}")
                    logger.error(f"响应头: {dict(response.headers)}")
                    logger.error(f"错误响应内容: {response.text}")
                    try:
                        error_data = response.json()
                        logger.error(f"错误详情: {error_data}")
                    except:
                        logger.error("无法解析错误响应为JSON")
                
                response.raise_for_status()
                data = response.json()
                
                if data.get('code') != '000000':
                    logger.error(f"获取资源列表失败: {data.get('message')}")
                    break
                
                entity = data.get('entity', {})
                content = entity.get('content', [])
                
                if not content:
                    break
                    
                all_resources.extend(content)
                
                # 检查是否还有更多页
                if page_num >= entity.get('pageCount', 1):
                    break
                    
                page_num += 1
                time.sleep(0.1)  # 避免请求过快
                
            except Exception as e:
                logger.error(f"获取资源列表时发生错误: {str(e)}")
                break
        
        logger.info(f"共获取到 {len(all_resources)} 个资源")
        return all_resources
    
    def get_metric_indicators(self) -> List[Dict]:
        """获取产品性能指标"""
        logger.info("正在获取产品性能指标")
        
        servlet_path = "/api/edw/openapi/version2/v1/dawn/monitor/distribute/metricindicators"
        params = {
            'poolId': self.pool_id,
            'productType': self.product_type
        }
        
        try:
            # 对请求进行签名
            signed_params = self.auth.sign_request('GET', servlet_path, params)
            
            # 手动构建查询字符串，避免requests再次编码
            query_string = self.auth.create_canonical_query_string(signed_params)
            
            # 构建完整URL
            url = f"{self.base_url}{servlet_path}?{query_string}"
            
            # 添加完整的请求头
            host = self.base_url.replace('https://', '').replace('http://', '').split('/')[0]
            headers = {
                'Host': host,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Charset': 'utf-8'
            }
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"查询字符串: {query_string}")
            
            response = self.session.get(url, headers=headers)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != '000000':
                logger.error(f"获取性能指标失败: {data.get('message')}")
                return []
            
            indicators = data.get('entity', [])
            
            # 筛选磁盘相关指标
            disk_indicators = []
            for indicator in indicators:
                if indicator.get('metricName') in self.disk_metrics:
                    disk_indicators.append(indicator)
            
            logger.info(f"找到 {len(disk_indicators)} 个磁盘相关指标")
            return disk_indicators
            
        except Exception as e:
            logger.error(f"获取性能指标时发生错误: {str(e)}")
            return []
    
    def get_metric_nodes(self, resource_id: str, metric_name: str) -> List[str]:
        """获取性能指标子节点名称（分区信息）"""
        servlet_path = "/api/edw/openapi/version2/v1/dawn/monitor/distribute/metricnode"
        params = {
            'poolId': self.pool_id,
            'metricName': metric_name,
            'resourceId': resource_id
        }
        
        try:
            # 对请求进行签名
            signed_params = self.auth.sign_request('GET', servlet_path, params)
            
            # 手动构建查询字符串，避免requests再次编码
            query_string = self.auth.create_canonical_query_string(signed_params)
            
            # 构建完整URL
            url = f"{self.base_url}{servlet_path}?{query_string}"
            
            # 添加完整的请求头
            host = self.base_url.replace('https://', '').replace('http://', '').split('/')[0]
            headers = {
                'Host': host,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Charset': 'utf-8'
            }
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"查询字符串: {query_string}")
            
            response = self.session.get(url, headers=headers)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != '000000':
                logger.warning(f"获取资源 {resource_id} 的 {metric_name} 子节点失败: {data.get('message')}")
                return []
            
            return data.get('entity', [])
            
        except Exception as e:
            logger.warning(f"获取资源 {resource_id} 的 {metric_name} 子节点时发生错误: {str(e)}")
            return []
    
    def get_performance_data(self, resource_id: str, metrics: List[Dict], 
                           start_time: str, end_time: str) -> List[Dict]:
        """获取性能数据"""
        servlet_path = "/api/edw/openapi/version2/v1/dawn/monitor/distribute/fetch"
        params = {'poolId': self.pool_id}
        
        payload = {
            'startTime': start_time,
            'endTime': end_time,
            'resourceId': resource_id,
            'productType': self.product_type,
            'performanceDataAggType': 'MAX',
            'metrics': metrics
        }
        
        try:
            # 对请求进行签名
            signed_params = self.auth.sign_request('POST', servlet_path, params)
            
            # 手动构建查询字符串，避免requests再次编码
            query_string = self.auth.create_canonical_query_string(signed_params)
            
            # 构建完整URL
            url = f"{self.base_url}{servlet_path}?{query_string}"
            
            # 添加完整的请求头
            host = self.base_url.replace('https://', '').replace('http://', '').split('/')[0]
            headers = {
                'Host': host,
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Accept-Charset': 'utf-8'
            }
            
            logger.debug(f"请求URL: {url}")
            logger.debug(f"请求头: {headers}")
            logger.debug(f"查询字符串: {query_string}")
            logger.debug(f"请求体: {payload}")
            
            response = self.session.post(url, json=payload, headers=headers)
            logger.debug(f"响应状态码: {response.status_code}")
            logger.debug(f"响应内容: {response.text}")
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') != '000000':
                logger.warning(f"获取资源 {resource_id} 性能数据失败: {data.get('message')}")
                return []
            
            return data.get('entity', [])
            
        except Exception as e:
            logger.warning(f"获取资源 {resource_id} 性能数据时发生错误: {str(e)}")
            return []
    
    def collect_disk_usage_data(self, start_time: str = None, end_time: str = None) -> List[Dict]:
        """收集磁盘使用量数据
        
        Args:
            start_time: 开始时间，格式：'YYYY-MM-DD HH:MM:SS'，如果未提供则默认为当前时间-1天
            end_time: 结束时间，格式：'YYYY-MM-DD HH:MM:SS'，如果未提供则默认为当前时间
        """
        logger.info("开始收集磁盘使用量数据")
        
        # 获取资源列表
        resources = self.get_resource_list()
        if not resources:
            logger.error("未获取到任何资源")
            return []
        
        # 获取磁盘相关指标
        indicators = self.get_metric_indicators()
        if not indicators:
            logger.error("未获取到磁盘相关指标")
            return []
        
        # 设置查询时间范围
        if not start_time or not end_time:
            # 如果没有传入时间，默认查询过去24小时的数据
            end_time_dt = datetime.now()
            start_time_dt = end_time_dt - timedelta(days=1)
            start_time_str = start_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            end_time_str = end_time_dt.strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"使用默认时间范围：{start_time_str} 到 {end_time_str}")
        else:
            start_time_str = start_time
            end_time_str = end_time
            logger.info(f"使用指定时间范围：{start_time_str} 到 {end_time_str}")
        
        all_disk_data = []
        
        for i, resource in enumerate(resources, 1):
            resource_id = resource.get('resourceId')
            resource_name = resource.get('resourceName')
            
            logger.info(f"正在处理资源 {i}/{len(resources)}: {resource_name} ({resource_id})")
            
            # 获取该资源的分区信息（使用第一个磁盘指标获取分区列表）
            first_metric = next(iter(self.disk_metrics.keys()))
            partitions = self.get_metric_nodes(resource_id, first_metric)
            
            if not partitions:
                logger.warning(f"资源 {resource_name} 未找到分区信息，将创建默认记录")
                # 即使没有分区信息，也要创建一条记录
                partition_data = {
                    'resourceName': resource_name,
                    'resourceId': resource_id,
                    'partition': 'N/A',
                    'disk_total': 0,
                    'disk_used': 0,
                    'disk_percent': 0
                }
                all_disk_data.append(partition_data)
                continue
            
            logger.info(f"资源 {resource_name} 找到 {len(partitions)} 个分区: {partitions}")
            
            # 为每个分区收集数据
            for partition in partitions:
                partition_data = {
                    'resourceName': resource_name,
                    'resourceId': resource_id,
                    'partition': partition,
                    'disk_total': 0,  # 默认值设为0
                    'disk_used': 0,   # 默认值设为0
                    'disk_percent': 0 # 默认值设为0
                }
                
                try:
                    # 构建查询指标
                    metrics_to_query = []
                    for metric_name in self.disk_metrics.keys():
                        metrics_to_query.append({
                            'metricName': metric_name,
                            'metricNodeName': partition
                        })
                    
                    # 获取性能数据
                    performance_data = self.get_performance_data(
                        resource_id, metrics_to_query, start_time_str, end_time_str
                    )
                    
                    # 解析性能数据
                    for perf_item in performance_data:
                        metric_name = perf_item.get('metricName')
                        avg_value = perf_item.get('avgValue')
                        
                        if avg_value is not None:
                            if metric_name == 'vm_realtime_disk_total':
                                partition_data['disk_total'] = round(avg_value, 2)
                            elif metric_name == 'vm_realtime_disk_used':
                                partition_data['disk_used'] = round(avg_value, 2)
                            elif metric_name == 'vm_realtime_disk_percent':
                                partition_data['disk_percent'] = round(avg_value, 2)
                    
                    # 如果获取到的性能数据为空，记录警告但保持默认值0
                    if not performance_data:
                        logger.warning(f"资源 {resource_name} 分区 {partition} 未获取到性能数据，使用默认值0")
                        
                except Exception as e:
                    logger.warning(f"获取资源 {resource_name} 分区 {partition} 性能数据时发生错误: {str(e)}，使用默认值0")
                
                all_disk_data.append(partition_data)
                time.sleep(0.1)  # 避免请求过快
        
        logger.info(f"数据收集完成，共收集到 {len(all_disk_data)} 条磁盘使用量记录")
        return all_disk_data
    
    def export_to_excel(self, data: List[Dict], output_file: str):
        """导出数据到Excel文件"""
        logger.info(f"正在导出数据到Excel文件: {output_file}")
        
        if not data:
            logger.warning("没有数据可导出")
            return
        
        # 创建DataFrame
        df_data = []
        for item in data:
            df_data.append({
                '资源名称': item['resourceName'],
                '资源ID': item['resourceId'],
                '分区': item['partition'],
                '磁盘容量大小(GB)': item['disk_total'] if item['disk_total'] is not None else 0,
                '已使用大小(GB)': item['disk_used'] if item['disk_used'] is not None else 0,
                '已使用百分比(%)': item['disk_percent'] if item['disk_percent'] is not None else 0
            })
        
        df = pd.DataFrame(df_data)
        
        # 导出到Excel
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='磁盘使用量报告', index=False)
                
                # 获取工作表并调整列宽
                worksheet = writer.sheets['磁盘使用量报告']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            logger.info(f"Excel文件导出成功: {output_file}")
            logger.info(f"共导出 {len(df_data)} 条记录")
            
        except Exception as e:
            logger.error(f"导出Excel文件时发生错误: {str(e)}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='磁盘使用量收集器')
    parser.add_argument('--pool-id', required=True, help='资源池ID')
    parser.add_argument('--product-type', default='vm', help='产品类型（默认: vm）')
    parser.add_argument('--output', default='disk_usage_report.xlsx', help='输出文件名（默认: disk_usage_report.xlsx）')
    parser.add_argument('--access-key', required=True, help='移动云Access Key ID (AK)')
    parser.add_argument('--secret-key', required=True, help='移动云Secret Access Key (SK)')
    parser.add_argument('--base-url', default='https://api-wuxi-1.cmecloud.cn:8443', 
                       help='API基础URL（默认: https://api-wuxi-1.cmecloud.cn:8443）')
    parser.add_argument('--config', help='配置文件路径（可选）')
    parser.add_argument('--start-time', help='开始时间，格式：YYYY-MM-DD HH:MM:SS（可选，默认为当前时间-1天）')
    parser.add_argument('--end-time', help='结束时间，格式：YYYY-MM-DD HH:MM:SS（可选，默认为当前时间）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式，显示详细日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("已启用调试模式")
    
    # 如果指定了配置文件，尝试从配置文件读取参数
    access_key = args.access_key
    secret_key = args.secret_key
    base_url = args.base_url
    
    if args.config:
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", args.config)
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            access_key = getattr(config, 'ACCESS_KEY', access_key)
            secret_key = getattr(config, 'SECRET_KEY', secret_key)
            base_url = getattr(config, 'BASE_URL', base_url)
            
            logger.info(f"已从配置文件加载参数: {args.config}")
        except Exception as e:
            logger.warning(f"无法加载配置文件 {args.config}: {str(e)}，使用命令行参数")
    
    # 验证必要参数
    if not access_key or not secret_key:
        logger.error("必须提供Access Key和Secret Key")
        parser.print_help()
        return
    
    # 创建收集器实例
    collector = DiskUsageCollector(
        pool_id=args.pool_id,
        product_type=args.product_type,
        base_url=base_url,
        access_key=access_key,
        secret_key=secret_key
    )
    
    try:
        logger.info(f"开始收集磁盘使用量数据...")
        logger.info(f"资源池ID: {args.pool_id}")
        logger.info(f"产品类型: {args.product_type}")
        logger.info(f"API地址: {base_url}")
        
        # 收集数据
        disk_data = collector.collect_disk_usage_data(
            start_time=args.start_time,
            end_time=args.end_time
        )
        
        if not disk_data:
            logger.warning("未收集到任何磁盘使用量数据")
            return
        
        # 导出到Excel
        collector.export_to_excel(disk_data, args.output)
        
        print(f"\n✅ 磁盘使用量报告已生成: {args.output}")
        print(f"📊 共收集到 {len(disk_data)} 条记录")
        
    except KeyboardInterrupt:
        logger.info("用户中断操作")
    except Exception as e:
        logger.error(f"程序执行时发生错误: {str(e)}")
        raise

if __name__ == '__main__':
    main()