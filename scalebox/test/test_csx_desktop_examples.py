import os
import sys
import time
from typing import Callable, Optional


# 确保可以从项目根导入 scalebox
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scalebox.csx_desktop.main import Sandbox as DesktopSandbox  # noqa: E402


class CsxDesktopValidator:
    def __init__(self) -> None:
        self.desktop: Optional[DesktopSandbox] = None
        self.success_count = 0
        self.fail_count = 0

    def log_test_result(self, name: str, success: bool, error: Optional[Exception] = None) -> None:
        if success:
            self.success_count += 1
            print(f"✅ {name}")
        else:
            self.fail_count += 1
            print(f"❌ {name}: {error}")

    def run_test(self, fn: Callable[[], None], name: str) -> None:
        try:
            fn()
            self.log_test_result(name, True)
        except Exception as e:
            self.log_test_result(name, False, e)

    # ======================== 桌面沙箱基础 ========================

    def test_desktop_creation_and_stream(self) -> None:
        print("创建桌面沙箱...")
        # 可根据需要设置 template/timeout/debug 等参数
        self.desktop = DesktopSandbox(template="desktop", timeout=1800, debug=True)
        assert self.desktop is not None

        print("启动VNC流...")
        self.desktop.stream.start()
        url = self.desktop.stream.get_url(auto_connect=True)
        print(f"VNC URL: {url}")
        time.sleep(2)

    def test_mouse_operations(self) -> None:
        assert self.desktop is not None
        width, height = self.desktop.get_screen_size()
        print(f"屏幕: {width}x{height}")

        cx, cy = width // 2, height // 2
        self.desktop.move_mouse(cx, cy)
        x, y = self.desktop.get_cursor_position()
        print(f"光标: ({x}, {y})")

        self.desktop.left_click(cx, cy)
        self.desktop.right_click(min(cx + 100, width - 1), cy)
        self.desktop.double_click(cx, min(cy + 100, height - 1))
        self.desktop.drag((cx, cy), (min(cx + 120, width - 1), cy))
        self.desktop.scroll("down", 1)
        self.desktop.scroll("up", 1)

    def test_keyboard_and_terminal(self) -> None:
        assert self.desktop is not None
        print("启动终端并执行命令...")
        self.desktop.launch("xfce4-terminal")
        time.sleep(2)

        win = self.desktop.get_current_window_id()
        print(f"当前窗口: {win}")

        self.desktop.write("echo 'Hello from csx_desktop' && uname -a")
        self.desktop.press("enter")
        time.sleep(1)

        # 新建标签页
        self.desktop.press("ctrl+shift+t")
        time.sleep(0.5)
        self.desktop.write("ls -la ~")
        self.desktop.press("enter")

    def test_app_launch_and_navigation(self) -> None:
        assert self.desktop is not None
        print("启动文件管理器...")
        # 尝试启动 Thunar（常见于 XFCE）
        self.desktop.launch("thunar")
        time.sleep(2)

        # 通过键盘导航示例
        self.desktop.press("tab")
        self.desktop.press("down")
        self.desktop.press("down")
        self.desktop.press("enter")
        time.sleep(1)

    def cleanup(self) -> None:
        if self.desktop is None:
            return
        print("停止VNC流并清理...")
        try:
            self.desktop.stream.stop()
        except Exception as e:
            print(f"停止VNC流失败: {e}")
        # 如果需要，可在此添加更多清理逻辑（如关闭应用、结束会话等）

    def print_summary(self) -> None:
        total = self.success_count + self.fail_count
        print("\n===== csx_desktop 示例汇总 =====")
        print(f"总计: {total}, 成功: {self.success_count}, 失败: {self.fail_count}")

    def run_all(self) -> None:
        self.run_test(self.test_desktop_creation_and_stream, "创建桌面沙箱并启动VNC流")
        self.run_test(self.test_mouse_operations, "鼠标操作示例")
        self.run_test(self.test_keyboard_and_terminal, "键盘与终端示例")
        self.run_test(self.test_app_launch_and_navigation, "应用启动与导航示例")


if __name__ == "__main__":
    validator = CsxDesktopValidator()
    try:
        validator.run_all()
    finally:
        validator.cleanup()
        validator.print_summary()


