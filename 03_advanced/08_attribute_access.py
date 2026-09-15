"""
属性访问控制 —— __getattr__ / __setattr__ / __getattribute__ / __delattr__

这四个方法可以拦截对象属性的读取, 设置, 删除.

【四个方法的触发时机】

  ┌───────────────────┬──────────────────────┬───────────────────────┐
  │ 方法               │ 触发时机              │ 危险性                 │
  ├───────────────────┼──────────────────────┼───────────────────────┤
  │ __getattribute__  │ 每次访问属性都调用     │ 极易无限递归! 慎用!    │
  │                   │ (无论属性是否存在)     │                       │
  ├───────────────────┼──────────────────────┼───────────────────────┤
  │ __getattr__       │ 只有正常查找失败后     │ 安全, 常用             │
  │                   │ 才调用 (兜底机制)     │                       │
  ├───────────────────┼──────────────────────┼───────────────────────┤
  │ __setattr__       │ 每次设置属性时调用     │ 容易递归, 需要防        │
  ├───────────────────┼──────────────────────┼───────────────────────┤
  │ __delattr__       │ 每次删除属性时调用     │ 相对安全               │
  └───────────────────┴──────────────────────┴───────────────────────┘

【最重要的防递归技巧】

  在 __setattr__, __getattribute__, __delattr__ 内部, 绝对不要直接写:
    self.xxx = yyy       # 会再次触发 __setattr__ → 无限递归!
    value = self.xxx     # 会再次触发 __getattribute__ → 无限递归!

  正确做法 ── 绕过拦截, 直接操作父类或 __dict__:
    object.__setattr__(self, name, value)
    object.__getattribute__(self, name)
    object.__delattr__(self, name)
    或
    self.__dict__[name] = value
    return self.__dict__[name]

  为什么 object.__setattr__ 能绕过? 因为 object (C 语言实现) 直接操作
  C 层的属性字典, 不会触发 Python 层的魔术方法.

【完整的属性查找链 —— obj.attr 时发生了什么?】

  obj.attr 的查找顺序 (类内部用 C3 线性化遍历所有父类):
    1. __getattribute__(obj, "attr") 无条件触发
    2. 在 obj.__dict__ 里找 "attr"
    3. 在 type(obj).__dict__ 以及所有父类的 __dict__ 里找
    4. 如果找到了且是数据描述符 → 返回描述符的 __get__ 结果
    5. 如果找到了且不是描述符 → 返回该值
    6. 如果都找不到 → 调用 __getattr__(obj, "attr")
    7. 如果连 __getattr__ 都没定义 → 抛出 AttributeError

  这也是为什么 __getattr__ 被称为"兜底" ── 它只在最后被调用.

【典型应用场景】

  __getattr__:
    - 代理模式: 把不存在的方法调用转发给内部对象
    - 动态属性: 根据名称动态生成属性值
    - API 包装: 把远程 API 伪装成本地对象

  __setattr__:
    - 属性验证: 赋值时检查类型和值
    - 访问日志: 记录所有属性的变化
    - 不可变对象: 创建后禁止修改

  __delattr__:
    - 属性保护: 阻止删除关键属性
    - 清理逻辑: 删除时做额外的资源释放

  __getattribute__:
    - 极少数场景, 如 ORM 的懒加载, 属性访问审计
    - 90% 的情况应该用 __getattr__ 代替
"""

# ============================================================
# 1. __getattr__ —— 属性不存在时才触发
# ============================================================
class DynamicAttributes:
    """对不存在的属性返回默认值，而不是抛 AttributeError"""
    def __init__(self):
        self.existing = "我有这个属性"

    def __getattr__(self, name):
        """只有正常查找失败时才会调用这个方法"""
        print(f"  __getattr__ 被调用: 属性 '{name}' 不存在")
        return f"动态生成的 '{name}' 值"

obj = DynamicAttributes()
print("--- __getattr__: 属性不存在时触发 ---")
print(f"  obj.existing = {obj.existing}")    # 正常访问，不触发 __getattr__
print(f"  obj.missing = {obj.missing}")      # 属性不存在，触发 __getattr__
print(f"  obj.anything = {obj.anything}")     # 同样触发


# ============================================================
# 2. __getattr__ 实用案例：代理 / 包装器
# ============================================================
class Proxy:
    """将不存在的方法调用转发到内部对象"""
    def __init__(self, target):
        self._target = target

    def __getattr__(self, name):
        """把对 Proxy 的调用转发给 _target"""
        print(f"  转发: {name} -> _target")
        return getattr(self._target, name)     # 从 _target 上取

