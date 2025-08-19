#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动云API鉴权模块

该模块提供移动云API的鉴权功能，包括：
- URL编码
- 规范化查询字符串创建
- 待签名字符串创建
- 签名生成
- 公共参数添加
- 请求签名

使用方法:
from ecloud_auth import ECloudAuth

auth = ECloudAuth(access_key='your_ak', secret_key='your_sk')
signed_params = auth.sign_request('GET', '/api/path', {'param1': 'value1'})
"""

import hashlib
import hmac
import time
import uuid
from typing import Dict
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class ECloudAuth:
    """移动云API鉴权类"""
    
    def __init__(self, access_key: str, secret_key: str):
        """
        初始化鉴权实例
        
        Args:
            access_key: 移动云Access Key ID (AK)
            secret_key: 移动云Secret Access Key (SK)
        """
        self.access_key = access_key
        self.secret_key = secret_key
    
    def _url_encode(self, value: str) -> str:
        """按照移动云API要求进行URL编码"""
        # 对于字符 A-Z、a-z、0-9 以及字符"-"、"_"、"."、"~"不编码
        # 冒号":"需要编码为%3A（根据文档示例：2020-06-02T17%3A10%3A20Z）
        # 其他字符编码成 "%XY" 的格式
        # 英文空格要被编码是 %20，而不是加号（+）
        encoded = quote(str(value), safe='-_.~')
        return encoded
    
    def _create_canonical_query_string(self, params: Dict) -> str:
        """创建规范化请求字符串"""
        # 1. 参数排序：按照参数名称的字典顺序排序
        sorted_params = sorted(params.items())
        
        # 2. 参数编码和连接
        encoded_params = []
        for key, value in sorted_params:
            encoded_key = self._url_encode(key)
            encoded_value = self._url_encode(value)
            encoded_params.append(f"{encoded_key}={encoded_value}")
        
        # 3. 用&符号连接
        canonical_query_string = '&'.join(encoded_params)
        return canonical_query_string
    
    def _create_string_to_sign(self, http_method: str, servlet_path: str, canonical_query_string: str) -> str:
        """创建待签名字符串"""
        # 根据官方文档规范：HTTPMethod + \n + percentEncode(servletPath) + \n + shaEncode(CanonicalizedQueryString)
        
        # 1. HTTP方法
        method = http_method.upper()
        
        # 2. servlet路径进行URL编码
        encoded_path = self._url_encode(servlet_path)
        
        # 3. 对查询字符串进行SHA-256摘要
        sha_encoded_query = hashlib.sha256(canonical_query_string.encode('utf-8')).hexdigest()
        
        # 4. 按照官方规范拼接待签名字符串
        string_to_sign = f"{method}\n{encoded_path}\n{sha_encoded_query}"
        
        logger.debug(f"HTTP方法: {method}")
        logger.debug(f"编码后的路径: {encoded_path}")
        logger.debug(f"SHA-256摘要查询字符串: {sha_encoded_query}")
        logger.debug(f"最终待签名字符串: {string_to_sign}")
        
        return string_to_sign
    
    def _generate_signature(self, string_to_sign: str) -> str:
        """生成签名"""
        # 根据官方文档，签名密钥需要加上'BC_SIGNATURE&'前缀
        signing_key = f"BC_SIGNATURE&{self.secret_key}"
        logger.debug(f"签名密钥前缀: BC_SIGNATURE&{self.secret_key[:8]}...")
        
        # 使用HMAC-SHA1算法计算签名，直接返回十六进制字符串
        signature_hex = hmac.new(
            signing_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha1
        ).hexdigest()
        
        logger.debug(f"生成的签名(十六进制): {signature_hex}")
        return signature_hex
    
    def _add_common_params(self, params: Dict) -> Dict:
        """添加公共参数"""
        # 根据官方Python示例代码，使用本地时间而不是UTC时间
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
        logger.debug(f"生成的ISO时间戳: {timestamp}")
        
        # 生成随机数
        nonce = uuid.uuid4().hex
        
        # 添加公共参数
        common_params = {
            'AccessKey': self.access_key,
            'Timestamp': timestamp,
            'SignatureMethod': 'HmacSHA1',
            'SignatureVersion': 'V2.0',
            'SignatureNonce': nonce,
            'Version': '2016-12-05'  # 添加API版本参数
        }
        
        # 合并参数
        all_params = {**params, **common_params}
        logger.debug(f"完整请求参数列表: {list(all_params.keys())}")
        logger.debug(f"添加公共参数后的完整参数: {all_params}")
        return all_params
    
    def sign_request(self, http_method: str, servlet_path: str, params: Dict) -> Dict:
        """对请求进行签名
        
        Args:
            http_method: HTTP方法（GET、POST等）
            servlet_path: API路径
            params: 请求参数字典
            
        Returns:
            包含签名的完整参数字典
        """
        logger.debug(f"开始签名请求: {http_method} {servlet_path}")
        logger.debug(f"原始参数: {params}")
        
        # 1. 添加公共参数
        all_params = self._add_common_params(params)
        logger.debug(f"添加公共参数后: {all_params}")
        
        # 2. 创建规范化查询字符串
        canonical_query_string = self._create_canonical_query_string(all_params)
        logger.debug(f"规范化查询字符串: {canonical_query_string}")
        
        # 3. 创建待签名字符串
        string_to_sign = self._create_string_to_sign(http_method, servlet_path, canonical_query_string)
        logger.debug(f"待签名字符串: {string_to_sign}")
        
        # 4. 生成签名
        signature = self._generate_signature(string_to_sign)
        logger.debug(f"生成的签名: {signature}")
        
        # 5. 添加签名到参数中
        all_params['Signature'] = signature
        
        return all_params
    
    def create_canonical_query_string(self, params: Dict) -> str:
        """创建规范化查询字符串（公开方法）
        
        Args:
            params: 参数字典
            
        Returns:
            规范化的查询字符串
        """
        return self._create_canonical_query_string(params)