from __future__ import annotations

from zhuziyayan.program_system.value import Value, ValueType
from zhuziyayan.program_system.variable import Variable


class Context:
    """管理变量的上下文。

    维护一个从变量名到 Variable 的字典。支持嵌套上下文：
    构建时传入另一个 Context 作为全局上下文，
    当前上下文未找到变量时会向上查找。
    """

    def __init__(self, global_context: Context | None):
        self._variables: dict[str, Variable] = {}
        self._global_context: Context | None = global_context

    def has_variable(self, var_name: str) -> bool:
        """检查上下文中是否存在该变量。"""
        if var_name in self._variables:
            return True
        if self._global_context is not None:
            return self._global_context.has_variable(var_name)
        return False

    def get_variable(self, var_name: str) -> Variable:
        """获取变量。

        优先从当前上下文查找；找不到则去全局上下文查找；
        都找不到则抛出 KeyError。
        """
        if var_name in self._variables:
            return self._variables[var_name]
        if self._global_context is not None:
            return self._global_context.get_variable(var_name)
        raise KeyError(f"变量 '{var_name}' 未定义")

    def set_variable(self, var_name: str, value: Value):
        """设置变量。

        若变量已存在，修改其值（保留 Variable 对象引用）；
        若当前上下文没有但全局上下文有，则委托全局上下文；
        若都没有，则在当前上下文中创建新变量。
        """
        if var_name in self._variables:
            self._variables[var_name].set_value(value)
        elif self._global_context is not None and self._global_context.has_variable(var_name):
            self._global_context.set_variable(var_name, value)
        else:
            self._variables[var_name] = Variable(var_name, value)

    def set_to_none(self, var_name: str):
        """将指定变量置为 None。"""
        self.set_variable(var_name, Value(ValueType.NONE, None))
