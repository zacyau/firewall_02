import ipaddress
from typing import Dict, List, Any, Optional, Tuple
from database import Database, SecurityPolicy, FirewallDevice


class PolicyValidator:
    """策略验证器 - 冲突检测与冗余分析"""

    def __init__(self, db: Database):
        self.db = db

    def validate_rules(self, device_name: str, direction: str, rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证策略规则列表

        Args:
            device_name: 目标防火墙设备名称
            direction: 策略方向 inbound/outbound
            rules: 待验证的策略规则列表

        Returns:
            结构化验证报告
        """
        if direction not in ("inbound", "outbound"):
            return {
                "valid": False,
                "issues": [{
                    "rule_index": -1,
                    "type": "error",
                    "severity": "error",
                    "existing_rule_id": None,
                    "desc": f"无效的策略方向: {direction}，仅支持 inbound/outbound"
                }],
                "summary": "输入参数校验失败"
            }

        device = self._get_device(device_name)
        if not device:
            return {
                "valid": False,
                "issues": [{
                    "rule_index": -1,
                    "type": "error",
                    "severity": "error",
                    "existing_rule_id": None,
                    "desc": f"设备 {device_name} 不存在"
                }],
                "summary": "输入参数校验失败"
            }

        existing_rules = self._get_existing_rules(device_name, direction)

        issues = []
        for idx, rule in enumerate(rules):
            validation_error = self._validate_rule_format(rule, idx)
            if validation_error:
                issues.append(validation_error)
                continue

            conflict_issues = self._detect_conflicts(idx, rule, existing_rules)
            issues.extend(conflict_issues)

            redundancy_issues = self._detect_redundancies(idx, rule, existing_rules)
            issues.extend(redundancy_issues)

        conflict_count = sum(1 for i in issues if i["type"] == "conflict")
        redundancy_count = sum(1 for i in issues if i["type"] == "redundancy")
        error_count = sum(1 for i in issues if i["severity"] == "error")

        summary_parts = []
        if conflict_count > 0:
            summary_parts.append(f"{conflict_count} 个冲突")
        if redundancy_count > 0:
            summary_parts.append(f"{redundancy_count} 个冗余规则")
        if not summary_parts:
            summary_parts.append("无冲突或冗余")

        return {
            "valid": error_count == 0,
            "issues": issues,
            "summary": f"发现 {', '.join(summary_parts)}" if error_count > 0 or redundancy_count > 0 else "验证通过，无冲突或冗余"
        }

    def validate_generated_policies(self, generated_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证生成的策略数据

        Args:
            generated_data: generate_policy 返回的数据

        Returns:
            各设备的验证报告
        """
        firewall_policies = generated_data.get("firewall_policies", [])
        if not firewall_policies:
            return {
                "valid": True,
                "issues": [],
                "summary": "无策略需要验证",
                "device_reports": {}
            }

        device_reports = {}
        all_issues = []

        device_rules = {}
        for fw_policy in firewall_policies:
            device_name = fw_policy.get("device_name", "")
            if device_name not in device_rules:
                device_rules[device_name] = []
            device_rules[device_name].append(fw_policy)

        for device_name, rules in device_rules.items():
            direction = "inbound"
            normalized_rules = [self._normalize_policy(r) for r in rules]

            report = self.validate_rules(device_name, direction, normalized_rules)
            device_reports[device_name] = report
            all_issues.extend(report.get("issues", []))

        conflict_count = sum(1 for i in all_issues if i["type"] == "conflict")
        redundancy_count = sum(1 for i in all_issues if i["type"] == "redundancy")
        error_count = sum(1 for i in all_issues if i["severity"] == "error")

        summary_parts = []
        if conflict_count > 0:
            summary_parts.append(f"{conflict_count} 个冲突")
        if redundancy_count > 0:
            summary_parts.append(f"{redundancy_count} 个冗余规则")

        return {
            "valid": error_count == 0,
            "issues": all_issues,
            "summary": f"发现 {', '.join(summary_parts)}" if summary_parts else "验证通过，无冲突或冗余",
            "device_reports": device_reports
        }

    def _normalize_policy(self, fw_policy: Dict[str, Any]) -> Dict[str, Any]:
        """将生成的策略数据标准化为验证规则格式"""
        source_ip = fw_policy.get("source_ip", "any")
        dest_ip = fw_policy.get("dest_ip", "any")
        protocol = fw_policy.get("protocol", "tcp")
        dest_port = fw_policy.get("dest_port", "any")
        action = "permit"

        if isinstance(source_ip, list):
            source_ip = ",".join(source_ip) if source_ip else "any"
        if isinstance(dest_ip, list):
            dest_ip = ",".join(dest_ip) if dest_ip else "any"
        if isinstance(dest_port, list):
            dest_port = ",".join(str(p) for p in dest_port) if dest_port else "any"

        return {
            "source_ip": str(source_ip),
            "dest_ip": str(dest_ip),
            "protocol": str(protocol),
            "dest_port": str(dest_port),
            "action": action,
            "source_zone": fw_policy.get("source_zone", ""),
            "dest_zone": fw_policy.get("dest_zone", "")
        }

    def _validate_rule_format(self, rule: Dict[str, Any], idx: int) -> Optional[Dict[str, Any]]:
        """验证单条规则的格式"""
        required_fields = ["source_ip", "dest_ip", "protocol", "dest_port", "action"]
        for field in required_fields:
            if field not in rule or rule[field] is None:
                return {
                    "rule_index": idx,
                    "type": "error",
                    "severity": "error",
                    "existing_rule_id": None,
                    "desc": f"规则缺少必填字段: {field}"
                }

        action = rule["action"].lower()
        if action not in ("permit", "deny"):
            return {
                "rule_index": idx,
                "type": "error",
                "severity": "error",
                "existing_rule_id": None,
                "desc": f"无效的 action 值: {rule['action']}，仅支持 permit/deny"
            }

        return None

    def _detect_conflicts(self, rule_index: int, new_rule: Dict[str, Any], existing_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测冲突"""
        issues = []

        for existing in existing_rules:
            overlap_type = self._check_match_overlap(new_rule, existing)

            if overlap_type == "exact":
                if new_rule["action"].lower() != existing.get("action", "permit").lower():
                    issues.append({
                        "rule_index": rule_index,
                        "type": "conflict",
                        "severity": "error",
                        "existing_rule_id": existing.get("id"),
                        "desc": f"与已存在规则 '{self._format_rule(existing)}' 直接冲突（匹配条件完全重叠，动作相反）"
                    })

            elif overlap_type == "new_subset":
                if new_rule["action"].lower() != existing.get("action", "permit").lower():
                    issues.append({
                        "rule_index": rule_index,
                        "type": "conflict",
                        "severity": "error",
                        "existing_rule_id": existing.get("id"),
                        "desc": f"与已存在规则 '{self._format_rule(existing)}' 部分冲突（新规则匹配范围被已有规则包含，动作相反）"
                    })

            elif overlap_type == "existing_subset":
                if new_rule["action"].lower() != existing.get("action", "permit").lower():
                    issues.append({
                        "rule_index": rule_index,
                        "type": "conflict",
                        "severity": "error",
                        "existing_rule_id": existing.get("id"),
                        "desc": f"与已存在规则 '{self._format_rule(existing)}' 部分冲突（新规则匹配范围包含已有规则，动作相反）"
                    })

        return issues

    def _detect_redundancies(self, rule_index: int, new_rule: Dict[str, Any], existing_rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """检测冗余"""
        issues = []

        for existing in existing_rules:
            overlap_type = self._check_match_overlap(new_rule, existing)

            if overlap_type == "exact":
                if new_rule["action"].lower() == existing.get("action", "permit").lower():
                    issues.append({
                        "rule_index": rule_index,
                        "type": "redundancy",
                        "severity": "warning",
                        "existing_rule_id": existing.get("id"),
                        "desc": f"与已存在规则 '{self._format_rule(existing)}' 完全重复"
                    })

            elif overlap_type == "new_subset":
                if new_rule["action"].lower() == existing.get("action", "permit").lower():
                    issues.append({
                        "rule_index": rule_index,
                        "type": "redundancy",
                        "severity": "warning",
                        "existing_rule_id": existing.get("id"),
                        "desc": f"该规则已被规则 '{self._format_rule(existing)}' 完全覆盖，可以移除"
                    })

        return issues

    def _check_match_overlap(self, rule1: Dict[str, Any], rule2: Dict[str, Any]) -> str:
        """检查两条规则的匹配条件重叠关系

        Returns:
            "exact" - 完全重叠
            "new_subset" - 新规则匹配范围是已有规则的子集
            "existing_subset" - 已有规则匹配范围是新规则的子集
            "partial" - 部分重叠
            "none" - 无重叠
        """
        src_relation = self._compare_ip_ranges(rule1.get("source_ip", "any"), rule2.get("source_ip", "any"))
        dst_relation = self._compare_ip_ranges(rule1.get("dest_ip", "any"), rule2.get("dest_ip", "any"))
        port_relation = self._compare_port_ranges(rule1.get("dest_port", "any"), rule2.get("dest_port", "any"))
        proto_match = self._compare_protocol(rule1.get("protocol", "any"), rule2.get("protocol", "any"))

        if not proto_match:
            return "none"

        if src_relation == "none" or dst_relation == "none" or port_relation == "none":
            return "none"

        all_exact = src_relation == "equal" and dst_relation == "equal" and port_relation == "equal"
        if all_exact:
            return "exact"

        r1_is_subset = self._is_subset_relation(src_relation, dst_relation, port_relation, "subset")
        r1_is_superset = self._is_subset_relation(src_relation, dst_relation, port_relation, "superset")

        if r1_is_subset:
            return "new_subset"
        if r1_is_superset:
            return "existing_subset"

        return "partial"

    def _is_subset_relation(self, src_rel: str, dst_rel: str, port_rel: str, target: str) -> bool:
        """判断规则1是否是规则2的子集或超集

        规则1是规则2的子集：当所有维度上规则1要么等于规则2，要么是规则2的子集
        """
        subset_ok = {"equal", target}
        return src_rel in subset_ok and dst_rel in subset_ok and port_rel in subset_ok

    def _compare_ip_ranges(self, ip1: str, ip2: str) -> str:
        """比较两个IP范围的关系

        Returns:
            "equal" - 完全相同
            "subset" - ip1 是 ip2 的子集
            "superset" - ip1 是 ip2 的超集
            "partial" - 部分重叠
            "none" - 无重叠
        """
        if ip1 == ip2:
            return "equal"

        if ip1 == "any" and ip2 == "any":
            return "equal"
        if ip1 == "any":
            return "superset"
        if ip2 == "any":
            return "subset"

        nets1 = self._parse_ip_list(ip1)
        nets2 = self._parse_ip_list(ip2)

        if not nets1 or not nets2:
            return "none"

        all_in_2 = all(any(self._network_contains(n2, n1) for n2 in nets2) for n1 in nets1)
        all_in_1 = all(any(self._network_contains(n1, n2) for n1 in nets1) for n2 in nets2)

        if all_in_2 and all_in_1:
            return "equal"
        if all_in_2:
            return "subset"
        if all_in_1:
            return "superset"

        any_overlap = any(
            self._network_overlaps(n1, n2)
            for n1 in nets1
            for n2 in nets2
        )

        return "partial" if any_overlap else "none"

    def _parse_ip_list(self, ip_str: str) -> List[ipaddress._BaseNetwork]:
        """解析IP字符串为网络对象列表"""
        networks = []
        for part in ip_str.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                if "/" in part:
                    networks.append(ipaddress.ip_network(part, strict=False))
                else:
                    networks.append(ipaddress.ip_network(f"{part}/32", strict=False))
            except ValueError:
                try:
                    networks.append(ipaddress.ip_network(f"{part}/128", strict=False))
                except ValueError:
                    continue
        return networks

    def _network_contains(self, parent: ipaddress._BaseNetwork, child: ipaddress._BaseNetwork) -> bool:
        """判断 parent 网络是否包含 child 网络"""
        try:
            return child.subnet_of(parent)
        except TypeError:
            return parent == child

    def _network_overlaps(self, net1: ipaddress._BaseNetwork, net2: ipaddress._BaseNetwork) -> bool:
        """判断两个网络是否有重叠"""
        try:
            return net1.overlaps(net2)
        except TypeError:
            return net1 == net2

    def _compare_port_ranges(self, port1: str, port2: str) -> str:
        """比较两个端口范围的关系

        Returns:
            "equal" / "subset" / "superset" / "partial" / "none"
        """
        if port1 == port2:
            return "equal"

        if port1 == "any" and port2 == "any":
            return "equal"
        if port1 == "any":
            return "superset"
        if port2 == "any":
            return "subset"

        ranges1 = self._parse_port_list(port1)
        ranges2 = self._parse_port_list(port2)

        if not ranges1 or not ranges2:
            return "none"

        set1 = self._port_ranges_to_set(ranges1)
        set2 = self._port_ranges_to_set(ranges2)

        if set1 == set2:
            return "equal"
        if set1.issubset(set2):
            return "subset"
        if set1.issuperset(set2):
            return "superset"
        if set1 & set2:
            return "partial"
        return "none"

    def _parse_port_list(self, port_str: str) -> List[Tuple[int, int]]:
        """解析端口字符串为范围列表"""
        ranges = []
        for part in port_str.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                if "-" in part:
                    start, end = part.split("-", 1)
                    ranges.append((int(start.strip()), int(end.strip())))
                else:
                    p = int(part)
                    ranges.append((p, p))
            except (ValueError, AttributeError):
                continue
        return ranges

    def _port_ranges_to_set(self, ranges: List[Tuple[int, int]]) -> set:
        """将端口范围列表转换为端口集合"""
        ports = set()
        for start, end in ranges:
            for p in range(start, end + 1):
                ports.add(p)
        return ports

    def _compare_protocol(self, proto1: str, proto2: str) -> bool:
        """比较协议是否匹配"""
        p1 = proto1.lower() if proto1 else "any"
        p2 = proto2.lower() if proto2 else "any"

        if p1 == "any" or p2 == "any":
            return True
        return p1 == p2

    def _format_rule(self, rule: Dict[str, Any]) -> str:
        """格式化规则为可读字符串"""
        action = rule.get("action", "permit")
        protocol = rule.get("protocol", "any")
        source_ip = rule.get("source_ip", "any")
        dest_ip = rule.get("dest_ip", "any")
        dest_port = rule.get("dest_port", "any")

        if dest_port == "any":
            return f"{action} {protocol} {source_ip} -> {dest_ip}"
        return f"{action} {protocol} {source_ip} -> {dest_ip} eq {dest_port}"

    def _get_device(self, device_name: str) -> Optional[Any]:
        """获取设备"""
        session = self.db.get_session()
        try:
            return session.query(FirewallDevice).filter(
                FirewallDevice.name == device_name
            ).first()
        finally:
            session.close()

    def _get_existing_rules(self, device_name: str, direction: str) -> List[Dict[str, Any]]:
        """获取设备上已存在的策略规则"""
        session = self.db.get_session()
        try:
            policies = session.query(SecurityPolicy).filter(
                SecurityPolicy.device_name == device_name,
                SecurityPolicy.status.in_(["applied", "pending"])
            ).all()

            rules = []
            for p in policies:
                rule = p.to_dict()
                if "action" not in rule:
                    rule["action"] = "permit"
                rules.append(rule)
            return rules
        finally:
            session.close()
