import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("program_live.py", base=base)
]

setup(
    name="LOL Live Extractor",
    version="0.1",
    description="League of Legends Live Client Data Extractor",
    executables=executables
)