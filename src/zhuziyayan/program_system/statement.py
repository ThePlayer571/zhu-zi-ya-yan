from __future__ import annotations

import copy
from abc import ABC, abstractmethod
from enum import Enum, auto
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
from zhuziyayan.translator.statement_info import StatementInfo
from zhuziyayan.utils import (
    format_chinese_integer,
    try_parse_boolean_input,
    try_parse_float_input,
    try_parse_integer_input,
    try_parse_string_input,
)


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

# _COMPUTE_OPERATOR_NAMES — 运算符的中文名映射
_COMPUTE_OPERATOR_NAMES: dict[ComputeOperator, str] = {
    ComputeOperator.ADD: "加",
    ComputeOperator.SUB: "减",
    ComputeOperator.MUL: "乘",
    ComputeOperator.DIV: "除以",
    ComputeOperator.MOD: "取模",
}

# _VALUE_TYPE_NAMES — ValueType 的中文名映射
_VALUE_TYPE_NAMES: dict[ValueType, str] = {
    ValueType.NONE: "无",
    ValueType.STRING: "字符串",
    ValueType.INTEGER: "整数",
    ValueType.FLOAT: "浮点数",
    ValueType.BOOLEAN: "布尔",
    ValueType.STRING_LIST: "字符串列表",
    ValueType.INTEGER_LIST: "整数列表",
    ValueType.FLOAT_LIST: "浮点数列表",
    ValueType.BOOLEAN_LIST: "布尔列表",
}

# _VALUE_TYPE_LABELS — ValueType 的简洁类型标签，用于【疏】
_VALUE_TYPE_LABELS: dict[ValueType, str] = {
    ValueType.NONE: "无",
    ValueType.STRING: "言",
    ValueType.INTEGER: "数",
    ValueType.FLOAT: "度",
    ValueType.BOOLEAN: "辩",
    ValueType.STRING_LIST: "列言",
    ValueType.INTEGER_LIST: "列数",
    ValueType.FLOAT_LIST: "列度",
    ValueType.BOOLEAN_LIST: "列辩",
}


# =============================================================================
# Statement — 语句基类
# =============================================================================


class Statement(ABC):
    """语句基类。

    每条语句对应源码中的一条可执行单元，以终止符（。？！）结尾。
    子类在 __init__ 中设置 _name 并通过 _register_detail() 注册执行细节。
    """

    def __init__(self, statement_info: StatementInfo, context: Context):
        self._statement_info = statement_info
        self._context = context
        self._name: str = ""
        self._details: dict[str, str] = {}

    # -------------------------------------------------------------------------
    # 只读属性
    # -------------------------------------------------------------------------

    @property
    def statement_info(self) -> StatementInfo:
        """该语句对应的源码信息。"""
        return self._statement_info

    @property
    def name(self) -> str:
        """语句类型的中文名（如 赋值、函数调用、条件判断）。"""
        return self._name

    @property
    def details(self) -> dict[str, str]:
        """执行细节的只读字典，键为属性名，值为字符串表示。"""
        return dict(self._details)

    # -------------------------------------------------------------------------
    # 子类注册接口
    # -------------------------------------------------------------------------

    def _register_detail(self, key: str, value: str) -> None:
        """子类在 __init__ 中调用，向 details 字典注册一条执行细节。"""
        self._details[key] = value

    @abstractmethod
    def describe(self) -> tuple[str, str]:
        """返回 (statement_description, change) 二元组。

        在 run() 之后调用，change 通过查询 _context 获取执行后变量的当前值。
        """
        ...

    @abstractmethod
    def run(self):
        """运行该语句，修改 context 或造成其他副作用。绝不抛出异常。"""
        ...

    # -------------------------------------------------------------------------
    # 辅助方法
    # -------------------------------------------------------------------------

    def _variable_value_string(self, var_name: str) -> str:
        """返回 '{变量名} = {类型标签} {字面量}'，通过查询 context 获取当前值。"""
        if self._context.has_variable(var_name):
            var = self._context.get_variable(var_name)
            label = _VALUE_TYPE_LABELS.get(var.value.type, "")
            literal = var.value.to_literal_string()
            if var.value.type == ValueType.NONE:
                return f"{var_name} = 无"
            return f"{var_name} = {literal} {label}也"
        return f"{var_name} = 无"

    @staticmethod
    def _describe_expression(expr: ValueExpression) -> str:
        """返回 ValueExpression 的可读字符串表示。"""
        if isinstance(expr, VariableExpression):
            return expr.variable_name
        elif isinstance(expr, ListIndexExpression):
            return f"{expr.variable_name}之{format_chinese_integer(expr.index)}"
        return str(expr)


