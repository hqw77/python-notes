# ============================================================
# 08. logging 模块
# ============================================================
# 大纲：
#   - 为什么不用 print() 做日志
#   - 日志级别：DEBUG, INFO, WARNING, ERROR, CRITICAL
#   - basicConfig()：快速配置
#   - Logger 对象：getLogger(__name__)
#   - Handler：控制输出目标（StreamHandler, FileHandler, RotatingFileHandler）
#   - Formatter：控制输出格式
#   - 日志格式字符串：%(asctime)s, %(levelname)s, %(name)s, %(message)s 等
#   - 父子 Logger 的层级关系
#   - 日志不传播：propagate = False
#   - 按大小轮转：RotatingFileHandler
#   - 按时间轮转：TimedRotatingFileHandler
#   - 实战：一个完整的日志配置
#   - 第三方日志库简介（loguru）
