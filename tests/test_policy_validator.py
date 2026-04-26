import pytest
import sys
import os
import ipaddress

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.policy_validator import PolicyValidator
from database import Database, SecurityPolicy, FirewallDevice


@pytest.fixture
def db():
    database = Database(db_url='sqlite:///:memory:')
    database.create_tables()
    return database


@pytest.fixture
def validator(db):
    return PolicyValidator(db)


@pytest.fixture
def sample_device(db):
    session = db.get_session()
    device = FirewallDevice(
        name="FW-01",
        vendor="huawei",
        ip="10.0.0.1",
        port=22,
        username="admin",
        password="admin",
        status="online"
    )
    session.add(device)
    session.commit()
    session.close()
    return device


def _add_existing_policy(db, device_name="FW-01", source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                         protocol="tcp", dest_port="80", action="permit", status="applied"):
    session = db.get_session()
    policy = SecurityPolicy(
        policy_name=f"test_policy_{source_ip}_{dest_port}",
        source_ip=source_ip,
        dest_ip=dest_ip,
        protocol=protocol,
        dest_port=dest_port,
        action=action,
        device_name=device_name,
        status=status
    )
    session.add(policy)
    session.commit()
    policy_id = policy.id
    session.close()
    return policy_id


class TestIPComparison:
    def test_equal_ips(self, validator):
        assert validator._compare_ip_ranges("10.0.0.1", "10.0.0.1") == "equal"

    def test_any_superset(self, validator):
        assert validator._compare_ip_ranges("any", "10.0.0.1") == "superset"

    def test_specific_subset_of_any(self, validator):
        assert validator._compare_ip_ranges("10.0.0.1", "any") == "subset"

    def test_cidr_contains_host(self, validator):
        assert validator._compare_ip_ranges("10.0.0.1", "10.0.0.0/24") == "subset"

    def test_host_in_cidr(self, validator):
        assert validator._compare_ip_ranges("10.0.0.0/24", "10.0.0.1") == "superset"

    def test_different_networks_no_overlap(self, validator):
        assert validator._compare_ip_ranges("10.0.0.0/24", "192.168.1.0/24") == "none"

    def test_overlapping_cidrs(self, validator):
        result = validator._compare_ip_ranges("10.0.0.0/23", "10.0.0.0/24")
        assert result == "superset"

    def test_equal_cidrs(self, validator):
        assert validator._compare_ip_ranges("10.0.0.0/24", "10.0.0.0/24") == "equal"

    def test_comma_separated_subset(self, validator):
        result = validator._compare_ip_ranges("10.0.0.1,10.0.0.2", "10.0.0.0/24")
        assert result == "subset"


class TestPortComparison:
    def test_equal_ports(self, validator):
        assert validator._compare_port_ranges("80", "80") == "equal"

    def test_any_superset(self, validator):
        assert validator._compare_port_ranges("any", "80") == "superset"

    def test_specific_subset_of_any(self, validator):
        assert validator._compare_port_ranges("80", "any") == "subset"

    def test_range_contains_single(self, validator):
        assert validator._compare_port_ranges("80", "80-90") == "subset"

    def test_single_in_range(self, validator):
        assert validator._compare_port_ranges("80-90", "80") == "superset"

    def test_different_ports_no_overlap(self, validator):
        assert validator._compare_port_ranges("80", "443") == "none"

    def test_overlapping_ranges(self, validator):
        result = validator._compare_port_ranges("80-90", "85-95")
        assert result == "partial"

    def test_equal_ranges(self, validator):
        assert validator._compare_port_ranges("80-90", "80-90") == "equal"

    def test_comma_separated_subset(self, validator):
        result = validator._compare_port_ranges("80,443", "80,443,8080")
        assert result == "subset"


class TestProtocolComparison:
    def test_same_protocol(self, validator):
        assert validator._compare_protocol("tcp", "tcp") is True

    def test_different_protocol(self, validator):
        assert validator._compare_protocol("tcp", "udp") is False

    def test_any_matches_all(self, validator):
        assert validator._compare_protocol("any", "tcp") is True
        assert validator._compare_protocol("tcp", "any") is True


