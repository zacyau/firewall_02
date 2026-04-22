import requests
import json

BASE_URL = "http://localhost:8080/api/v1"


def test_register_device():
    """测试设备注册"""
    print("=" * 60)
    print("测试1: 注册防火墙设备")
    print("=" * 60)

    device_data = {
        "name": "huawei_fw_01",
        "vendor": "huawei",
        "ip": "192.168.1.10",
        "port": 22,
        "username": "admin",
        "password": "admin123",
        "location": "数据中心A"
    }

    response = requests.post(f"{BASE_URL}/devices/register", json=device_data)
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_get_all_devices():
    """测试获取所有设备"""
    print("=" * 60)
    print("测试2: 获取所有设备")
    print("=" * 60)

    response = requests.get(f"{BASE_URL}/devices")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


def test_generate_policy():
    """测试生成策略"""
    print("=" * 60)
    print("测试3: 生成防火墙策略")
    print("=" * 60)

    policy_data = {
        "policy_name": "web_https_access",
        "source_ip": "10.0.1.100",
        "dest_ip": "10.0.2.200",
        "protocol": "tcp",
        "dest_port": "443"
    }

    response = requests.post(f"{BASE_URL}/policies/generate", json=policy_data)
    print(f"状态码: {response.status_code}")
    result = response.json()

    if result.get("status") == "success":
        data = result.get("data", {})
        print(f"策略名称: {data.get('policy_name')}")
        print(f"源IP: {data.get('source_ip')}")
        print(f"目的IP: {data.get('dest_ip')}")
        print(f"协议: {data.get('protocol')}")
        print(f"目的端口: {data.get('dest_port')}")
        print(f"防火墙数量: {data.get('firewall_count')}")
        print(f"防火墙路径: {data.get('path_description')}")
        print()

        print("生成的防火墙策略配置:")
        print("-" * 60)
        for idx, fw_policy in enumerate(data.get('firewall_policies', []), 1):
            print(f"\n[{idx}] 设备: {fw_policy['device_name']}")
            print(f"    源区域: {fw_policy['source_zone']} -> 目的区域: {fw_policy['dest_zone']}")
            print(f"    策略脚本:")
            print(fw_policy['policy_script'])

    print()


def test_get_health():
    """测试健康检查"""
    print("=" * 60)
    print("测试4: 健康检查")
    print("=" * 60)

    response = requests.get("http://localhost:8080/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("防火墙自动化运维平台 - API 测试")
    print("=" * 60)
    print()

    try:
        test_register_device()
        test_get_all_devices()
        test_generate_policy()
        test_get_health()

        print("=" * 60)
        print("所有测试完成！")
        print("=" * 60)
    except Exception as e:
        print(f"测试失败: {e}")
