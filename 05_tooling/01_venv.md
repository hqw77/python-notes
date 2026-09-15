# 虚拟环境与包管理

## 为什么需要虚拟环境?

Python 项目会依赖第三方包. 不同项目可能依赖同一个包的不同版本:

```
项目A: 需要 Django 3.2
项目B: 需要 Django 5.0

如果把 Django 装到全局 → 两个项目打架, 有一个跑不了
```

**虚拟环境就是给每个项目一个独立的 Python 包空间**, 互不干扰.

打个比方:
- 全局安装 = 所有人共用一个大仓库
- 虚拟环境 = 每个项目自己有独立的小仓库

---

## 创建和使用虚拟环境

### 创建

```bash
# 在项目目录下创建名为 .venv 的虚拟环境
cd d:\python_learn
python -m venv .venv
```

这会在项目根目录生成一个 `.venv/` 文件夹, 里面有:
- 一个独立的 Python 解释器
- 一个独立的 pip
- 一个独立的 site-packages 目录 (装包的地方)

### 激活

```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# 或 (CMD)
.venv\Scripts\activate.bat

# macOS / Linux
source .venv/bin/activate
```

激活后, 终端前面会出现 `(.venv)` 标记:

```
(.venv) PS D:\python_learn>
```

现在输入 `python` 和 `pip` 用的都是虚拟环境里的了.

### 退出

```bash
deactivate
```

---

## pip 常用命令

```bash
pip install requests              # 安装一个包
pip install requests==2.28.0      # 安装指定版本
pip install "django>=4.0,<5.0"    # 安装版本范围

pip uninstall requests            # 卸载

pip list                          # 查看已安装的包
pip show requests                 # 查看某个包的详细信息

pip freeze > requirements.txt     # 导出依赖列表到文件
pip install -r requirements.txt   # 从文件安装所有依赖
```

### 版本号写法

| 写法 | 含义 |
|---|---|
| `requests==2.28.0` | 精确等于 2.28.0 |
| `requests>=2.28.0` | 大于等于 2.28.0 |
| `requests~=2.28.0` | 兼容版本: >=2.28.0, <2.29.0 |
| `requests!=2.28.0` | 不等于 2.28.0 |

---

## requirements.txt

这就是一份依赖清单, 放到 Git 里, 别人拉下来就能装一样的环境:

```
# requirements.txt
requests==2.28.0
pytest==8.0.0
```

```bash
pip install -r requirements.txt   # 一键安装所有依赖
```

---

## 切换国内镜像源 (提速)

PyPI 官方源在国外, 国内下载慢. 换清华或阿里源:

```bash
# 临时使用
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

常用国内源:

| 镜像 | 地址 |
|---|---|
| 清华 | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| 阿里 | `https://mirrors.aliyun.com/pypi/simple` |
| 中科大 | `https://pypi.mirrors.ustc.edu.cn/simple` |

---

## 给成绩系统创建虚拟环境 (动手试试)

```bash
cd d:\python_learn\projects\grade_system
python -m venv .venv                           # 创建
.\.venv\Scripts\Activate.ps1                   # 激活 (PowerShell)

# 现在安装 pytest (下一节课要用)
pip install pytest

# 导出依赖
pip freeze > requirements.txt

# 退出
deactivate
```

---

## 现代替代方案 (了解即可)

| 工具 | 特点 |
|---|---|
| **uv** | Rust 写的, pip 的 10-100 倍速度, Astral 出品 |
| **poetry** | 一站式依赖管理 + 打包 + 发布 |
| **pipenv** | 曾经的官方推荐, 现在势头被 uv 超越 |

初学阶段用 `venv + pip` 就够, 后面再换.
