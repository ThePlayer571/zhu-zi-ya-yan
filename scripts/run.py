from src.zhuziyayan.translator.translator import translate_program
from src.zhuziyayan.program_system.program import Program

with open('source_code.txt', 'r', encoding='utf-8') as f:
    source_code = f.read()
    program_info = translate_program(source_code)
    program = Program(program_info)
    program.run()
