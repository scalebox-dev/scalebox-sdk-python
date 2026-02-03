from scalebox.code_interpreter import Sandbox
import json

# 1. 准备要上传的文件内容
print("正在准备文件内容...")
results_data = {
    "experiment_id": "exp_001",
    "status": "completed",
    "metrics": {"accuracy": 0.952, "precision": 0.94, "recall": 0.96},
    "timestamp": "2024-01-01T12:00:00Z",
    "details": [
        {"epoch": 1, "loss": 0.45},
        {"epoch": 2, "loss": 0.32},
        {"epoch": 3, "loss": 0.18},
    ],
}

# 转换为 JSON 字符串
json_content = json.dumps(results_data, indent=2)

# 2. 创建沙箱并写入文件
print("\n正在创建沙箱并写入文件...")
sandbox = Sandbox.create(timeout=1800)
remote_path = "/home/user/results.json"

# 关键修改：使用 sandbox.write() 写入文件
sandbox.files.write(remote_path, json_content)
print(f"✅ 文件已写入沙箱: {remote_path}")

# 3. 获取预签名下载 URL
print("\n正在生成下载链接...")
download_url = sandbox.download_url(
    path=remote_path, use_signature_expiration=180  # 180秒有效期
)

print(f"\n📥 下载 URL: {download_url}")
print(f"⏰ 链接将在 3 分钟后过期")

upload_url = sandbox.upload_url(path="/home/user", use_signature_expiration=360)
print(f"\n📥 上传 URL: {upload_url}")
print(f"⏰ 链接将在 6 分钟后过期")
