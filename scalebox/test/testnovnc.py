from email.mime import application

from csx_desktop.main import Sandbox

sandbox = Sandbox()
sandbox.stream.start()

print(sandbox.get_screen_size())
sandbox.launch("firefox-esr")
windpws_id = sandbox.get_current_window_id()
print(windpws_id)
print(sandbox.get_window_title(window_id=windpws_id))
