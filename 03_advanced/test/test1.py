class TenDescriptor:
    """一个描述符，无论访问什么属性都返回 10"""
    def __get__(self, instance, owner):
        # instance: 调用这个描述符的实例
        # owner:    实例所属的类
        print(f"  __get__(instance={instance}, owner={owner.__name__})")
        return 10

class MyClass:
    x = TenDescriptor()      # 类属性 x 是一个描述符对象！

obj = MyClass()
print("--- 非数据描述符 ---")
print(f"  obj.x = {obj.x}")  # 不是取实例属性，而是触发描述符的 __get__
print(f"  MyClass.x = {MyClass.x}")  # instance 为 None
