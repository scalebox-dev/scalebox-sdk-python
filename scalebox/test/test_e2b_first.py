from dotenv import load_dotenv

load_dotenv()
from e2b_code_interpreter import Sandbox

sbx = Sandbox.create()  # By default the sandbox is alive for 5 minutes
execution = sbx.run_code("print('hello world')")  # Execute Python inside the sandbox
print(execution)

files = sbx.files.list("/")
print(files)
