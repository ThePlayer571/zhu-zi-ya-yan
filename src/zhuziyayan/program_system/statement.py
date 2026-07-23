from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import TYPE_CHECKING, Callable

from zhuziyayan.program_system.context import Context
from zhuziyayan.program_system.expression import (
    ValueExpression,
    VariableExpression,
    ListIndexExpression,
    list_element_type,
)
from zhuziyayan.program_system.value import (
    Value,
    ValueType,
    is_zero,
    is_positive,
)

if TYPE_CHECKING:
    from zhuziyayan.program_system.function import Function


# =============================================================================
# ComputeOperator — 计算赋值运算符
# =============================================================================


class ComputeOperator(Enum):
    """计算赋值运算符。"""

    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()


# _UNSUPPORTED — _compute 返回此值表示该类型不支持该运算
_UNSUPPORTED = object()


# =============================================================================
# Statement — 语句基类
# =============================================================================


class Statement(ABC):
    """语句基类。

    每条语句对应源码中的一条可执行单元，以终止符（。？！）结尾。
    """

    def __init__(self, source_code: str, context: Context):
        self._source_code = source_code
        self._context = context

    @property
    def source_code(self) -> str:
        """该语句对应的源码文本。"""
        return self._source_code

    @abstractmethod
    def run(self):
        """运行该语句，修改 context 或造成其他副作用。绝不抛出异常。"""
        ...


# =============================================================================
# 1. VariableDefinitionStatement — 变量定义
# =============================================================================


class VariableDefinitionStatement(Statement):
    """变量定义语句。

    定义新变量并初始化为指定的类型和值。
    """

    def __init__(self, source_code: str, context: Context,
                 variable_name: str, value: Value):
        super().__init__(source_code, context)
        self._variable_name = variable_name
        self._value = value

    @property
    def variable_name(self) -> str:
        """新变量的名称。"""
        return self._variable_name

    @property
    def value(self) -> Value:
        """变量的初始值（Value 对象）。"""
        return self._value

    def run(self):
        self._context.set_variable(self._variable_name, self._value)


# =============================================================================
# 2. AssignmentStatement — 赋值
# =============================================================================


class AssignmentStatement(Statement):
    """赋值语句。

    将右侧值返回表达式的值赋给左侧变量。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str, source: ValueExpression):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._source = source

    @property
    def target_variable_name(self) -> str:
        """赋值目标变量名（左侧）。"""
        return self._target_variable_name

    @property
    def source(self) -> ValueExpression:
        """赋值来源表达式（右侧）。"""
        return self._source

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        source_value = self._source.evaluate(self._context)

        if source_value.type == ValueType.NONE:
            self._context.set_to_none(self._target_variable_name)
            return

        raw = source_value.raw
        target_type = target_var.value.type

        # 列表赋值需要深拷贝
        if target_type in (
            ValueType.STRING_LIST, ValueType.INTEGER_LIST,
            ValueType.FLOAT_LIST, ValueType.BOOLEAN_LIST,
        ):
            raw = copy.deepcopy(raw)

        new_value = Value(target_type, raw)
        target_var.set_value(new_value)


# =============================================================================
# 3. ComputeAssignmentStatement — 计算赋值
# =============================================================================


class ComputeAssignmentStatement(Statement):
    """计算赋值语句。

    对变量执行运算后将结果赋回原变量。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str, operator: ComputeOperator,
                 source: ValueExpression):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._operator = operator
        self._source = source

    @property
    def target_variable_name(self) -> str:
        """运算目标变量名。"""
        return self._target_variable_name

    @property
    def operator(self) -> ComputeOperator:
        """运算符。"""
        return self._operator

    @property
    def source(self) -> ValueExpression:
        """运算右侧表达式。"""
        return self._source

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        lhs = target_var.value
        rhs = self._source.evaluate(self._context)

        if rhs.type == ValueType.NONE:
            self._context.set_to_none(self._target_variable_name)
            return

        if lhs.type != rhs.type:
            self._context.set_to_none(self._target_variable_name)
            return

        raw_result = self._compute(lhs.raw, rhs.raw, lhs.type)
        if raw_result is _UNSUPPORTED:
            self._context.set_to_none(self._target_variable_name)
            return

        new_value = Value(lhs.type, raw_result)
        target_var.set_value(new_value)

    def _compute(self, lhs_raw, rhs_raw, value_type: ValueType):
        """根据运算符和类型执行计算。

        若该类型不支持此运算，返回 _UNSUPPORTED。
        """
        op = self._operator

        if value_type == ValueType.INTEGER:
            if op == ComputeOperator.ADD:
                return lhs_raw + rhs_raw
            elif op == ComputeOperator.SUB:
                return lhs_raw - rhs_raw
            elif op == ComputeOperator.MUL:
                return lhs_raw * rhs_raw
            elif op == ComputeOperator.DIV:
                return lhs_raw // rhs_raw
            elif op == ComputeOperator.MOD:
                return lhs_raw % rhs_raw

        elif value_type == ValueType.FLOAT:
            if op == ComputeOperator.ADD:
                return lhs_raw + rhs_raw
            elif op == ComputeOperator.SUB:
                return lhs_raw - rhs_raw
            elif op == ComputeOperator.MUL:
                return lhs_raw * rhs_raw
            elif op == ComputeOperator.DIV:
                return lhs_raw / rhs_raw
            elif op == ComputeOperator.MOD:
                return lhs_raw % rhs_raw

        elif value_type == ValueType.STRING:
            if op == ComputeOperator.ADD:
                return lhs_raw + rhs_raw
            return _UNSUPPORTED

        elif value_type == ValueType.BOOLEAN:
            if op == ComputeOperator.ADD:
                return bool(lhs_raw + rhs_raw)
            return _UNSUPPORTED

        elif value_type in (
            ValueType.STRING_LIST, ValueType.INTEGER_LIST,
            ValueType.FLOAT_LIST, ValueType.BOOLEAN_LIST,
        ):
            if op == ComputeOperator.ADD:
                return lhs_raw + rhs_raw
            return _UNSUPPORTED

        return _UNSUPPORTED


