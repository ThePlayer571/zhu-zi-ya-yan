import sys
from pathlib import Path

# 将 src/ 加入 sys.path，与 tests/conftest.py 保持一致
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from zhuziyayan.translator.translator import translate_program
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.io_strategy import PythonNativeIO

source_path = Path(__file__).resolve().parent / "source_code.txt"
with open(source_path, 'r', encoding='utf-8') as f:
    source_code = f.read()
    program_info = translate_program(source_code)
    program = Program(program_info, PythonNativeIO())
    program.run()
