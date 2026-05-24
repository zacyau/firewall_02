"""
防火墙路径计算引擎 - 基于安全区域的路径计算
通过配置文件定义防火墙区域拓扑，自动推导防火墙之间的访问路径
"""

import ipaddress
from typing import Dict, List, Any, Optional, Tuple


class PathCalculator:
    """防火墙路径计算引擎"""

    def __init__(self, devices_config: Dict):
        """
        初始化路径计算引擎
        
        Args:
            devices_config: 防火墙配置字典，包含所有防火墙的区域配置
        """
        self.devices = devices_config
        self.max_hops = 10                    # 最大跳数限制
        self.max_recursion_depth = 10         # 最大递归深度限制
        
        # 路径防火墙列表，存储计算过程中的中间结果
        self.npf_list = []
        
        # 引擎初始化时自动生成3张映射字典
        self.direct_network_map = self._build_direct_network_map()
        self.middle_forward_map = self._build_middle_forward_map()
        self.internet_forward_map = self._build_internet_forward_map()

    def _format_network_key(self, network: str) -> str:
        """
        格式化网段为查询key，保留掩码信息
        例如: "1.1.1.0/24" -> "n1.1.1.0/24", "172.25.0.0/16" -> "n172.25.0.0/16"
        """
        network = network.strip()
        return f"n{network}"

    def _parse_network(self, network: str) -> str:
        """
        解析网段，提取网络地址和掩码
        例如: "172.25.0.0/24" -> ("172.25.0.0", 24), "1.1.1.0" -> ("1.1.1.0", 32)
        """
        network = network.strip()
        if '/' in network:
            parts = network.rsplit('/', 1)
            addr = parts[0]
            mask = int(parts[1])
            return addr, mask
        else:
            return network, 32

    def _is_ip_in_network(self, ip: str, network: str) -> bool:
        """
        判断IP或网段是否在另一个网段范围内
        例如: "10.0.1.50" in "10.0.0.0/16" -> True
             "10.24.0.0/16" in "10.0.0.0/8" -> True (网段包含)
        """
        try:
            net = ipaddress.ip_network(network, strict=False)
            # 如果输入是CIDR网段格式，判断网段是否被包含
            if '/' in ip:
                try:
                    ip_net = ipaddress.ip_network(ip, strict=False)
                    return ip_net.subnet_of(net)
                except:
                    return False
            # 否则当作单个IP处理
            ip_addr = ipaddress.ip_address(ip)
            return ip_addr in net
        except:
            return False

    def _networks_match(self, net1: str, net2: str) -> bool:
        """
        判断两个网段是否匹配（相交）
        使用ipaddress模块进行网段包含判断
        """
        try:
            network1 = ipaddress.ip_network(net1, strict=False)
            network2 = ipaddress.ip_network(net2, strict=False)
            # 检查两个网段是否有交集
            return network1.overlaps(network2)
        except:
            # fallback: 比较解析后的网络地址
            n1, _ = self._parse_network(net1)
            n2, _ = self._parse_network(net2)
            return n1 == n2

    def _build_direct_network_map(self) -> Dict[str, Dict[str, str]]:
        """
        构建直连网段关联映射字典
        用于快速查询直连网段 -> (防火墙名称, 区域名称)
        
        收集范围:
        - edge 区域的网段列表
        - forward-in 区域的 net 属性（排除 0.0.0.0）
        - forward-out 区域的 net 属性
        - mixed 区域的 net 属性
        """
        direct_map = {}
        
        for fw_name, fw_config in self.devices.items():
            zones = fw_config.get('zones', {})
            
            # 1. 处理 edge 类型区域
            edge_zones = zones.get('edge', {})
            for zone_name, networks in edge_zones.items():
                for net in networks:
                    key = self._format_network_key(net)
                    direct_map[key] = {
                        'firewall': fw_name,
                        'zone': zone_name
                    }
            
            # 2. 处理 forward-in 类型区域
            forward_in_zones = zones.get('forward-in', {})
            for zone_name, zone_config in forward_in_zones.items():
                nets = zone_config.get('net', [])
                for net in nets:
                    # 排除 0.0.0.0（默认区域）
                    if net != '0.0.0.0':
                        key = self._format_network_key(net)
                        direct_map[key] = {
                            'firewall': fw_name,
                            'zone': zone_name
                        }
            
            # 3. 处理 forward-out 类型区域
            forward_out_zones = zones.get('forward-out', {})
            for zone_name, zone_config in forward_out_zones.items():
                nets = zone_config.get('net', [])
                for net in nets:
                    key = self._format_network_key(net)
                    direct_map[key] = {
                        'firewall': fw_name,
                        'zone': zone_name
                    }
            
            # 4. 处理 mixed 类型区域
            mixed_zones = zones.get('mixed', {})
            for zone_name, zone_config in mixed_zones.items():
                nets = zone_config.get('net', [])
                for net in nets:
                    key = self._format_network_key(net)
                    direct_map[key] = {
                        'firewall': fw_name,
                        'zone': zone_name
                    }
        
        return direct_map

    def _build_middle_forward_map(self) -> Dict[str, Dict[str, List[str]]]:
        """
        构建中转防火墙区域映射字典
        用于快速查询中转防火墙及其区域与远端防火墙的关联关系
        
        筛选条件（满足任一则为中转墙）:
        - 有 2 个及以上 forward-in 区域
        - 有 mixed 区域
        - 同时有 forward-in 和 mixed 区域
        """
        middle_map = {}
        
        for fw_name, fw_config in self.devices.items():
            zones = fw_config.get('zones', {})
            
            forward_in_zones = zones.get('forward-in', {})
            mixed_zones = zones.get('mixed', {})
            
            # 判断是否为中转墙
            is_middle = False
            zone_info = {}
            
            # 检查 forward-in 区域
            for zone_name, zone_config in forward_in_zones.items():
                dev_list = zone_config.get('dev', [])
                if dev_list:
                    is_middle = True
                    zone_info[zone_name] = dev_list
            
            # 检查 mixed 区域
            for zone_name, zone_config in mixed_zones.items():
                dev_list = zone_config.get('dev', [])
                if dev_list:
                    is_middle = True
                    zone_info[zone_name] = dev_list
            
            if is_middle and zone_info:
                middle_map[fw_name] = zone_info
        
        return middle_map

    def _build_internet_forward_map(self) -> Dict[str, Dict[str, Any]]:
        """
        构建互联网防火墙区域映射字典
        用于快速查询内部网段经由哪台互联网防火墙转发
        
        对每个 forward-out 区域的 allow 网段:
        - 查找同防火墙中哪个 forward-in 区域的 net 包含该网段
        - in 方向: src_zone = forward-out区域, dst_zone = trust区域
        - out 方向: src_zone = trust区域, dst_zone = forward-out区域
        """
        internet_map = {}
        
        for fw_name, fw_config in self.devices.items():
            zones = fw_config.get('zones', {})
            forward_out_zones = zones.get('forward-out', {})
            forward_in_zones = zones.get('forward-in', {})
            
            for out_zone_name, out_config in forward_out_zones.items():
                allow_nets = out_config.get('allow', [])
                
                for net in allow_nets:
                    # 查找 trust_zone（forward-in 区域中 net 包含该网段的）
                    trust_zone = None
                    for in_zone_name, in_config in forward_in_zones.items():
                        in_nets = in_config.get('net', [])
                        for in_net in in_nets:
                            if self._networks_match(net, in_net):
                                trust_zone = in_zone_name
                                break
                        if trust_zone:
                            break
                    
                    if trust_zone:
                        key = self._format_network_key(net)
                        internet_map[key] = {
                            'firewall': fw_name,
                            'in': {
                                'src_zone': out_zone_name,  # 互联网方向进来的源区域是 forward-out 区域
                                'dst_zone': trust_zone       # 目标是信任区域
                            },
                            'out': {
                                'src_zone': trust_zone,      # 信任区域发起
                                'dst_zone': out_zone_name    # 出口是 forward-out 区域
                            }
                        }
        
        return internet_map

    def _find_network_in_direct_map(self, ip_or_network: str) -> Optional[Dict[str, str]]:
        """
        在 direct_network_map 中查找 IP 或网段对应的防火墙和区域
        支持精确匹配和IP在网段中匹配
        优先匹配更精确的网段（掩码位数越长越精确）
        """
        # 1. 尝试直接精确匹配
        key = self._format_network_key(ip_or_network)
        if key in self.direct_network_map:
            return self.direct_network_map[key]

        # 2. 如果没有精确匹配，查找所有匹配的网段，优先返回最精确的
        matches = []
        for net_key, info in self.direct_network_map.items():
            if net_key.startswith('n'):
                network = net_key[1:]  # 去掉前缀 'n'
                if self._is_ip_in_network(ip_or_network, network):
                    # 获取掩码位数作为精确度指标
                    if '/' in network:
                        mask_len = int(network.split('/')[1])
                    else:
                        mask_len = 32  # 精确IP视为 /32
                    matches.append((mask_len, info))

        if matches:
            # 按掩码长度降序排序（长度越大越精确），返回最精确的匹配
            matches.sort(key=lambda x: x[0], reverse=True)
            return matches[0][1]

        return None

    def _get_forward_in_zones(self, fw_name: str) -> Dict[str, Dict]:
        """获取防火墙的所有 forward-in 区域"""
        fw_config = self.devices.get(fw_name, {})
        return fw_config.get('zones', {}).get('forward-in', {})

    def _get_mixed_zones(self, fw_name: str) -> Dict[str, Dict]:
        """获取防火墙的所有 mixed 区域"""
        fw_config = self.devices.get(fw_name, {})
        return fw_config.get('zones', {}).get('mixed', {})

    def _is_default_zone(self, fw_name: str, zone_name: str) -> bool:
        """判断是否是默认区域（net=['0.0.0.0'] 的 forward-in 区域）"""
        fw_config = self.devices.get(fw_name, {})
        zones = fw_config.get('zones', {})
        forward_in = zones.get('forward-in', {})
        
        zone_config = forward_in.get(zone_name, {})
        nets = zone_config.get('net', [])
        
        # 只有一个 forward-in 区域且 net=['0.0.0.0']
        return nets == ['0.0.0.0'] and len(forward_in) == 1

    def _complete_dst_zone(self, src_fw: str, dst_fw: str, depth: int = 0) -> Optional[str]:
        """
        补全源防火墙的 dst_zone
        
        逻辑:
        1. 如果只有1个 forward-in 区域，直接返回该区域名
        2. 如果有多个 forward-in 区域，检查 dev 是否包含 dst_fw
        3. 如果没有直接匹配，递归查找
        """
        if depth >= self.max_recursion_depth:
            return None
        
        forward_in_zones = self._get_forward_in_zones(src_fw)
        
        # 如果只有1个 forward-in 区域，返回该区域
        if len(forward_in_zones) == 1:
            return list(forward_in_zones.keys())[0]
        
        # 检查是否有区域直接关联 dst_fw
        for zone_name, zone_config in forward_in_zones.items():
            dev_list = zone_config.get('dev', [])
            if dst_fw in dev_list:
                return zone_name
        
        # 递归查找
        for zone_name, zone_config in forward_in_zones.items():
            dev_list = zone_config.get('dev', [])
            for dev_fw in dev_list:
                # 检查 dev_fw 是否能到达 dst_fw
                result = self._find_path_between_firewalls(dev_fw, dst_fw, depth + 1)
                if result:
                    return zone_name
        
        return None

    def _complete_src_zone(self, src_fw: str, dst_fw: str, depth: int = 0) -> Optional[str]:
        """
        补全目标防火墙的 src_zone
        逻辑同 _complete_dst_zone，从目标防火墙向源防火墙反向查找
        """
        if depth >= self.max_recursion_depth:
            return None
        
        forward_in_zones = self._get_forward_in_zones(dst_fw)
        mixed_zones = self._get_mixed_zones(dst_fw)
        
        all_zones = {**forward_in_zones, **mixed_zones}
        
        # 如果只有1个 forward-in 区域且是默认区域
        if len(forward_in_zones) == 1:
            zone_name = list(forward_in_zones.keys())[0]
            if self._is_default_zone(dst_fw, zone_name):
                return zone_name
        
        # 检查是否有区域直接关联 src_fw
        for zone_name, zone_config in all_zones.items():
            dev_list = zone_config.get('dev', [])
            if src_fw in dev_list:
                return zone_name
        
        # 递归查找
        for zone_name, zone_config in all_zones.items():
            dev_list = zone_config.get('dev', [])
            for dev_fw in dev_list:
                result = self._find_path_between_firewalls(src_fw, dev_fw, depth + 1)
                if result:
                    return zone_name
        
        return None

    def _find_path_between_firewalls(self, fw1: str, fw2: str, depth: int = 0) -> bool:
        """
        查找两个防火墙之间是否存在路径
        使用 middle_forward_map 进行查找
        """
        if depth >= self.max_recursion_depth:
            return False
        
        if fw1 == fw2:
            return True
        
        # 在 middle_forward_map 中查找
        for fw_name, zone_info in self.middle_forward_map.items():
            for zone_name, dev_list in zone_info.items():
                if fw2 in dev_list:
                    # 找到了一个连接，继续递归查找
                    if fw_name == fw1:
                        return True
                    # 需要进一步检查 fw1 到 fw_name 的路径
                    if self._find_path_between_firewalls(fw1, fw_name, depth + 1):
                        return True
        
        return False

    def _find_middle_firewalls(self, src_fw: str, dst_fw: str) -> List[Dict[str, str]]:
        """
        查找中间防火墙
        在 middle_forward_map 中查找同时连接 src_fw 和 dst_fw 的防火墙
        """
        middle_list = []
        visited = set()
        
        for fw_name, zone_info in self.middle_forward_map.items():
            if fw_name in (src_fw, dst_fw):
                continue
            
            src_zone = None
            dst_zone = None
            
            for zone_name, dev_list in zone_info.items():
                if src_fw in dev_list:
                    src_zone = zone_name
                if dst_fw in dev_list:
                    dst_zone = zone_name
            
            if src_zone and dst_zone and src_zone != dst_zone:
                if fw_name not in visited:
                    visited.add(fw_name)
                    middle_list.append({
                        'firewall': fw_name,
                        'src_zone': src_zone,
                        'dst_zone': dst_zone
                    })
        
        return middle_list

    def calculate_path(self, src_net: str, dst_net: str) -> List[Dict[str, str]]:
        """
        根据源网络和目标网络计算防火墙路径
        
        Args:
            src_net: 源网络（如 "1.1.1.0"）
            dst_net: 目标网络（如 "172.25.0.0"）
        
        Returns:
            npf_list: 路径防火墙列表，每条记录包含 firewall/src_zone/dst_zone
        """
        # 重置 npf_list
        self.npf_list = []
        
        # Step 1: 查询 direct_network_map 获取源防火墙和目标防火墙（支持IP在网段中匹配）
        src_info = self._find_network_in_direct_map(src_net)
        dst_info = self._find_network_in_direct_map(dst_net)
        
        if not src_info:
            raise ValueError(f"无法找到源网络 {src_net} 所在的防火墙")
        if not dst_info:
            raise ValueError(f"无法找到目标网络 {dst_net} 所在的防火墙")
        
        src_fw = src_info['firewall']
        src_zone = src_info['zone']
        dst_fw = dst_info['firewall']
        dst_zone = dst_info['zone']
        
        # Step 3: 初始化 npf_list
        fw1 = {'firewall': src_fw, 'src_zone': src_zone, 'dst_zone': ''}
        fw2 = {'firewall': dst_fw, 'src_zone': '', 'dst_zone': dst_zone}
        
        self.npf_list = [fw1, fw2]
        
        # Step 4: 判断是同墙访问还是跨墙访问
        if src_fw == dst_fw:
            # 同墙不同区域访问，合并为一条记录
            self.npf_list = [{'firewall': src_fw, 'src_zone': src_zone, 'dst_zone': dst_zone}]
            return self.npf_list
        
        # Step 5: 跨墙访问，补全缺失的 Zone
        # 补全源防火墙的 dst_zone
        for item in self.npf_list:
            if item['firewall'] == src_fw and not item['dst_zone']:
                item['dst_zone'] = self._complete_dst_zone(src_fw, dst_fw) or ''
        
        # 补全目标防火墙的 src_zone
        for item in self.npf_list:
            if item['firewall'] == dst_fw and not item['src_zone']:
                item['src_zone'] = self._complete_src_zone(src_fw, dst_fw) or ''
        
        # Step 6: 查找中间防火墙
        middle_firewalls = self._find_middle_firewalls(src_fw, dst_fw)
        
        # 将中间防火墙插入到 npf_list 中（按路径顺序）
        if middle_firewalls:
            # 简单插入到源防火墙和目标防火墙之间
            result = [self.npf_list[0]]  # 源防火墙
            result.extend(middle_firewalls)  # 中间防火墙
            result.append(self.npf_list[1])  # 目标防火墙
            self.npf_list = result
        
        return self.npf_list

    # ==================== 以下为保留的辅助方法，保持接口兼容 ====================

    def get_policy_config(self, source_ip: str, dest_ip: str, protocol: str, dest_port: str, policy_name: str) -> Dict[str, Any]:
        """获取完整的策略配置（兼容旧接口）"""
        path = self.calculate_path(source_ip, dest_ip)

        policy_configs = []
        for idx, fw in enumerate(path):
            direction = "入口" if idx == 0 else ("出口" if idx == len(path) - 1 else "中转")
            fw_config = self.devices.get(fw['firewall'], {})
            policy_configs.append({
                "device_name": fw['firewall'],
                "vendor": fw_config.get('vendor', 'huawei'),
                "source_zone": fw['src_zone'],
                "dest_zone": fw['dst_zone'],
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "protocol": protocol,
                "dest_port": dest_port,
                "policy_name": f"{policy_name}_{fw['firewall']}",
                "flow_direction": direction,
                "sequence": idx + 1
            })
        
        return {
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "protocol": protocol,
            "dest_port": dest_port,
            "policy_name": policy_name,
            "firewall_count": len(path),
            "firewall_policies": policy_configs,
            "path_description": " -> ".join([fw["firewall"] for fw in path]),
            "path_summary": " | ".join([f"{fw['firewall']} ({fw['src_zone']} -> {fw['dst_zone']})" for fw in path])
        }

    def expand_ip_ranges(self, ip_list: List[str]) -> List[str]:
        """
        展开IP列表中的网段为具体IP或保留网段格式
        例如: ["192.168.1.0/30", "10.0.0.1"] -> ["192.168.1.0/30", "10.0.0.1"]
        对于 /30, /31, /32 这样的小网段直接保留，对于 /24 及更大的网段保留原格式
        实际使用时配合 calculate_paths_for_ip_pairs 进行路径计算
        """
        if not ip_list:
            return []

        result = []
        for ip in ip_list:
            if '/' in ip:
                # 提取掩码长度
                mask_len = int(ip.split('/')[1]) if '/' in ip else 32
                # 对于 /24 及更大的网段（更多可用IP），保留原格式避免过大列表
                # 对于 /25, /26, /27, /28, /29, /30, /31, /32，保留原格式
                # 只有 /8, /16 这样的大网段才展开
                if mask_len <= 24:
                    # 展开大网段为具体IP（但限制数量避免内存爆炸）
                    try:
                        net = ipaddress.ip_network(ip, strict=False)
                        # 对于超大网段只取前256个IP
                        if net.num_addresses > 256:
                            # 只保留网段格式，让 calculate_paths_for_ip_pairs 内部处理匹配
                            result.append(ip)
                        else:
                            result.append(ip)
                    except:
                        result.append(ip)
                else:
                    result.append(ip)
            else:
                result.append(ip)

        return result if result else ip_list

    def calculate_paths_for_ip_pairs(self, ip_pairs: List[Tuple[str, str]]) -> List[List[Dict[str, str]]]:
        """
        为多个IP对计算防火墙路径

        Args:
            ip_pairs: IP对列表，每对为 (源IP, 目标IP)

        Returns:
            路径列表，每个元素是一个防火墙路径列表
        """
        paths = []
        for src_ip, dst_ip in ip_pairs:
            try:
                path = self.calculate_path(src_ip, dst_ip)
                paths.append(path)
            except ValueError:
                # 如果找不到路径，跳过这个IP对
                continue
        return paths

    def merge_paths_by_consistency(self, paths: List[List[Dict]], source_ips: List[str], dest_ips: List[str], source_dest_pairs: List[Tuple[str, str]] = None) -> List[Dict[str, Any]]:
        """路径合并优化 - 按路径一致性分组（兼容旧接口）"""
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
            for idx, fw in enumerate(path):
                direction = "入口" if idx == 0 else ("出口" if idx == len(path) - 1 else "中转")
                fw_config = self.devices.get(fw['firewall'], {})
                policy_configs.append({
                    "device_name": fw['firewall'],
                    "vendor": fw_config.get('vendor', 'huawei'),
                    "source_zone": fw['src_zone'],
                    "dest_zone": fw['dst_zone'],
                    "source_ips": group_data["source_ips"],
                    "dest_ips": group_data["dest_ips"],
                    "policy_name": f"policy_{fw['firewall']}_{idx + 1}",
                    "flow_direction": direction,
                    "sequence": idx + 1,
                    "source_dest_pairs": group_data["source_dest_pairs"]
                })
            
            merged_results.append({
                "path": path,
                "firewall_count": len(path),
                "source_ips": group_data["source_ips"],
                "dest_ips": group_data["dest_ips"],
                "source_dest_pairs": group_data["source_dest_pairs"],
                "firewall_policies": policy_configs,
                "path_description": " -> ".join([fw["firewall"] for fw in path]),
                "path_summary": " | ".join([f"{fw['firewall']} ({fw['src_zone']} -> {fw['dst_zone']})" for fw in path])
            })
        
        return merged_results

    def _get_path_key(self, path: List[Dict]) -> str:
        """生成路径唯一标识（兼容旧接口）"""
        return "|".join([f"{fw['firewall']}:{fw['src_zone']}->{fw['dst_zone']}" for fw in path])
