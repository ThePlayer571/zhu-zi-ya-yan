class Program:
    """程序运行的环境。

    注意这个类不负责解释，只负责执行。
    """
    def __init__(self, source_code: str):
        self.source_code = source_code