# =============================================================================
# 1. VariableDefinitionStatement — 变量定义
# =============================================================================


class VariableDefinitionStatement(Statement):
    """变量定义语句。

    定义新变量并初始化为指定的类型和值。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 variable_name: str, value: Value):
        super().__init__(statement_info, context)
        self._variable_name = variable_name
        self._value = value
        self._name = "变量定义"
        self._register_detail("变量名", variable_name)
        self._register_detail("类型", _VALUE_TYPE_NAMES[value.type])
        self._register_detail("初始值", value.to_literal_string())

    def run(self):
        self._context.set_variable(self._variable_name, self._value)

    def describe(self) -> tuple[str, str]:
        desc = f"定义{self._variable_name}为{self._value.to_literal_string()}"
        change = self._variable_value_string(self._variable_name)
        return desc, change


# =============================================================================
# 2. AssignmentStatement — 赋值
# =============================================================================


class AssignmentStatement(Statement):
    """赋值语句。

    将右侧值返回表达式的值赋给左侧变量。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str, source: ValueExpression):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._source = source
        self._name = "赋值"
        self._register_detail("目标变量", target_variable_name)
        self._register_detail("来源", self._describe_expression(source))

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

        # 列表赋值需要深拷贝
        if source_value.type in (
                ValueType.STRING_LIST, ValueType.INTEGER_LIST,
                ValueType.FLOAT_LIST, ValueType.BOOLEAN_LIST,
        ):
            raw = copy.deepcopy(raw)

        new_value = Value(source_value.type, raw)
        target_var.set_value(new_value)

    def describe(self) -> tuple[str, str]:
        source_desc = self._describe_expression(self._source)
        desc = f"{self._target_variable_name}取{source_desc}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 3. ComputeAssignmentStatement — 计算赋值
# =============================================================================


class ComputeAssignmentStatement(Statement):
    """计算赋值语句。

    对变量执行 Python 运算，再将结果通过类型转换回原类型后赋回原变量。
    若运算不支持或过程中出现任何错误，将目标变量置为 None。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str, operator: ComputeOperator,
                 source: ValueExpression):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._operator = operator
        self._source = source
        self._name = "计算赋值"
        self._register_detail("目标变量", target_variable_name)
        self._register_detail("运算符", _COMPUTE_OPERATOR_NAMES[operator])
        self._register_detail("来源", self._describe_expression(source))

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

        # 执行 Python 运算，捕获运行时异常（如除零、类型不兼容等）
        # noinspection broad-exception
        try:
            raw_result = self._compute(lhs.raw, rhs.raw, lhs.type)
        except Exception:
            self._context.set_to_none(self._target_variable_name)
            return

        if raw_result is _UNSUPPORTED:
            self._context.set_to_none(self._target_variable_name)
            return

        # 将运算结果通过类型转换回原类型
        # noinspection broad-exception
        try:
            converted = self._convert_to_type(raw_result, lhs.type)
            new_value = Value(lhs.type, converted)
        except Exception:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.set_value(new_value)

    @staticmethod
    def _convert_to_type(raw, value_type: ValueType):
        """将 Python 运算的中间结果转换回目标类型。"""
        if value_type == ValueType.INTEGER:
            return int(raw)
        elif value_type == ValueType.FLOAT:
            return float(raw)
        elif value_type == ValueType.BOOLEAN:
            return bool(raw)
        elif value_type == ValueType.STRING:
            return str(raw)
        else:
            # 列表等复合类型，raw 已是正确的 Python 对象
            return raw

    def _compute(self, lhs_raw, rhs_raw, value_type: ValueType):
        """执行纯 Python 运算并返回中间结果。

        若该类型不支持此运算，返回 _UNSUPPORTED。
        此方法不进行类型转换——类型转换由 _convert_to_type 负责。
        """
        op = self._operator

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
        else:
            return _UNSUPPORTED

    def describe(self) -> tuple[str, str]:
        op_name = _COMPUTE_OPERATOR_NAMES[self._operator]
        source_desc = self._describe_expression(self._source)
        desc = f"{self._target_variable_name}{op_name}{source_desc}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 4. ZeroCheckStatement — 判零
# =============================================================================


class ZeroCheckStatement(Statement):
    """判零语句。

    判断变量是否为"零"，将布尔结果赋回原变量。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._name = "判零"
        self._register_detail("目标变量", target_variable_name)

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        result = is_zero(target_var.value)
        target_var.set_value(Value(ValueType.BOOLEAN, result))

    def describe(self) -> tuple[str, str]:
        desc = f"判零{self._target_variable_name}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 5. PositiveCheckStatement — 判正
