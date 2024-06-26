import os
import sys

from dotenv import load_dotenv

sys.path.append(".")
if os.path.exists("../envs/dev.env"):
    load_dotenv("../envs/dev.env", override=True)
