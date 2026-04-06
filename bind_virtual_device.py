import os
import json
import util.zepp_helper as zeppHelper
import requests
import uuid
import random

def run_bind():
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

    # 2026 年最新可能的多个 API 端点
    endpoints = [
        "https://api-mifit-cn2.zepp.com/v1/devices/bind.json",
        "https://api-mifit-cn3.zepp.com/v1/devices/bind.json",
        "https://account-cn.huami.com/v1/devices/bind.json"
    ]
    
    headers = {
        "appname": "com.xiaomi.hm.health",
        "appplatform": "android_phone",
        "v": "6.14.0",
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "userid": user_id,
        "device_type": "2",  # 手环
        "device_source": "24",
        "mac_address": ":".join(["%02x" % random.randint(0, 255) for _ in range(6)]).upper(),
        "device_sn": str(uuid.uuid4())[:16].upper(),
        "country_code": "CN"
    }
    
    success = False
    for url in endpoints:
        print(f"正在探测端点: {url} ...")
        try:
            # 尝试 POST 提交
            res = requests.post(url, data=data, headers=headers, timeout=5).json()
            if res.get("message") == "success" or res.get("code") == 1:
                print(f"✅ 成功！通过端点 {url} 挂载虚拟手环。")
                success = True
                break
            else:
                print(f"⏩ 跳过: {res.get('message') or res.get('code')}")
        except Exception as e:
            print(f"⚠️ 连接失败: {url}")

    if not success:
        print("❌ 警告：所有已知 API 路径均已失效。华米可能彻底关闭了虚拟绑定。")
        print("💡 建议：去闲鱼买个 5 元的坏小米手环 2 代，扫码完成一次真绑定，即可永久解决。")

if __name__ == "__main__":
    run_bind()
