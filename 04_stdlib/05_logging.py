"""
logging 模块 -- 正式的日志, 不是 print

[问题场景: print 撑不住一个要跑很久的程序]

  print("开始处理")            # 没有级别, 分不清是调试信息还是错误
  print(f"耗时 {t}s")          # 没有时间戳, 看不出先后顺序
  print("出错了", e)           # 没有堆栈, 排查全靠猜
  上线后想关掉调试输出?        # 只能一行行删 print

  logging 解决的正是这四件事:
    1. 分级 (DEBUG/INFO/WARNING/ERROR/CRITICAL), 运行时按级别过滤
    2. 自动加时间, 模块名, 行号
    3. 一条配置决定输出到控制台还是文件, 还是都输出
    4. 异常有 logger.exception() 直接带完整堆栈

[核心概念]

  ┌──────────┬──────────────────────────────────────────────────┐
  │ Logger   │ 你要拿到的对象: logging.getLogger(__name__)       │
  │ Handler  │ 输出到哪里: StreamHandler / FileHandler / 轮转     │
  │ Formatter│ 一行长什么样: %(asctime)s %(levelname)s ...        │
  │ Level    │ DEBUG < INFO < WARNING < ERROR < CRITICAL         │
  └──────────┴──────────────────────────────────────────────────┘

  一条日志的流向:
      logger.info(...) -> 本 Logger 的 Handler -> 父 Logger -> ... -> root

  父子关系按名字的点号: getLogger("a.b") 的父是 getLogger("a").

[运行方式]
  全部: python 05_logging.py
  单个: python 05_logging.py why / basic / levels / logger / handlers / rotate / exception / use_cases
"""

import logging
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path


# ============================================================
# 1. 为什么不用 print
# ============================================================
def demo_why():
    print("--- 1. print 做日志的四个问题 ---")

    print("  print 输出:")
    print("    开始处理")
    print("    处理失败: division by zero")

    print("\n  logging 输出同样内容:")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        force=True,          # 清掉之前的配置, 避免重复 handler (3.8+)
        stream=sys.stdout,
    )
    logging.info("开始处理")
    logging.error("处理失败: division by zero")

    print("  → 有级别, 有时间, 有模块名, 而且能一条配置切掉 DEBUG")


# ============================================================
# 2. basicConfig 与五个级别
# ============================================================
def demo_basic():
    print("--- 2. basicConfig: 最简配置 ---")

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(message)s",
        force=True,
        stream=sys.stdout,
    )

    print("  设置 level=INFO 后, DEBUG 会被过滤: ")
    logging.debug("这条 DEBUG 看不到")
    logging.info("这条 INFO 能看到")
    logging.warning("这条 WARNING 能看到")
    logging.error("这条 ERROR 能看到")

    print("\n  级别数字 (自定义级别时用得上): ")
    for name in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        print(f"    {name:<9} = {logging.getLevelName(name)}")
    print(f"    WARNING 是默认级别, 不配置只会输出 WARNING 及以上")


# ============================================================
# 3. Level 的过滤发生在哪里
# ============================================================
def demo_levels():
    print("--- 3. 级别过滤: logger 和 handler 各管一道 ---")

    logger = logging.getLogger("demo.levels")
    logger.setLevel(logging.DEBUG)        # logger 自己放开到 DEBUG
    logger.propagate = False
    for h in list(logger.handlers):
        logger.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)     # 但 handler 只放 WARNING 及以上
    handler.setFormatter(logging.Formatter("    [handler] %(levelname)s %(message)s"))
    logger.addHandler(handler)

    print("  logger=DEBUG, handler=WARNING: ")
    logger.debug("DEBUG 被 handler 拦下")
    logger.info("INFO 被 handler 拦下")
    logger.warning("WARNING 通过")
    logger.error("ERROR 通过")

    print(f"  logger.isEnabledFor(DEBUG) = {logger.isEnabledFor(logging.DEBUG)}")
    print("  → 生产环境常用: logger 开 DEBUG, 控制台 handler 只放 INFO, 文件放 DEBUG")

    logger.removeHandler(handler)
    handler.close()


# ============================================================
# 4. Logger 的层级与传播
# ============================================================
def demo_logger():
    print("--- 4. getLogger(__name__) 与父子传播 ---")

    logging.basicConfig(
        level=logging.INFO,
        format="%(name)-12s %(levelname)-8s %(message)s",
        force=True,
        stream=sys.stdout,
    )

    app = logging.getLogger("app")
    db = logging.getLogger("app.db")

    app.info("来自 app")
    db.info("来自 app.db")          # 自己的 handler 没有, 往上找到 app / root 的

    print(f"  app.db 的父 logger: {db.parent.name}")
    print(f"  app.db 的层级链: {[x.name for x in [db, db.parent, db.parent.parent]]}")

    # propagate=False: 不再往上传, 避免重复输出
    db.propagate = False
    db.addHandler(logging.StreamHandler(sys.stdout))
    print("  给 app.db 加了 handler 且 propagate=False: ")
    db.info("只输出一次")
    db.propagate = True
    for h in list(db.handlers):
        db.removeHandler(h)
        h.close()

    print("  → 模块里统一用 getLogger(__name__), 名字自然形成层级, 方便按包调级别")


