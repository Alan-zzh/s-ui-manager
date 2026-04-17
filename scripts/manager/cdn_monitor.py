"""
CDN监控模块 - 从网站获取优选IP排名，自动分配给VLESS-WS和Trojan-WS
Author: Alan
Version: v5.0.0
运行方式：
  - 手动运行：python3 cdn_monitor.py
  - 后台服务：systemctl start s-ui-cdn-monitor
  - 定时任务：每天凌晨3点自动运行
"""
import requests
import json
import time
import sqlite3
import re
import os
import sys
import random
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class CDNMonitor:
    def __init__(self):
        # 服务器配置
        self.server_ip = os.getenv('SERVER_IP', 'YOUR_SERVER_IP')
        self.db_path = os.getenv('SERVER_DB_PATH', '/usr/local/s-ui/db/s-ui.db')
        self.cf_domain = os.getenv('CF_DOMAIN', 'YOUR_CF_DOMAIN')
        self.monitor_interval = int(os.getenv('CDN_MONITOR_INTERVAL', '86400'))  # 24小时
        
        # 优选IP配置
        self.cf_ip_url = "https://api.uouin.com/cloudflare.html"
        self.top_ips = []  # 存储前5个优选IP
        
    def fetch_cf_ip_list(self):
        """从网站获取优选IP列表（已按延迟排序）"""
        try:
            print(">>> 获取Cloudflare优选IP列表...")
            response = requests.get(self.cf_ip_url, timeout=30, verify=False)
            if response.status_code == 200:
                html = response.text
                # 提取所有IP（网站已经按延迟排序）
                ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', html)
                
                # 去重并取前5个
                unique_ips = list(dict.fromkeys(ips))  # 保持顺序去重
                self.top_ips = unique_ips[:5]
                
                print(f"  ✅ 获取到 {len(unique_ips)} 个优选IP")
                print(f"  📋 前5个最低延迟IP:")
                for i, ip in enumerate(self.top_ips, 1):
                    print(f"    {i}. {ip}")
                return True
            else:
                print(f"  ❌ 获取失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return False
    
    def assign_ips_to_protocols(self):
        """为VLESS-WS和Trojan-WS分配不同的优选IP"""
        if not self.top_ips:
            print("❌ 没有可用的优选IP")
            return False
        
        # 随机选择2个不同的IP
        if len(self.top_ips) >= 2:
            selected = random.sample(self.top_ips, 2)
            vless_ip = selected[0]
            trojan_ip = selected[1]
        else:
            # 如果只有1个IP，两个协议共用
            vless_ip = self.top_ips[0]
            trojan_ip = self.top_ips[0]
        
        print(f"\n>>> 分配优选IP:")
        print(f"  VLESS-WS: {vless_ip}")
        print(f"  Trojan-WS: {trojan_ip}")
        
        return vless_ip, trojan_ip
    
    def save_ips_to_db(self, vless_ip, trojan_ip):
        """将优选IP保存到数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建或更新CDN设置表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cdn_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # 保存VLESS-WS的优选IP
        cursor.execute("""
            INSERT OR REPLACE INTO cdn_settings (key, value) 
            VALUES (?, ?)
        """, ('vless_cdn_ip', vless_ip))
        
        # 保存Trojan-WS的优选IP
        cursor.execute("""
            INSERT OR REPLACE INTO cdn_settings (key, value) 
            VALUES (?, ?)
        """, ('trojan_cdn_ip', trojan_ip))
        
        # 保存更新时间
        cursor.execute("""
            INSERT OR REPLACE INTO cdn_settings (key, value) 
            VALUES (?, ?)
        """, ('last_update', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # 保存前5个IP列表（JSON格式）
        cursor.execute("""
            INSERT OR REPLACE INTO cdn_settings (key, value) 
            VALUES (?, ?)
        """, ('top5_ips', json.dumps(self.top_ips)))
        
        conn.commit()
        conn.close()
        print(f"\n  ✅ 已保存优选IP到数据库")
        return True
    
    def run_once(self):
        """运行一次CDN监控"""
        print("\n" + "=" * 50)
        print(f"CDN监控开始 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        
        if not self.fetch_cf_ip_list():
            return False
        
        vless_ip, trojan_ip = self.assign_ips_to_protocols()
        return self.save_ips_to_db(vless_ip, trojan_ip)
    
    def run_daemon(self):
        """后台守护进程模式"""
        print(f"CDN监控守护进程启动")
        print(f"监控间隔: {self.monitor_interval}秒 ({self.monitor_interval/3600:.1f}小时)")
        
        while True:
            try:
                self.run_once()
                print(f"\n>>> 等待 {self.monitor_interval}秒后下次检测...")
                time.sleep(self.monitor_interval)
            except KeyboardInterrupt:
                print("\n监控已停止")
                break
            except Exception as e:
                print(f"\n❌ 监控错误: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = CDNMonitor()
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        monitor.run_daemon()
    else:
        monitor.run_once()
