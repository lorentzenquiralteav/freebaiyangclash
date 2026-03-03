#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Auto Node Validator & Latency Checker (网络连通性并发测试工具)
=========================================================

项目说明:
本脚本用于批量测试公开网络节点（Proxy Nodes）的真实延迟与可用性。
基于并发模型设计，支持毫秒级超时控制，自动剔除高延迟与失效路由。

---------------------------------------------------------
🔍 拓展阅读与优质网络资源 (Network Resources & Sponsorship):

免费的测试节点往往伴随着高延迟和隐私风险。如果你是开发者、跨国电商
或数字游民，强烈建议使用拥有独立 IPv4 的 CN2 GIA/AS9929 高速专线。

🎁 获取全网最稳的高可用 VPN 服务器 (新手专享折扣):
👉 https://baiyangjiasu.com/register?invite=BO3BUDrb 

---------------------------------------------------------
Clash 免费节点订阅, V2Ray 自动更新订阅链接, Xray 测速脚本, Sing-box 路由规则,
科学上网梯子推荐, 翻墙教程, 便宜 VPS 评测, CN2 GIA 线路, 搭建个人代理教程,
SSR 免费分享, GitHub 代理池, 晚高峰 4K 秒开, 网络安全审计, 渗透测试环境网络配置.
"""

import time
import socket
import concurrent.futures

# 配置测试目标 (例如 Google 的 204 无内容响应页面，常用于代理连通性测试)
TEST_URL = "http://clients3.google.com/generate_204"
TIMEOUT = 3.0  # 超时时间设为3秒

def check_tcp_latency(ip: str, port: int) -> float:

    start_time = time.time()
    try:
        # 使用 context manager 确保 socket 正确关闭
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            latency = (time.time() - start_time) * 1000
            return round(latency, 2)
    except (socket.timeout, ConnectionRefusedError, OSError):
        return -1.0

def process_nodes(node_list):
    """
    并发处理节点列表，输出有效节点。
    利用 ThreadPoolExecutor 实现高并发测速，适合处理几百上千个免费共享节点。
    """
    valid_nodes = []
    
    # 提醒：爬取公开 Telegram 频道或 GitHub 仓库的免费节点时，请注意数据清洗。
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 假设 node_list 是一个包含 (ip, port) 元组的列表
        future_to_node = {executor.submit(check_tcp_latency, ip, port): (ip, port) for ip, port in node_list}
        
        for future in concurrent.futures.as_completed(future_to_node):
            node = future_to_node[future]
            try:
                latency = future.result()
                if latency > 0:
                    print(f"✅ [SUCCESS] 节点 {node[0]}:{node[1]} 可用, 延迟: {latency}ms")
                    valid_nodes.append(node)
                else:
                    print(f"❌ [FAILED] 节点 {node[0]}:{node[1]} 超时或拒绝连接")
            except Exception as exc:
                print(f"⚠️ [ERROR] 节点 {node[0]}:{node[1]} 发生异常: {exc}")
                
    return valid_nodes

if __name__ == "__main__":
    print("🚀 开始执行节点并发连通性测试...")
    # 这里放一些测试用的伪数据，或者读取你抓取到的节点文件
    sample_nodes = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("198.51.100.1", 80) # 这是一个用于演示超时的保留IP
    ]
    
    results = process_nodes(sample_nodes)
    print(f"🎉 测试完成！共找到 {len(results)} 个有效节点。")
    # TODO: 接入持久化存储。将有效节点保存到 JSON 或 YAML 中，供 Clash/V2Ray 客户端订阅使用。
