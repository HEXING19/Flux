#!/usr/bin/env python3
"""
测试IP封禁API调用
用于诊断签名和参数问题
"""

import sys
sys.path.append('/Users/hexing/Flux/backend')

from app.services.ipblock_service import IpBlockService
from app.utils.sdk.aksk_py3 import Signature

# 测试参数
flux_base_url = "https://10.5.41.194"
auth_code = "32333965343537652D313835352D343037362D396636612D3935383930353036376337317C7C7C73616E67666F727C76317C3132372E302E302E317C7C7C7C35343444393835394443304433304135434143454536354136454236314232323332383541343346313533453043463635434136373245453138334443464139443445393731413646444134373430453345334243453145453843394242423332393536333135393736414145423241413136314635363438423235394134447C39364135364538423334344139373635394434303334434642353442354336323638304143443539364337394146453841304345393142433044373330354531354332454333364331393443443144303938423442314630303245363442464239414643303639324331394633463234363041353146454632444531444334437C7C307C"

print("=" * 80)
print("IP封禁API测试")
print("=" * 80)

# 测试1：验证auth_code解码
print("\n[测试1] 解码auth_code")
try:
    sig = Signature(auth_code=auth_code)
    print(f"✅ auth_code解码成功")
except Exception as e:
    print(f"❌ auth_code解码失败: {e}")
    sys.exit(1)

# 测试2：创建服务并测试IP封禁
print("\n[测试2] 测试IP封禁调用")

service = IpBlockService(
    base_url=flux_base_url,
    auth_code=auth_code
)

# 测试封禁参数
test_params = {
    "ip_address": "100.200.1.200",
    "device_id": 57,
    "device_name": "物联网安全网关",
    "device_type": "AF",
    "device_version": "8.0.106",
    "block_type": "SRC_IP",
    "time_type": "forever",
    "time_unit": "d",
    "reason": "测试封禁"
}

print(f"IP地址: {test_params['ip_address']}")
print(f"设备: {test_params['device_name']} (ID: {test_params['device_id']})")
print(f"设备版本: {test_params['device_version']}")
print(f"封禁类型: {test_params['block_type']}")
print(f"时长: {test_params['time_type']}")
print(f"原因: {test_params['reason']}")

print("\n[执行封禁]")

result = service.block_ip(
    ip_address=test_params["ip_address"],
    device_id=test_params["device_id"],
    device_name=test_params["device_name"],
    device_type=test_params["device_type"],
    device_version=test_params["device_version"],
    block_type=test_params["block_type"],
    time_type=test_params["time_type"],
    time_value=None,
    time_unit=test_params["time_unit"],
    reason=test_params["reason"]
)

print("\n" + "=" * 80)
print("封禁结果")
print("=" * 80)
print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")

if result.get("success"):
    print(f"Rule IDs: {result.get('rule_ids', [])}")
    print(f"Rule Count: {result.get('rule_count', 0)}")
else:
    print(f"Error Type: {result.get('error_info', {}).get('error_type')}")
    print(f"Raw Message: {result.get('error_info', {}).get('raw_message')}")

print("\n" + "=" * 80)
