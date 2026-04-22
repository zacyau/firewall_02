from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from typing import Dict, Any
import os


class TemplateRenderer:
    """模板渲染器"""

    def __init__(self, template_dir: str = "templates"):
        self.template_dir = template_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_policy(self, vendor: str, policy_config: Dict[str, Any]) -> str:
        """渲染策略模板

        Args:
            vendor: 厂商名称
            policy_config: 策略配置字典

        Returns:
            渲染后的配置脚本
        """
        template_name = f"{vendor}_policy.j2"

        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            template = self.env.get_template("huawei_policy.j2")

        policy_config["generation_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return template.render(**policy_config)

    def render_batch_policies(self, vendor: str, policies: list) -> Dict[str, str]:
        """批量渲染策略

        Args:
            vendor: 厂商名称
            policies: 策略配置列表

        Returns:
            策略名称到脚本的映射
        """
        results = {}
        for policy in policies:
            policy_name = policy.get("policy_name", "unnamed_policy")
            script = self.render_policy(vendor, policy)
            results[policy_name] = script
        return results
