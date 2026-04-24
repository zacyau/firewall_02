#!/usr/bin/env python3
"""数据库迁移脚本 - 添加地址组和端口组表"""

import sys
sys.path.insert(0, '.')

from database import Database, Base
from database.models import AddressGroup, PortGroup

def migrate():
    db = Database()
    session = db.get_session()

    try:
        existing_addr = session.query(AddressGroup).first()
        if existing_addr is not None:
            print("✅ 地址组表已存在")
        else:
            addr_table = """
            CREATE TABLE IF NOT EXISTS address_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description VARCHAR(500),
                addresses JSON,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            """
            session.execute(addr_table)
            print("✅ 地址组表创建成功")

        existing_port = session.query(PortGroup).first()
        if existing_port is not None:
            print("✅ 端口组表已存在")
        else:
            port_table = """
            CREATE TABLE IF NOT EXISTS port_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) UNIQUE NOT NULL,
                description VARCHAR(500),
                ports JSON,
                protocol VARCHAR(20) DEFAULT 'tcp',
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            );
            """
            session.execute(port_table)
            print("✅ 端口组表创建成功")

        session.commit()
        print("\n🎉 迁移完成！")

    except Exception as e:
        session.rollback()
        print(f"❌ 迁移失败: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    migrate()