# =============================================================================
# 4. ZeroCheckStatement — 判零
# =============================================================================


class ZeroCheckStatement(Statement):
    """判零语句。

    判断变量是否为"零"，将布尔结果赋回原变量。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name

    @property
    def target_variable_name(self) -> str:
        """被判断的变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        result = is_zero(target_var.value)
        target_var.set_value(Value(ValueType.BOOLEAN, result))


# =============================================================================
# 5. PositiveCheckStatement — 判正
# =============================================================================


class PositiveCheckStatement(Statement):
    """判正语句。

    判断变量是否为"正"，将布尔结果赋回原变量。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name

    @property
    def target_variable_name(self) -> str:
        """被判断的变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        result = is_positive(target_var.value)
        target_var.set_value(Value(ValueType.BOOLEAN, result))


# =============================================================================
# 6. ListIndexModifyStatement — 列表索引修改
# =============================================================================


class ListIndexModifyStatement(Statement):
    """列表索引修改语句。

    修改列表指定位置（1-based）的元素。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str, index: int,
                 source: ValueExpression):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._index = index  # 1-based
        self._source = source

    @property
    def target_variable_name(self) -> str:
        """目标列表变量名。"""
        return self._target_variable_name

    @property
    def index(self) -> int:
        """索引（1-based）。"""
        return self._index

    @property
    def source(self) -> ValueExpression:
        """新的元素值表达式。"""
        return self._source

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        new_value = self._source.evaluate(self._context)

        if new_value.type == ValueType.NONE:
            self._context.set_to_none(self._target_variable_name)
            return

        zero_based = self._index - 1
        list_raw = target_var.value.raw

        if zero_based < 0 or zero_based >= len(list_raw):
            self._context.set_to_none(self._target_variable_name)
            return

        # 类型校验：新值的类型必须与列表元素类型一致
        element_type = list_element_type(target_var.value.type)
        if element_type is not None and new_value.type != element_type:
            self._context.set_to_none(self._target_variable_name)
            return

        list_raw[zero_based] = new_value.raw


# =============================================================================
# 7. ListAppendStatement — 列表追加
# =============================================================================


class ListAppendStatement(Statement):
    """列表追加语句。

    向列表末尾追加新元素。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str, source: ValueExpression):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._source = source

    @property
    def target_variable_name(self) -> str:
        """目标列表变量名。"""
        return self._target_variable_name

    @property
    def source(self) -> ValueExpression:
        """要追加的值表达式。"""
        return self._source

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        new_value = self._source.evaluate(self._context)

        if new_value.type == ValueType.NONE:
            self._context.set_to_none(self._target_variable_name)
            return

        # 类型校验
        element_type = list_element_type(target_var.value.type)
        if element_type is not None and new_value.type != element_type:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.value.raw.append(new_value.raw)


