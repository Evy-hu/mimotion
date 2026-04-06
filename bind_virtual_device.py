import os
import json
import util.zepp_helper as zeppHelper
import requests
import uuid
import random

def run_bind():
    # 1. 初始化配置
    config = json.loads(os.environ.get("CONFIG"))
    user = config.get('USER')
    password = config.get('PWD')

    print(f"尝试登录账号: {user}")
    access_token, msg = zeppHelper.login_access_token(user, password)
    if not access_token:
        print(f"登录失败: {msg}")
        return

    device_id = str(uuid.uuid4())
    login_token, app_token, user_id, msg = zeppHelper.grant_login_tokens(access_token, device_id)

    if not app_token:
        print(f"获取 Token 失败: {msg}")
        return

    # 2. 构造更真实的绑定请求 (V2 修复版)
    # 改动点：增加了更详细的 headers 和 data 校验位
    url = "https://api-mifit-cn.huami.com/v1/devices/bind.json"
    
    headers = {
        "appname": "com.xiaomi.hm.health",
        "appplatform": "android_phone",
        "v": "2.0",
        "cv": "6.14.0",
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "userid": user_id,
        "device_type": "2",  # 2 为手环
        "device_source": "24",
        "mac_address": ":".join(["%02x" % random.randint(0, 255) for _ in range(6)]).upper(),
        "device_sn": str(uuid.uuid4())[:16].upper(),
        "app_name": "com.xiaomi.hm.health",
        "country_code": "CN",
        "lang": "zh_CN",
        "timezone": "Asia/Shanghai"
    }
    
    print("正在尝试 V2 协议挂载虚拟手环...")
    # 尝试使用 POST
    res = requests.post(url, data=data, headers=headers).json()
    
    # 如果还是 1012，尝试自动切换到 PUT (这是某些后端架构的特殊要求)
    if res.get("code") == -1012:
        print("检测到 Method 限制，尝试切换 PUT 协议...")
        res = requests.put(url, data=data, headers=headers).json()
    
    if res.get("message") == "success" or res.get("code") == 1:
        print("✅ 虚拟设备挂载成功！")
    else:
        print(f"❌ 最终绑定失败: {res}")

if __name__ == "__main__":
    run_bind()