# =============================================================================


class PositiveCheckStatement(Statement):
    """判正语句。

    判断变量是否为"正"，将布尔结果赋回原变量。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._name = "判正"
        self._register_detail("目标变量", target_variable_name)

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        result = is_positive(target_var.value)
        target_var.set_value(Value(ValueType.BOOLEAN, result))

    def describe(self) -> tuple[str, str]:
        desc = f"判正{self._target_variable_name}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 6. ListIndexModifyStatement — 列表索引修改
# =============================================================================


class ListIndexModifyStatement(Statement):
    """列表索引修改语句。

    修改列表指定位置（1-based）的元素。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str, index: int,
                 source: ValueExpression):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._index = index  # 1-based
        self._source = source
        self._name = "列表索引修改"
        self._register_detail("目标变量", target_variable_name)
        self._register_detail("索引", format_chinese_integer(index))
        self._register_detail("新值", self._describe_expression(source))

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

    def describe(self) -> tuple[str, str]:
        source_desc = self._describe_expression(self._source)
        desc = f"{self._target_variable_name}之{format_chinese_integer(self._index)}改为{source_desc}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 7. ListAppendStatement — 列表追加
# =============================================================================


class ListAppendStatement(Statement):
    """列表追加语句。

    向列表末尾追加新元素。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str, source: ValueExpression):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._source = source
        self._name = "列表追加"
        self._register_detail("目标列表", target_variable_name)
        self._register_detail("追加值", self._describe_expression(source))

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

    def describe(self) -> tuple[str, str]:
        source_desc = self._describe_expression(self._source)
        desc = f"{self._target_variable_name}追加{source_desc}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 8. ListPopTailStatement — 删除尾部元素
# =============================================================================


class ListPopTailStatement(Statement):
    """列表删尾语句。

    删除列表的最后一个元素。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._name = "列表删尾"
        self._register_detail("目标列表", target_variable_name)

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        if not target_var.value.raw:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.value.raw.pop()

    def describe(self) -> tuple[str, str]:
        desc = f"{self._target_variable_name}删尾"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 9. ListPopHeadStatement — 删除头部元素
# =============================================================================


class ListPopHeadStatement(Statement):
    """列表删头语句。

    删除列表的第一个元素。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._name = "列表删头"
        self._register_detail("目标列表", target_variable_name)

    def run(self):
        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        target_var = self._context.get_variable(self._target_variable_name)
        if not target_var.value.raw:
            self._context.set_to_none(self._target_variable_name)
            return

        target_var.value.raw.pop(0)

    def describe(self) -> tuple[str, str]:
        desc = f"{self._target_variable_name}删头"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 10. FunctionCallStatement — 函数调用
# =============================================================================


class FunctionCallStatement(Statement):
    """函数调用语句。

    调用指定名称的函数。每次调用创建新的 Function 实例，
    以全局 Context 为 external_context，保证独立的局部作用域。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 function_name: str):
        super().__init__(statement_info, context)
        self._function_name = function_name
        self._name = "函数调用"
        self._register_detail("函数名", function_name)

    def run(self) -> str | None:
        """返回需要调用的函数名，由上层 Function.execute() 负责实际调用。"""
        return self._function_name

    def describe(self) -> tuple[str, str]:
        desc = f"调用函数《{self._function_name}》"
        return desc, ""


# =============================================================================
# 11. IfStatement — 条件控制流
# =============================================================================


