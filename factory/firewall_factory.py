from typing import Dict, Any
from adapters import (
    FirewallAdapter,
    HuaweiFirewallAdapter,
    HillstoneFirewallAdapter,
    H3CFirewallAdapter,
    JuniperFirewallAdapter
)


class FirewallFactory:
    """防火墙工厂类 - 使用工厂模式创建设备实例"""

    VENDOR_MAP = {
        "huawei": HuaweiFirewallAdapter,
        "hillstone": HillstoneFirewallAdapter,
        "h3c": H3CFirewallAdapter,
        "juniper": JuniperFirewallAdapter
    }

    @classmethod
    def create_firewall(cls, device_config: Dict[str, Any]) -> FirewallAdapter:
        """创建防火墙适配器实例"""
        vendor = device_config.get("vendor", "").lower()

        if vendor not in cls.VENDOR_MAP:
            raise ValueError(f"不支持的厂商: {vendor}，支持的厂商: {list(cls.VENDOR_MAP.keys())}")

        adapter_class = cls.VENDOR_MAP[vendor]
        return adapter_class(device_config)

    @classmethod
    def get_supported_vendors(cls) -> list:
        """获取支持的厂商列表"""
        return list(cls.VENDOR_MAP.keys())
