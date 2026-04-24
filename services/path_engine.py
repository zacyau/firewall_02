import ipaddress
from typing import Dict, List, Any, Tuple, Optional, Set
from services.config_loader import config_loader


class PathCalculator:
    """防火墙路径计算引擎 - 支持智能路由查找"""

    def __init__(self):
        self.max_hops = 10  # 最大跳数，防止无限循环

    def _get_devices(self):
        """动态获取最新设备列表"""
        return config_loader.get_devices()

    def calculate_path(self, source_ip: str, dest_ip: str) -> List[Dict[str, Any]]:
        """智能路径计算 - 支持跨网段路由查找

        Args:
            source_ip: 源IP地址
            dest_ip: 目标IP地址

        Returns:
            防火墙路径列表，每项包含防火墙名称、源目Zone（每台防火墙独立的Zone命名）
        """
        # 1. 找到源IP所在的防火墙（根据直连网段判断）
        source_firewall = self._find_firewall_by_ip(source_ip)
        if not source_firewall:
            raise ValueError(f"无法找到源IP {source_ip} 所在的防火墙")

        # 2. 找到目的IP所在的防火墙
        dest_firewall = self._find_firewall_by_ip(dest_ip)
        if not dest_firewall:
            raise ValueError(f"无法找到目的IP {dest_ip} 所在的防火墙")

        # 3. 如果在同一台防火墙直连网段
        if source_firewall == dest_firewall:
            return [self._build_firewall_info(source_firewall, source_ip, dest_ip, 1, "直连")]

        # 4. 路由查找：从源防火墙到目的防火墙的路径
        firewall_path = self._route_lookup(source_firewall, dest_firewall, dest_ip)

        # 5. 构建路径信息
        result = []
        for idx, fw_name in enumerate(firewall_path):
            if idx == 0:
                direction = "入口"
            elif idx == len(firewall_path) - 1:
                direction = "出口"
            else:
                direction = "中转"

            result.append(self._build_firewall_info(fw_name, source_ip, dest_ip, idx + 1, direction))

        return result

    def _find_firewall_by_ip(self, ip_address: str) -> Optional[str]:
        """根据IP地址查找所在的防火墙

        通过直连网段判断IP属于哪台防火墙
        """
        for fw_name, fw_config in self._get_devices().items():
            connected_networks = fw_config.get("connected_networks", [])
            for conn in connected_networks:
                network = conn.get("network", "")
                if self._ip_in_network(ip_address, network):
                    return fw_name
        return None

    def _ip_in_network(self, ip: str, network: str) -> bool:
        """检查IP是否在网段内"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            net_obj = ipaddress.ip_network(network, strict=False)
            return ip_obj in net_obj
        except:
            return False

    def _route_lookup(self, source_fw: str, dest_fw: str, dest_ip: str) -> List[str]:
        """路由查找 - 从源防火墙递归查找目的防火墙"""
        visited = set()
        path = []

        def recursive_lookup(current_fw: str) -> bool:
            if current_fw in visited:
                return False
            if len(path) >= self.max_hops:
                return False

            visited.add(current_fw)
            path.append(current_fw)

            # 如果到达目的防火墙
            if current_fw == dest_fw:
                return True

            # 查找路由表，找到下一跳
            current_config = self._get_devices().get(current_fw, {})
            routing_table = current_config.get("routing_table", [])

            # 匹配目的网络的路由
            routes = []
            for route in routing_table:
                dest_network = route.get("destination", "")
                if self._ip_in_network(dest_ip, dest_network):
                    routes.append((dest_network, route.get("next_hop")))

            # 按网段精确度排序
            routes.sort(key=lambda x: self._get_network_prefix(x[0]), reverse=True)

            for _, next_fw in routes:
                if recursive_lookup(next_fw):
                    return True

            # 回溯
            path.pop()
            return False

        if recursive_lookup(source_fw):
            return path
        else:
            return [source_fw]

    def _get_network_prefix(self, network: str) -> int:
        """获取网段前缀长度"""
        try:
            return ipaddress.ip_network(network, strict=False).prefixlen
        except:
            return 0

    def _build_firewall_info(self, fw_name: str, source_ip: str, dest_ip: str, sequence: int, direction: str) -> Dict[str, Any]:
        """构建防火墙信息"""
        fw_config = self._get_devices().get(fw_name, {})
        connected_networks = fw_config.get("connected_networks", [])
        routing_table = fw_config.get("routing_table", [])

        source_zone = "unknown"
        dest_zone = "unknown"

        for conn in connected_networks:
            network = conn.get("network", "")
            if self._ip_in_network(source_ip, network):
                source_zone = conn.get("zone", "unknown")
            if self._ip_in_network(dest_ip, network):
                dest_zone = conn.get("zone", "unknown")

        if source_zone == "unknown":
            for route in routing_table:
                dest_network = route.get("destination", "")
                if self._ip_in_network(source_ip, dest_network):
                    source_zone = route.get("zone", "unknown")
                    break

        if dest_zone == "unknown":
            for route in routing_table:
                dest_network = route.get("destination", "")
                if self._ip_in_network(dest_ip, dest_network):
                    dest_zone = route.get("zone", "unknown")
                    break

        return {
            "device_name": fw_name,
            "vendor": fw_config.get("vendor", "unknown"),
            "ip": fw_config.get("ip", ""),
            "location": fw_config.get("location", ""),
            "source_zone": source_zone,
            "dest_zone": dest_zone,
            "sequence": sequence,
            "flow_direction": direction,
            "ip_path": {
                "source_ip": source_ip,
                "dest_ip": dest_ip
            }
        }

    def get_policy_config(self, source_ip: str, dest_ip: str, protocol: str, dest_port: str, policy_name: str) -> Dict[str, Any]:
        """获取完整的策略配置"""
        path = self.calculate_path(source_ip, dest_ip)

        policy_configs = []
        for fw in path:
            policy_configs.append({
                "device_name": fw["device_name"],
                "vendor": fw["vendor"],
                "ip": fw["ip"],
                "location": fw["location"],
                "source_zone": fw["source_zone"],
                "dest_zone": fw["dest_zone"],
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "protocol": protocol,
                "dest_port": dest_port,
                "policy_name": f"{policy_name}_{fw['device_name']}",
                "flow_direction": fw["flow_direction"],
                "sequence": fw["sequence"]
            })

        return {
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "protocol": protocol,
            "dest_port": dest_port,
            "policy_name": policy_name,
            "firewall_count": len(path),
            "firewall_policies": policy_configs,
            "path_description": " → ".join([fw["device_name"] for fw in path]),
            "path_summary": self._generate_path_summary(path)
        }

    def _generate_path_summary(self, path: List[Dict[str, Any]]) -> str:
        """生成路径摘要说明"""
        summary_parts = []
        for fw in path:
            summary_parts.append(
                f"{fw['device_name']} ({fw['source_zone']} → {fw['dest_zone']})"
            )
        return " | ".join(summary_parts)

    def calculate_paths_for_ip_pairs(self, ip_pairs: List[Tuple[str, str]]) -> List[List[Dict[str, Any]]]:
        """为一组IP对计算路径

        Args:
            ip_pairs: [(source_ip, dest_ip), ...]

        Returns:
            每对IP对应的防火墙路径列表
        """
        paths = []
        for source_ip, dest_ip in ip_pairs:
            try:
                path = self.calculate_path(source_ip, dest_ip)
                paths.append(path)
            except Exception as e:
                paths.append([])
        return paths

    def merge_paths_by_consistency(self, paths: List[List[Dict[str, Any]]], source_ips: List[str], dest_ips: List[str], source_dest_pairs: List[Tuple[str, str]] = None) -> List[Dict[str, Any]]:
        """路径合并优化 - 按路径一致性分组

        当地址组中所有IP组合计算出相同路径时，仅输出一套策略配置
        当地址组中不同IP组合产生不同路径时，需按路径分类输出多套策略

        Args:
            paths: 各IP对应的防火墙路径列表
            source_ips: 源IP列表
            dest_ips: 目的IP列表
            source_dest_pairs: 源目的IP对列表（如果提供，则使用此参数）

        Returns:
            合并后的策略组列表
        """
        path_groups = {}

        if source_dest_pairs is None:
            source_dest_pairs = [(src, dst) for src in source_ips for dst in dest_ips]

        for idx, path in enumerate(paths):
            if not path:
                continue

            if idx >= len(source_dest_pairs):
                continue

            src_ip, dst_ip = source_dest_pairs[idx]
            path_key = self._get_path_key(path)

            if path_key not in path_groups:
                path_groups[path_key] = {
                    "path": path,
                    "source_ips": [],
                    "dest_ips": [],
                    "source_dest_pairs": []
                }

            path_groups[path_key]["source_ips"].append(src_ip)
            path_groups[path_key]["dest_ips"].append(dst_ip)
            path_groups[path_key]["source_dest_pairs"].append((src_ip, dst_ip))

        merged_results = []
        for path_key, group_data in path_groups.items():
            path = group_data["path"]

            policy_configs = []
            for fw in path:
                policy_configs.append({
                    "device_name": fw["device_name"],
                    "vendor": fw["vendor"],
                    "ip": fw["ip"],
                    "location": fw["location"],
                    "source_zone": fw["source_zone"],
                    "dest_zone": fw["dest_zone"],
                    "source_ips": group_data["source_ips"],
                    "dest_ips": group_data["dest_ips"],
                    "policy_name": f"policy_{fw['device_name']}_{fw['sequence']}",
                    "flow_direction": fw["flow_direction"],
                    "sequence": fw["sequence"],
                    "source_dest_pairs": group_data["source_dest_pairs"]
                })

            merged_results.append({
                "path": path,
                "firewall_count": len(path),
                "source_ips": group_data["source_ips"],
                "dest_ips": group_data["dest_ips"],
                "source_dest_pairs": group_data["source_dest_pairs"],
                "firewall_policies": policy_configs,
                "path_description": " → ".join([fw["device_name"] for fw in path])
            })

        return merged_results

    def _get_path_key(self, path: List[Dict[str, Any]]) -> str:
        """生成路径唯一标识"""
        return "|".join([
            f"{fw['device_name']}:{fw['source_zone']}->{fw['dest_zone']}"
            for fw in path
        ])

    def expand_ip_ranges(self, addresses: List[str]) -> List[str]:
        """展开IP地址列表，支持单个IP和CIDR范围

        Args:
            addresses: IP地址列表，支持 "192.168.1.1" 或 "192.168.1.0/24"

        Returns:
            展开后的IP列表
        """
        expanded = []
        for addr in addresses:
            addr = addr.strip()
            if not addr:
                continue

            if "/" in addr:
                try:
                    network = ipaddress.ip_network(addr, strict=False)
                    expanded.extend([str(ip) for ip in network.hosts()])
                except:
                    expanded.append(addr)
            else:
                expanded.append(addr)

        return expanded