class IfStatement(Statement):
    """If 条件语句。

    若条件变量为 True，则调用指定函数；否则跳过。
    函数调用时创建新的 Function 实例，以全局 Context 为 external_context。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 condition_variable_name: str, function_name: str):
        super().__init__(statement_info, context)
        self._condition_variable_name = condition_variable_name
        self._function_name = function_name
        self._name = "条件判断"
        self._register_detail("条件变量", condition_variable_name)
        self._register_detail("调用的函数", function_name)
        self._will_call: bool = False

    def run(self) -> str | None:
        """若条件为真则返回需要调用的函数名，否则返回 None。

        由上层 Function.execute() 负责实际调用。
        """
        if not self._context.has_variable(self._condition_variable_name):
            self._will_call = False
            return None

        cond_var = self._context.get_variable(self._condition_variable_name)
        if cond_var.value.type != ValueType.BOOLEAN:
            self._will_call = False
            return None

        if cond_var.value.raw:
            self._will_call = True
            return self._function_name
        self._will_call = False
        return None

    def describe(self) -> tuple[str, str]:
        desc = f"若{self._condition_variable_name}则调用《{self._function_name}》"
        if self._will_call:
            change = f"将调用《{self._function_name}》"
        else:
            change = "跳过"
        return desc, change


# =============================================================================
# 12. OutputStatement — 输出
# =============================================================================


class OutputStatement(Statement):
    """输出语句。

    将变量的值展示于外界。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._name = "输出"
        self._register_detail("输出变量", target_variable_name)

    def run(self):
        from zhuziyayan.program_system.program import Program

        if not self._context.has_variable(self._target_variable_name):
            return

        program = Program.get_running()
        if program is None:
            raise RuntimeError("Program 实例不存在，无法执行输出语句")

        target_var = self._context.get_variable(self._target_variable_name)
        program.get_io_strategy().write_output(target_var.value.to_literal_string())

    def describe(self) -> tuple[str, str]:
        desc = f"输出{self._target_variable_name}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 13. InputStatement — 输入
# =============================================================================


class InputStatement(Statement):
    """输入语句。

    从外界读取一行数据，尽量保持变量原有类型。

    根据变量当前类型对输入文本进行解析：

    - INTEGER：全字匹配非负整数字面量，成功则更新值，失败则置 None。
    - FLOAT：全字匹配非负浮点数字面量，成功则更新值，失败则置 None。
    - BOOLEAN：全字匹配单个布尔字面量字符，成功则更新值，失败则置 None。
    - STRING / NONE：原样存入字符串。
    - 列表类型：无法输入，置 None。

    支持可选的提示字符串（问/询/质 关键字后可接字符串字面量）。
    """

    def __init__(self, statement_info: StatementInfo, context: Context,
                 target_variable_name: str, prompt: str | None = None):
        super().__init__(statement_info, context)
        self._target_variable_name = target_variable_name
        self._prompt = prompt
        self._name = "输入"
        self._register_detail("输入变量", target_variable_name)
        if prompt is not None:
            self._register_detail("提示", prompt)

    def run(self):
        from zhuziyayan.program_system.program import Program

        if not self._context.has_variable(self._target_variable_name):
            self._context.set_to_none(self._target_variable_name)
            return

        program = Program.get_running()
        if program is None:
            raise RuntimeError("Program 实例不存在，无法执行输入语句")

        raw = program.get_io_strategy().read_input(self._prompt)
        target_var = self._context.get_variable(self._target_variable_name)
        existing_type = target_var.value.type

        if existing_type == ValueType.INTEGER:
            parsed = try_parse_integer_input(raw)
            if parsed is not None:
                target_var.set_value(Value(ValueType.INTEGER, parsed))
            else:
                target_var.set_value(Value(ValueType.NONE, None))
        elif existing_type == ValueType.FLOAT:
            parsed = try_parse_float_input(raw)
            if parsed is not None:
                target_var.set_value(Value(ValueType.FLOAT, parsed))
            else:
                target_var.set_value(Value(ValueType.NONE, None))
        elif existing_type == ValueType.BOOLEAN:
            parsed = try_parse_boolean_input(raw)
            if parsed is not None:
                target_var.set_value(Value(ValueType.BOOLEAN, parsed))
            else:
                target_var.set_value(Value(ValueType.NONE, None))
        elif existing_type == ValueType.STRING:
            target_var.set_value(Value(ValueType.STRING, try_parse_string_input(raw)))
        elif existing_type == ValueType.NONE:
            target_var.set_value(Value(ValueType.STRING, try_parse_string_input(raw)))
        else:
            # 列表类型无法输入
            target_var.set_value(Value(ValueType.NONE, None))

    def describe(self) -> tuple[str, str]:
        desc = f"输入{self._target_variable_name}"
        change = self._variable_value_string(self._target_variable_name)
        return desc, change


# =============================================================================
# 14. LiteraryStatement — 文学性语句
# =============================================================================


class LiteraryStatement(Statement):
    """文学性语句。

    无法解析出任何含义的语句，运行时不产生任何效果。
    """

    def __init__(self, statement_info: StatementInfo, context: Context):
        super().__init__(statement_info, context)
        self._name = "无操作"

    def run(self):
        pass

    def describe(self) -> tuple[str, str]:
        return "（无操作）", ""
