# SBX_API_KEY='sk-46I2XqSG6oIu0dWjCryHrJVno8eLswELgNwatXHX'
from scalebox.code_interpreter import Sandbox

sbx = Sandbox.create(template="code-interpreter", timeout=600)
print("created", sbx.sandbox_id)
#import pdb;pdb.set_trace()
#sbx.kill()
