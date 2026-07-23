import sys
from pathlib import Path

# 将 src/ 加入 sys.path，使测试可以直接 import zhuziyayan
src_path = Path(__file__).resolve().parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
