#!/usr/bin/env python3
"""
数据库迁移脚本：为 security_policies 表添加 error_message 字段
"""

import sqlite3
import os

def migrate():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'firewall_platform.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        print("新数据库将在首次运行时自动创建")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查字段是否已存在
    cursor.execute("PRAGMA table_info(security_policies)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'error_message' not in columns:
        print("添加 error_message 字段到 security_policies 表...")
        cursor.execute("ALTER TABLE security_policies ADD COLUMN error_message TEXT")
        conn.commit()
        print("迁移完成")
    else:
        print("error_message 字段已存在，跳过迁移")
    
    conn.close()

if __name__ == '__main__':
    migrate()