# =============================================================================
# 8. ListPopTailStatement — 删除尾部元素
# =============================================================================


class ListPopTailStatement(Statement):
    """列表删尾语句。

    删除列表的最后一个元素。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name

    @property
    def target_variable_name(self) -> str:
        """目标列表变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        if not target_var.value.raw:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.value.raw.pop()


# =============================================================================
# 9. ListPopHeadStatement — 删除头部元素
# =============================================================================


class ListPopHeadStatement(Statement):
    """列表删头语句。

    删除列表的第一个元素。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name

    @property
    def target_variable_name(self) -> str:
        """目标列表变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        if not target_var.value.raw:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.value.raw.pop(0)


# =============================================================================
# 10. FunctionCallStatement — 函数调用
# =============================================================================


class FunctionCallStatement(Statement):
    """函数调用语句。

    调用指定名称的函数。
    """

    def __init__(self, source_code: str, context: Context,
                 function_name: str,
                 function_provider: Callable[[str], Function]):
        super().__init__(source_code, context)
        self._function_name = function_name
        self._function_provider = function_provider

    @property
    def function_name(self) -> str:
        """被调用的函数名（不含《》）。"""
        return self._function_name

    def run(self):
        func = self._function_provider(self._function_name)
        if func is not None:
            func.execute(self._context)


# =============================================================================
# 11. IfStatement — 条件控制流
# =============================================================================


class IfStatement(Statement):
    """If 条件语句。

    若条件变量为 True，则调用指定函数；否则跳过。
    """

    def __init__(self, source_code: str, context: Context,
                 condition_variable_name: str, function_name: str,
                 function_provider: Callable[[str], Function]):
        super().__init__(source_code, context)
        self._condition_variable_name = condition_variable_name
        self._function_name = function_name
        self._function_provider = function_provider

    @property
    def condition_variable_name(self) -> str:
        """条件变量名。"""
        return self._condition_variable_name

    @property
    def function_name(self) -> str:
        """条件为真时调用的函数名（不含《》）。"""
        return self._function_name

    def run(self):
        if not self._context.has_variable(self._condition_variable_name):
            return

        cond_var = self._context.get_variable(self._condition_variable_name)
        if cond_var.value.type != ValueType.BOOLEAN:
            return

        if cond_var.value.raw:
            func = self._function_provider(self._function_name)
            if func is not None:
                func.execute(self._context)


# =============================================================================
# 12. OutputStatement — 输出
# =============================================================================


class OutputStatement(Statement):
    """输出语句。

    将变量的值展示于外界。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str,
                 output_fn: Callable[[object], None] = print):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._output_fn = output_fn

    @property
    def target_variable_name(self) -> str:
        """要输出的变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            return

        target_var = self._context.get_variable(self._target_variable_name)
        self._output_fn(target_var.value.raw)


# =============================================================================
# 13. InputStatement — 输入
# =============================================================================


class InputStatement(Statement):
    """输入语句。

    从外界读取一行数据，以字符串类型存入变量。
    """

    def __init__(self, source_code: str, context: Context,
                 target_variable_name: str,
                 input_fn: Callable[[], str] = input):
        super().__init__(source_code, context)
        self._target_variable_name = target_variable_name
        self._input_fn = input_fn

    @property
    def target_variable_name(self) -> str:
        """接收输入的变量名。"""
        return self._target_variable_name

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        raw = self._input_fn()
        target_var = self._context.get_variable(self._target_variable_name)
        target_var.set_value(Value(ValueType.STRING, raw))


# =============================================================================
# 14. LiteraryStatement — 文学性语句
# =============================================================================


class LiteraryStatement(Statement):
    """文学性语句。

    无法解析出任何含义的语句，运行时不产生任何效果。
    """

    def run(self):
        pass
