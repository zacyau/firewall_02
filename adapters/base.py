from abc import ABC, abstractmethod
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import os


class FirewallAdapter(ABC):
    """防火墙适配器基类 - 统一接口"""

    def __init__(self, device_config: Dict[str, Any]):
        self.device_config = device_config
        self.name = device_config["name"]
        self.ip = device_config["ip"]
        self.port = device_config.get("port", 22)
        self.username = device_config.get("username")
        self.password = device_config.get("password")
        self.location = device_config.get("location", "Unknown")
        self._init_template_renderer()

    def _init_template_renderer(self):
        """初始化模板渲染器"""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染策略模板"""
        context["generation_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            template = self.env.get_template(template_name)
        except Exception:
            template = self.env.get_template("huawei_policy.j2")
        return template.render(**context)

    @abstractmethod
    def connect(self) -> bool:
        """连接到防火墙"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """断开连接"""
        pass

    @abstractmethod
    def check_heartbeat(self) -> Dict[str, Any]:
        """检查心跳"""
        pass

    @abstractmethod
    def create_security_policy(self, policy_config: Dict[str, Any]) -> str:
        """创建安全策略 - 返回生成的配置脚本"""
        pass

    @abstractmethod
    def apply_policy(self, policy_script: str) -> Dict[str, Any]:
        """应用策略到设备"""
        pass

    @abstractmethod
    def get_zone_by_ip(self, ip_address: str) -> str:
        """根据IP地址判断所属安全区域"""
        pass

    @abstractmethod
    def generate_cli_command(self, policy_config: Dict[str, Any]) -> str:
        """生成CLI命令"""
        pass
