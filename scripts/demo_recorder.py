"""运行 source_code.txt 并输出复盘记录。"""
import sys
sys.path.insert(0, 'src')

from zhuziyayan.translator.translator import translate_program
from zhuziyayan.program_system.program import Program
from zhuziyayan.program_system.io_strategy import PythonNativeIO

with open('scripts/source_code.txt', 'r', encoding='utf-8') as f:
    source = f.read()

program_info = translate_program(source)
program = Program(program_info, PythonNativeIO())
program.run()

output_path = 'output/复盘记录.txt'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(program.recorder.get_full_text())
print(f'Done → {output_path}')
