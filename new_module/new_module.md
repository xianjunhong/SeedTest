# 如何新增模块

以新增小麦籽粒考种为例子

### 1.在frank/uiModule复制三个ui界面并改名字

![image-20250609110335468](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609110335468.png)![image-20250609110509581](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609110509581.png)

记得还要改class的名字，ui类中的启动类的名字

![image-20250609113439034](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609113439034.png)

![image-20250609113443745](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609113443745.png)

![image-20250609113453738](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609113453738.png)

![image-20250609113522698](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609113522698.png)

### 2在frank/fieldMoudle/all_fields新建你需要的字段，字段是否显示主页、数据管理页面、默认值你自己定义，你在处理图像以后的save_info时会用到

![image-20250609110925314](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609110925314.png)

### 3.回到uiModule把home和data的导入包中的

```python
from frank.fieldModule.all_fields import SoySeedFields as FIELDS
```

替换为

```python
from frank.fieldModule.all_fields import WheatSeedFields as FIELDS
```

4.在frank/handleModule复制一份并改名

![image-20250609111244124](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609111244124.png)

5.修改config.ini,指定图片存储的地点和模型路径，如果不是yolo训练的模型，是图像处理的就不需要指定了

![image-20250609112635682](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609112635682.png)

6修改frank/handleModule/wheat_seed里面的字段和cofig.ini字段

![image-20250609112744863](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609112744863.png)

改为![image-20250609112805241](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609112805241.png)

![image-20250609113056505](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609113056505.png)

全部替换

7在start_v2.py中注册页面

![image-20250609114747514](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609114747514.png)

![image-20250609114816285](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609114816285.png)

![image-20250609121050096](D:\GitProgress\SeedTest\new_module\new_module.assets\image-20250609121050096.png)