print("\n--- __getattr__: 代理模式 ---")
plist = Proxy([1, 2, 3])
print(f"  plist.append(4): {plist.append(4)}")
print(f"  plist.__class__: {plist.__class__}")     # 不会拦截 __class__，因为实际存在
print(f"  plist._target: {plist._target}")          # 不会拦截 _target


# ============================================================
# 3. __setattr__ —— 每次设置属性都触发
# ============================================================
class GuardedObject:
    """记录所有属性的设置操作"""
    def __init__(self, name):
        # 这里必须用 object.__setattr__ 或 self.__dict__，否则无限递归！
        object.__setattr__(self, "_log", [])
        self.name = name                   # 这会触发 __setattr__

    def __setattr__(self, name, value):
        """拦截所有 self.xxx = yyy 操作"""
        log = object.__getattribute__(self, "_log")   # 绕过 __getattribute__
        log.append(f"设置 {name} = {value!r}")
        # 安全地设置属性 —— 用父类的 __setattr__
        object.__setattr__(self, name, value)

    def show_log(self):
        for entry in self._log:
            print(f"  {entry}")

print("\n--- __setattr__: 拦截属性设置 ---")
g = GuardedObject("初始值")
g.age = 30
g.name = "新名字"
g.show_log()


# ============================================================
# 4. __delattr__ —— 每次删除属性时触发
# ============================================================
class Protected:
    """阻止删除特定属性"""
    def __init__(self):
        self.normal = "可以删"
        self.protected = "不能删"

    def __delattr__(self, name):
        if name == "protected":
            print(f"  __delattr__: 禁止删除 '{name}' ")
            return
        # 安全地删除属性
        object.__delattr__(self, name)
        print(f"  已删除: '{name}'")

print("\n--- __delattr__: 拦截属性删除 ---")
p = Protected()
del p.normal
print(f"  p.normal 还在吗: {hasattr(p, 'normal')}")   # False
del p.protected                                       # 被拦截
print(f"  p.protected 还在吗: {hasattr(p, 'protected')}")  # True


# ============================================================
# 5. __getattribute__ —— 危险！每次访问属性都触发
# ============================================================
class LogAccess:
    """记录所有属性访问（包括存在的属性）"""
    def __init__(self):
        object.__setattr__(self, "_access_log", [])

    def __getattribute__(self, name):
        """每次访问任何属性都会触发 —— 极易无限递归！"""
        # 绝对不能写 self._access_log ！！！会无限递归！！！
        log = object.__getattribute__(self, "_access_log")
        if not name.startswith("_"):
            log.append(f"访问了 {name}")
        return object.__getattribute__(self, name)

print("\n--- __getattribute__: 拦截所有访问 ---")
la = LogAccess()
la.x = 10
print(f"  la.x = {la.x}")
print(f"  la.x = {la.x}")
print(f"  访问日志: {la._access_log}")


# ============================================================
# 6. 四者调用顺序总结
# ============================================================
print("\n--- 调用顺序演示 ---")

class FullControl:
    def __init__(self):
        object.__setattr__(self, "_data", {})
        self.existing = "已有的属性"   # 触发 __setattr__

    def __getattribute__(self, name):
        print(f"    1. __getattribute__('{name}') — 每次都触发")
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            pass
        # 找不到时，继续往下走……
        # Python 会自动调用 __getattr__

    def __getattr__(self, name):
        print(f"    2. __getattr__('{name}') — 没找到才触发")
        return f"默认值 for '{name}'"

    def __setattr__(self, name, value):
        print(f"    __setattr__('{name}', {value!r})")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        print(f"    __delattr__('{name}')")
        object.__delattr__(self, name)

fc = FullControl()
print("\n  访问存在的属性:")
_ = fc.existing
print("\n  访问不存在的属性:")
_ = fc.missing
print("\n  设置属性:")
fc.new_attr = 100
print("\n  删除属性:")
del fc.new_attr


# ============================================================
# 总结
# ============================================================
# 触发时机:
#   __getattribute__ : 每次访问属性（无论存在与否）— 慎用！
#   __getattr__      : 正常查找失败后调用 — 安全，常用
#   __setattr__      : 每次设置属性时调用
#   __delattr__      : 每次删除属性时调用
#
# 防递归方法: 在 __setattr__/__getattribute__/__delattr__ 内部
#   用 object.__setattr__(self, name, value) 代替 self.xxx
#   用 self.__dict__[name] = value 也可以
#
# 使用场景:
#   __getattr__ → 代理模式、动态属性、API 包装
#   __setattr__ → 属性验证、访问日志、不可变对象
#   __delattr__ → 属性保护、清理逻辑
