import paramiko
from typing import Dict, List, Any
from .base import FirewallAdapter


class HuaweiFirewallAdapter(FirewallAdapter):
    """华为防火墙适配器"""

    def __init__(self, device_config: Dict[str, Any]):
        super().__init__(device_config)
        self.client = None

    def connect(self) -> bool:
        """连接华为防火墙"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(
                self.ip,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=10
            )
            return True
        except Exception as e:
            print(f"连接华为防火墙 {self.name} 失败: {e}")
            return False

    def disconnect(self) -> bool:
        """断开华为防火墙连接"""
        if self.client:
            self.client.close()
            return True
        return False

    def check_heartbeat(self) -> Dict[str, Any]:
        """检查华为防火墙心跳"""
        if not self.connect():
            return {
                "status": "offline",
                "device_name": self.name,
                "message": "连接失败"
            }

        try:
            stdin, stdout, stderr = self.client.exec_command("display version")
            output = stdout.read().decode()

            stdin, stdout, stderr = self.client.exec_command("display device")
            device_info = stdout.read().decode()

            self.disconnect()

            return {
                "status": "online",
                "device_name": self.name,
                "vendor": "huawei",
                "ip": self.ip,
                "version_info": output[:200],
                "device_info": device_info[:200]
            }
        except Exception as e:
            self.disconnect()
            return {
                "status": "error",
                "device_name": self.name,
                "message": str(e)
            }

    def get_zone_by_ip(self, ip_address: str) -> str:
        """根据IP判断安全区域"""
        zone_mappings = self.device_config.get("zone_mappings", {})

        for zone, ip_ranges in zone_mappings.items():
            for ip_range in ip_ranges:
                if self._ip_in_range(ip_address, ip_range):
                    return zone
        return "untrust"

    def _ip_in_range(self, ip: str, cidr: str) -> bool:
        """检查IP是否在CIDR范围内"""
        import ipaddress
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(cidr, strict=False)
            return ip_obj in network
        except:
            return False

    def generate_cli_command(self, policy_config: Dict[str, Any]) -> str:
        """生成华为防火墙CLI命令"""
        return self._render_template("huawei_policy.j2", policy_config)

    def create_security_policy(self, policy_config: Dict[str, Any]) -> str:
        """创建安全策略"""
        return self.generate_cli_command(policy_config)

    def apply_policy(self, policy_script: str) -> Dict[str, Any]:
        """应用策略到华为防火墙"""
        if not self.connect():
            return {
                "status": "failed",
                "message": "连接失败"
            }

        try:
            commands = policy_script.strip().split('\n')
            for cmd in commands:
                if cmd.strip() and not cmd.strip().startswith('#'):
                    stdin, stdout, stderr = self.client.exec_command(cmd)
                    stderr_data = stderr.read().decode()
                    if stderr_data:
                        print(f"命令执行警告: {stderr_data}")

            self.disconnect()
            return {
                "status": "success",
                "device_name": self.name,
                "message": "策略应用成功"
            }
        except Exception as e:
            self.disconnect()
            return {
                "status": "failed",
                "device_name": self.name,
                "message": str(e)
            }
