# field_config.py

class FieldConfig:
    def __init__(self, name, label, dtype=str, default="", form_visible=True, table_visible=True):
        self.name = name          # 字段的变量名，比如 "width"
        self.label = label        # UI 上的显示名，比如 "宽度"
        self.dtype = dtype        # 数据类型，比如 float、str、int
        self.default = default    # 默认值
        self.form_visible = form_visible    # 是否展示在表单
        self.table_visible = table_visible    # 是否展示在表格