# ============================================================
# 5. Handler + Formatter: 同时输出到控制台和文件
# ============================================================
def demo_handlers():
    print("--- 5. 控制台 + 文件, 各用各的格式 ---")

    with tempfile.TemporaryDirectory() as tmp:
        log_file = Path(tmp) / "app.log"

        logger = logging.getLogger("demo.handlers")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        for h in list(logger.handlers):
            logger.removeHandler(h)
            h.close()

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("  [控制台] %(levelname)-8s %(message)s"))

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s %(message)s")
        )

        logger.addHandler(console)
        logger.addHandler(file_handler)

        logger.debug("只进文件")
        logger.info("控制台和文件都有")
        logger.warning("控制台和文件都有")

        for h in list(logger.handlers):
            logger.removeHandler(h)
            h.close()          # 必须 close, 否则 Windows 上临时目录删不掉

        print(f"  文件里共 {len(log_file.read_text(encoding='utf-8').splitlines())} 行: ")
        for line in log_file.read_text(encoding="utf-8").splitlines():
            print(f"    {line}")


# ============================================================
# 6. 轮转: 别让日志文件涨到几个 G
# ============================================================
def demo_rotate():
    print("--- 6. RotatingFileHandler: 按大小轮转 ---")

    with tempfile.TemporaryDirectory() as tmp:
        log_file = Path(tmp) / "rotate.log"

        logger = logging.getLogger("demo.rotate")
        logger.setLevel(logging.INFO)
        logger.propagate = False
        for h in list(logger.handlers):
            logger.removeHandler(h)
            h.close()

        handler = RotatingFileHandler(
            log_file,
            maxBytes=300,        # 单文件超过 300 字节就轮转
            backupCount=2,       # 最多保留 2 个历史文件
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)

        for i in range(20):
            logger.info(f"第 {i:02d} 条日志, 这条内容会占掉一些字节")

        logger.removeHandler(handler)
        handler.close()

        files = sorted(p.name for p in Path(tmp).iterdir())
        print(f"  轮转后目录里: {files}")
        print(f"  当前 rotate.log 大小: {log_file.stat().st_size} 字节")

    print("  时间轮转用 TimedRotatingFileHandler(when='midnight', backupCount=7)")
    print("  → 线上项目必须配轮转, 不然日志能吃掉整块磁盘")


# ============================================================
# 7. 异常: logger.exception 带堆栈
# ============================================================
def demo_exception():
    print("--- 7. 记录异常: exception / error 的区别 ---")

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(message)s",
        force=True,
        stream=sys.stdout,
    )

    def divide(a, b):
        try:
            return a / b
        except ZeroDivisionError:
            logging.exception("除法失败: a=%s b=%s", a, b)   # 自动附带堆栈
            return None

    print("  logger.exception 的输出: ")
    divide(1, 0)

    print("\n  对比 logging.error (只有一行, 没有堆栈): ")
    logging.error("除法失败")

    print("  提示: 只在 except 块里用 exception(), 它等价于 error(..., exc_info=True)")


# ============================================================
# 8. 实战: 一个可以直接抄走的日志配置
# ============================================================
def demo_use_cases():
    print("--- 8. 实战: 项目里通用的一份日志配置 ---")

    def setup_logging(level=logging.INFO, file_path=None):
        """既能控制台看, 也能落盘; 返回配置好的 logger"""
        logger = logging.getLogger("myapp")
        logger.setLevel(level)
        logger.propagate = False
        for h in list(logger.handlers):
            logger.removeHandler(h)
            h.close()

        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console = logging.StreamHandler(sys.stdout)
        console.setLevel(level)
        console.setFormatter(fmt)
        logger.addHandler(console)

        if file_path:
            fh = logging.FileHandler(file_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)          # 文件记得更细
            fh.setFormatter(fmt)
            logger.addHandler(fh)

        return logger

    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "service.log"
        log = setup_logging(logging.DEBUG, log_path)

        log.debug("加载配置")
        log.info("服务启动, 端口 %s", 8000)
        log.warning("磁盘剩余 %s%%, 注意清理", 12)
        try:
            1 / 0
        except ZeroDivisionError:
            log.exception("处理请求时出错")

        for h in list(log.handlers):
            log.removeHandler(h)
            h.close()

        print(f"\n  落盘文件共 {len(log_path.read_text(encoding='utf-8').splitlines())} 行")

    print("  要点: 用 %s 占位而不是 f-string (级别不够时不浪费格式化开销)")


# ============================================================
# 入口
# ============================================================
if __name__ == "__main__":
    import sys as _sys
    demos = {
        "why": demo_why,
        "basic": demo_basic,
        "levels": demo_levels,
        "logger": demo_logger,
        "handlers": demo_handlers,
        "rotate": demo_rotate,
        "exception": demo_exception,
        "use_cases": demo_use_cases,
    }
    if len(_sys.argv) > 1:
        fn = demos.get(_sys.argv[1])
        if fn is None:
            print(f"未知案例 '{_sys.argv[1]}', 可选: {', '.join(demos)}")
            _sys.exit(1)
        fn()
    else:
        for fn in demos.values():
            fn()


# ============================================================
# 总结
# ============================================================
# 最小可用:
#   logging.basicConfig(level=logging.INFO,
#                       format="%(asctime)s %(levelname)s %(name)s: %(message)s")
#   logging.info("...")
#
# 正经项目:
#   logger = logging.getLogger(__name__)      # 名字形成层级
#   logger.addHandler(StreamHandler())        # 控制台
#   logger.addHandler(FileHandler(...))       # 落盘
#   logger.addHandler(RotatingFileHandler(maxBytes=..., backupCount=...))  # 轮转
#   handler.setFormatter(Formatter(...))
#
# 级别:
#   DEBUG (开发细节) < INFO (关键流程) < WARNING (可恢复的异常)
#   < ERROR (功能失败) < CRITICAL (程序要挂了)
#
# 三个坑:
#   1. basicConfig 只在第一次生效, 多次调用要加 force=True
#   2. handler 重复添加会重复输出, 加之前先 clear / 检查
#   3. 别用 f-string 拼日志, 用 %s 占位 (级别不满足时不执行格式化)
