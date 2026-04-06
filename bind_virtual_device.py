import os
import json
import util.zepp_helper as zeppHelper

def run_bind():
    # 从环境变量读取你已经配置好的 CONFIG
    config = json.loads(os.environ.get("CONFIG"))
    user = config.get('USER')
    password = config.get('PWD')

    print(f"尝试登录账号: {user}")
    # 1. 登录并获取 access_token
    access_token, msg = zeppHelper.login_access_token(user, password)
    if not access_token:
        print(f"登录失败: {msg}")
        return

    # 2. 获取所需的各种 Token 和 userid
    # 这里 device_id 随便生成一个即可，zeppHelper 会处理
    import uuid
    device_id = str(uuid.uuid4())
    login_token, app_token, user_id, msg = zeppHelper.grant_login_tokens(access_token, device_id)

    if not app_token:
        print(f"获取 Token 失败: {msg}")
        return

    # 3. 调用绑定接口挂载虚拟手环
    import requests
    url = "https://api-mifit-cn.huami.com/v1/devices/bind.json"
    data = {
        "userid": user_id,
        "device_type": "2", # 强制手环类型
        "device_source": "24",
        "mac_address": "00:11:22:33:44:55", # 虚拟 MAC
        "device_sn": str(uuid.uuid4())[:16].upper(),
        "app_name": "com.xiaomi.hm.health",
        "cv": "6.14.0"
    }
    headers = {"apptoken": app_token}
    
    print("正在向服务器申请挂载虚拟手环...")
    res = requests.post(url, data=data, headers=headers).json()
    
    if res.get("message") == "success":
        print("✅ 恭喜！虚拟设备挂载成功。你的账号现在已有“硬件身份”了。")
    else:
        print(f"❌ 绑定返回结果: {res}")

if __name__ == "__main__":
    run_bind()