class TestConflictDetection:
    def test_direct_conflict(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="permit")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "deny"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert report["valid"] is False
        assert any(i["type"] == "conflict" for i in report["issues"])

    def test_no_conflict_same_action(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="permit")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        conflict_issues = [i for i in report["issues"] if i["type"] == "conflict"]
        assert len(conflict_issues) == 0

    def test_partial_conflict_new_subset(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="any", action="deny")

        new_rule = {
            "source_ip": "10.0.0.1",
            "dest_ip": "192.168.1.1",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert any(i["type"] == "conflict" for i in report["issues"])

    def test_no_conflict_different_protocol(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="deny")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "udp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        conflict_issues = [i for i in report["issues"] if i["type"] == "conflict"]
        assert len(conflict_issues) == 0

    def test_no_conflict_different_port(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="deny")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "443",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        conflict_issues = [i for i in report["issues"] if i["type"] == "conflict"]
        assert len(conflict_issues) == 0


class TestRedundancyDetection:
    def test_exact_duplicate(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="permit")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert any(i["type"] == "redundancy" and "完全重复" in i["desc"] for i in report["issues"])

    def test_covered_by_broader_rule(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="any", action="permit")

        new_rule = {
            "source_ip": "10.0.0.1",
            "dest_ip": "192.168.1.1",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert any(i["type"] == "redundancy" and "完全覆盖" in i["desc"] for i in report["issues"])

    def test_not_redundant_different_action(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="any", action="permit")

        new_rule = {
            "source_ip": "10.0.0.1",
            "dest_ip": "192.168.1.1",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "deny"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        redundancy_issues = [i for i in report["issues"] if i["type"] == "redundancy"]
        assert len(redundancy_issues) == 0

    def test_not_redundant_narrower_existing(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.1", dest_ip="192.168.1.1",
                             protocol="tcp", dest_port="80", action="permit")

        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "any",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        redundancy_issues = [i for i in report["issues"] if i["type"] == "redundancy"]
        assert len(redundancy_issues) == 0


class TestValidationReport:
    def test_valid_report_no_issues(self, validator, db, sample_device):
        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "permit"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert report["valid"] is True
        assert len(report["issues"]) == 0
        assert "验证通过" in report["summary"]

    def test_invalid_direction(self, validator, db, sample_device):
        report = validator.validate_rules("FW-01", "invalid_direction", [])
        assert report["valid"] is False
        assert any("无效的策略方向" in i["desc"] for i in report["issues"])

    def test_device_not_found(self, validator, db):
        report = validator.validate_rules("NONEXISTENT", "inbound", [])
        assert report["valid"] is False
        assert any("不存在" in i["desc"] for i in report["issues"])

    def test_missing_required_field(self, validator, db, sample_device):
        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert report["valid"] is False
        assert any("缺少必填字段" in i["desc"] for i in report["issues"])

    def test_invalid_action(self, validator, db, sample_device):
        new_rule = {
            "source_ip": "10.0.0.0/24",
            "dest_ip": "192.168.1.0/24",
            "protocol": "tcp",
            "dest_port": "80",
            "action": "invalid"
        }

        report = validator.validate_rules("FW-01", "inbound", [new_rule])
        assert report["valid"] is False
        assert any("无效的 action" in i["desc"] for i in report["issues"])

    def test_report_format(self, validator, db, sample_device):
        _add_existing_policy(db, source_ip="10.0.0.0/24", dest_ip="192.168.1.0/24",
                             protocol="tcp", dest_port="80", action="deny")

        new_rules = [
            {
                "source_ip": "10.0.0.0/24",
                "dest_ip": "192.168.1.0/24",
                "protocol": "tcp",
                "dest_port": "80",
                "action": "permit"
            },
            {
                "source_ip": "10.0.0.0/16",
                "dest_ip": "192.168.1.0/24",
                "protocol": "tcp",
                "dest_port": "80",
                "action": "permit"
            }
        ]

        report = validator.validate_rules("FW-01", "inbound", new_rules)
        assert "valid" in report
        assert "issues" in report
        assert "summary" in report

        for issue in report["issues"]:
            assert "rule_index" in issue
            assert "type" in issue
            assert "severity" in issue
            assert "desc" in issue
            assert issue["type"] in ("conflict", "redundancy", "error")
            assert issue["severity"] in ("error", "warning")


class TestPerformance:
    def test_large_rule_set(self, validator, db, sample_device):
        for i in range(100):
            _add_existing_policy(db, source_ip=f"10.{i // 256}.{i % 256}.0/24",
                                 dest_ip=f"192.168.{i}.0/24",
                                 protocol="tcp", dest_port=str(8000 + i),
                                 action="permit")

        new_rules = [
            {
                "source_ip": "10.0.0.0/24",
                "dest_ip": "192.168.0.0/24",
                "protocol": "tcp",
                "dest_port": "8000",
                "action": "permit"
            },
            {
                "source_ip": "172.16.0.0/16",
                "dest_ip": "10.10.0.0/16",
                "protocol": "tcp",
                "dest_port": "9999",
                "action": "deny"
            }
        ]

        import time
        start = time.time()
        report = validator.validate_rules("FW-01", "inbound", new_rules)
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Validation took {elapsed:.2f}s, expected < 5s"
        assert "valid" in report
        assert "issues" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
