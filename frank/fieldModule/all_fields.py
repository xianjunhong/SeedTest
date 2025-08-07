# all_fields.py
from .field_config import FieldConfig

# 豆荚的参数
PodFields = [
    FieldConfig("id", "产品编号", str, "",False,True),
    FieldConfig("name", "名称", str, "",True,True),
    FieldConfig("width", "宽度", float, "",True,True),
    FieldConfig("height", "长度", float, "",True,True),
    FieldConfig("inner_length", "内径长度", float, "",True,True),
    FieldConfig("diameter", "内切圆直径", float, "",True,True),
    FieldConfig("lustre", "翠绿程度", float, "",True,True),
    FieldConfig("pod_count", "豆荚个数", int, "",True,True),
    FieldConfig("weight", "重量", float, "0",False,True),
    FieldConfig("create_time", "创建时间", str, "",False,True),
    # FieldConfig("test_field", "测试字段", str, "",True,True),
    FieldConfig("operator", "操作", str, "",False,True),

]

# 大豆籽粒的参数
SoySeedFields = [
    FieldConfig("id", "产品编号", str, "",False,True),
    FieldConfig("name", "名称", str, "",True,True),
    FieldConfig("num", "籽粒个数", int, "",True,True),
    FieldConfig("length", "平均长度", float, "0",True,True),
    FieldConfig("width", "平均宽度", float, "0",True,True),
    FieldConfig("weight", "总重量", float, "0",False,True),
    FieldConfig("thousand_seed_weight", "千粒重", float, "0",False,True),
    FieldConfig("create_time", "创建时间", str, "",False,True),
    # FieldConfig("test_field", "测试字段", str, "",True,True),
    FieldConfig("operator", "操作", str, "",False,True),

]


# 通用考种的参数
CountAnythingFields = [
    FieldConfig("id", "产品编号", str, "",False,True),
    FieldConfig("name", "名称", str, "",True,True),
    FieldConfig("num", "数量", int, "",True,True),
    FieldConfig("weight", "重量", float, "0",False,True),
    FieldConfig("create_time", "创建时间", str, "",False,True),
    # FieldConfig("test_field", "测试字段", str, "",True,True),
    FieldConfig("operator", "操作", str, "",False,True),

]


# 图像获取参数
ImageAcquisitionFields = [
    FieldConfig("id", "产品编号", str, "",False,True),
    FieldConfig("name", "名称", str, "",True,True),
    FieldConfig("weight", "重量", float, "0",False,True),
    FieldConfig("create_time", "创建时间", str, "",False,True),
    # FieldConfig("test_field", "测试字段", str, "",True,True),
    FieldConfig("operator", "操作", str, "",False,True),

]

# 小麦籽粒的参数
WheatSeedFields = [
    FieldConfig("id", "产品编号", str, "",False,True),
    FieldConfig("name", "名称", str, "",True,True),
    FieldConfig("num", "籽粒个数", int, "",True,True),
    FieldConfig("length", "平均长度", float, "0",True,True),
    FieldConfig("width", "平均宽度", float, "0",True,True),
    FieldConfig("weight", "总重量", float, "0",False,True),
    FieldConfig("thousand_seed_weight", "千粒重", float, "0",False,True),
    FieldConfig("create_time", "创建时间", str, "",False,True),
    # FieldConfig("test_field", "测试字段", str, "",True,True),
    FieldConfig("operator", "操作", str, "",False,True),

]
