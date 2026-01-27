#!/usr/bin/env python3
"""
测试用例：基于desktop创建sandbox，上传并执行test_sf.py
"""

import os
import re
import sys
import time

# 确保可以从项目根导入 scalebox
from scalebox.csx_desktop.main import Sandbox


def main():
    """主测试函数"""
    print("=" * 60)
    print("开始测试：基于desktop创建sandbox并执行test_sf.py")
    print("=" * 60)
    
    # 1. 基于desktop创建sandbox
    print("\n[步骤 1] 正在创建desktop sandbox...")
    sandbox = Sandbox.create(
        template="browser-use",
        timeout=3600,  # 1小时超时
    )
    print(f"✓ Sandbox创建成功，ID: {sandbox.sandbox_id}")
    
    # 2. 获取network_proxy
    print("\n[步骤 2] 获取network_proxy...")
    network_proxy = sandbox.network_proxy()
    print(f"✓ Network Proxy: {network_proxy}")
    
    # 3. 获取VNC URL（不启动，直接获取）
    print("\n[步骤 3] 获取VNC URL...")
    vnc_url = sandbox.stream.get_url(auto_connect=True)
    print(f"✓ VNC URL: {vnc_url}")
    
    # 4. 读取test_sf.py并修改username和password
    print("\n[步骤 4] 读取并修改test_sf.py...")
    test_sf_path = os.path.join(os.path.dirname(__file__), "test_sf.py")
    
    with open(test_sf_path, 'r', encoding='utf-8') as f:
        test_sf_content = f.read()
    
    # 从network_proxy中提取username和password
    if network_proxy and isinstance(network_proxy, dict):
        # network_proxy结构: {'proxy_configs': {'username': '...', 'password': '...', ...}, ...}
        proxy_configs = network_proxy.get("proxy_configs", {})
        if isinstance(proxy_configs, dict):
            proxy_username = proxy_configs.get("username", "")
            proxy_password = proxy_configs.get("password", "")
        else:
            # 兼容旧格式：直接在network_proxy中
            proxy_username = network_proxy.get("username", "")
            proxy_password = network_proxy.get("password", "")
        
        if not proxy_username or not proxy_password:
            print("⚠ 警告: network_proxy中缺少username或password字段")
            print(f"  network_proxy内容: {network_proxy}")
        else:
            # 替换test_sf.py中的username和password
            # 匹配proxy字典中的username和password（处理可能的引号差异）
            pattern_username = r'"username"\s*:\s*"[^"]*"'
            pattern_password = r'"password"\s*:\s*"[^"]*"'
            
            test_sf_content = re.sub(
                pattern_username,
                f'"username": "{proxy_username}"',
                test_sf_content
            )
            test_sf_content = re.sub(
                pattern_password,
                f'"password": "{proxy_password}"',
                test_sf_content
            )
            
            print(f"✓ 已更新username: {proxy_username}")
            print(f"✓ 已更新password: {proxy_password[:20]}...")
    else:
        print("⚠ 警告: network_proxy为空或格式不正确，跳过修改")
        print(f"  network_proxy类型: {type(network_proxy)}, 值: {network_proxy}")
    
    # 5. 上传test_sf.py到sandbox的/目录
    print("\n[步骤 5] 上传test_sf.py到sandbox的/目录...")
    result = sandbox.files.write("/test_sf.py", test_sf_content.encode('utf-8'))
    print(f"✓ 文件上传成功: {result.path}")
    
    # 6. 在sandbox中执行命令
    print("\n[步骤 6] 在sandbox中执行: source /venv/bin/activate && python /test_sf.py")
    try:
        # 使用bash -c确保source命令和环境变量正确加载
        result = sandbox.commands.run(
            'bash -c "source /venv/bin/activate && python /test_sf.py"',
            timeout=600  # 10分钟超时
        )
        print(f"✓ 命令执行完成")
        print(f"退出码: {result.exit_code}")
        print(f"标准输出:\n{result.stdout}")
        if result.stderr:
            print(f"标准错误:\n{result.stderr}")
    except Exception as e:
        print(f"✗ 命令执行失败: {e}")
        raise
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    # 清理（可选，注释掉以保留sandbox）
    # sandbox.kill()
    # print("Sandbox已清理")


if __name__ == "__main__":
    main()

