import time

from scalebox.csx_desktop.main import Sandbox


def desktop_automation_demo():
    """桌面自动化功能演示"""

    # 1. 创建桌面沙箱实例
    print("正在启动桌面沙箱...")
    desktop = Sandbox(timeout=3600, template="browser-use")
    # print(f"沙箱已启动，ID: {desktop.sandbox_id}")

    # 2. 启动VNC流以便远程查看桌面
    print("启动VNC远程桌面...")
    time.sleep(5)
    desktop.stream.start()
    vnc_url = desktop.stream.get_url(auto_connect=True)
    print(f"VNC访问URL: {vnc_url}")
    # print(f"VNC认证密钥: {desktop.stream.get_auth_key()}")

    # 等待系统完全启动
    time.sleep(3)

    # 3. 基本鼠标操作示例
    print("执行鼠标操作...")

    # 获取屏幕尺寸
    screen_width, screen_height = desktop.get_screen_size()
    print(f"屏幕尺寸: {screen_width}x{screen_height}")

    # 移动鼠标到屏幕中心
    center_x, center_y = screen_width // 2, screen_height // 2
    desktop.move_mouse(center_x, center_y)

    # 获取当前光标位置
    cursor_x, cursor_y = desktop.get_cursor_position()
    print(f"光标位置: ({cursor_x}, {cursor_y})")

    # 左键点击
    desktop.left_click(center_x, center_y)

    # 右键点击
    desktop.right_click(center_x + 100, center_y)

    # 双击
    desktop.double_click(center_x, center_y + 100)

    # 鼠标拖动示例
    desktop.drag((center_x, center_y), (center_x + 200, center_y))

    # 鼠标滚动
    desktop.scroll("down", 2)  # 向下滚动2次
    desktop.scroll("up", 1)  # 向上滚动1次

    # 4. 键盘输入示例
    print("执行键盘操作...")

    # 打开终端
    desktop.launch("xfce4-terminal")  # 或 xfce4-terminal
    time.sleep(2)

    # 获取当前窗口ID
    current_window = desktop.get_current_window_id()
    print(f"当前窗口ID: {current_window}")

    # 输入命令
    desktop.write("echo 'Hello from SBX Sandbox!'")
    desktop.press("enter")

    # 特殊按键
    desktop.press("ctrl+shift+t")  # 新建标签页
    time.sleep(1)

    desktop.write("ls -la")
    desktop.press("enter")

    # 5. 窗口管理示例
    print("执行窗口管理操作...")

    # 获取所有可见窗口
    terminal_windows = desktop.get_application_windows("xfce4-terminal")
    print(f"终端窗口: {terminal_windows}")

    if terminal_windows:
        # 获取窗口标题
        window_title = desktop.get_window_title(terminal_windows[0])
        print(f"窗口标题: {window_title}")

    # 6. 启动应用程序示例
    print("启动其他应用程序...")

    # 使用gtk-launch启动应用程序
    try:
        desktop.launch("firefox-esr")  # 启动Firefox浏览器
        time.sleep(3)

        # 在Firefox中输入URL
        desktop.press("ctrl+l")  # 聚焦地址栏
        desktop.write("https://www.google.com")
        desktop.press("enter")

    except Exception as e:
        print(f"启动Firefox失败: {e}")

    # 7. 文件操作示例 - 创建并打开文件
    print("执行文件操作...")

    # 创建测试文件
    test_content = """Hello World!
This is a test file created from Scalebox Sandbox SDK.
Current time: {time}
""".format(
        time=time.ctime()
    )

    desktop.files.write("/tmp/test_file.txt", test_content)
    print("已创建测试文件")

    # 使用默认程序打开文件
    # desktop.open("/tmp/test_file.txt")
    # time.sleep(2)

    # 8. 截图功能示例
    print("执行截图操作...")

    # 截取屏幕并保存为bytes
    screenshot_bytes = desktop.screenshot(format="bytes")
    print(f"截图大小: {len(screenshot_bytes)} 字节")

    # 也可以获取截图流
    # screenshot_stream = desktop.screenshot(format="stream")
    # for chunk in screenshot_stream:
    #     # 处理截图数据
    #     pass

    # 9. 复杂自动化脚本示例
    print("执行复杂自动化任务...")

    # 返回终端窗口
    terminal_windows = desktop.get_application_windows("xfce4-terminal")
    if terminal_windows:
        # 激活终端窗口
        desktop.commands.run(
            f"DISPLAY={desktop._display} xdotool windowactivate {terminal_windows[0]}"
        )

        # 创建Python脚本并执行
        python_script = """#!/usr/bin/env python3
import time
print("starting...")
for i in range(5):
    print(f"count: {i}")
time.sleep(0.5)
print("success!")
"""

        script_path = "/tmp/automation_script.py"
        desktop.files.write(script_path, python_script)

        desktop.write(f"python3 /uploads{script_path}")
        desktop.press("enter")

    # 10. 等待和定时操作
    print("等待操作完成...")
    desktop.wait(2000)  # 等待2秒

    # 展示所有功能已完成
    desktop.write("echo 'All successfully!'")
    desktop.press("enter")

    print("演示完成! 沙箱将在10分钟后自动关闭或按Ctrl+C提前结束")

    # 保持沙箱运行以便观察
    try:
        time.sleep(600)  # 保持10分钟
    except KeyboardInterrupt:
        print("提前结束沙箱会话")

    # 11. 清理工作会在with语句退出时自动执行


# def specific_use_cases():
#     """特定用例示例"""
#
#     # 用例1: 网页自动化测试
#     def web_automation():
#         with Sandbox() as desktop:
#             desktop.open("firefox")
#             time.sleep(3)
#             desktop.press("ctrl+l")
#             desktop.write("https://www.google.com")
#             desktop.press("enter")
#             time.sleep(2)
#             desktop.write("Scalebox Sandbox Automation")
#             desktop.press("enter")
#             # 更多网页自动化操作...
#
#     # 用例2: GUI应用测试
#     def gui_app_testing():
#         with Sandbox() as desktop:
#             # 启动待测试的GUI应用
#             desktop.launch("some-gui-application")
#             time.sleep(2)
#
#             # 执行一系列测试操作
#             desktop.move_mouse(100, 100)
#             desktop.left_click()
#             desktop.write("测试输入")
#             desktop.press("enter")
#
#             # 验证结果
#             screenshot = desktop.screenshot(format="bytes")
#             # 这里可以添加截图分析逻辑
#
#     # 用例3: 教育演示
#     def educational_demo():
#         with Sandbox() as desktop:
#             # 打开编程环境
#             desktop.open("vscode")  # 或其他IDE
#
#             # 逐步演示代码编写和执行过程
#             time.sleep(2)
#             desktop.write("# Python编程演示")
#             desktop.press("enter")
#             desktop.write("print('Hello, Students!')")
#             desktop.press("enter")
#
#             # 保存并运行
#             desktop.press("ctrl+s")
#             desktop.press("ctrl+alt+t")  # 打开终端
#             desktop.write("python3 demo.py")
#             desktop.press("enter")


if __name__ == "__main__":
    try:
        desktop_automation_demo()
    except Exception as e:
        print(f"演示过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
