"""
HTTP 基础 —— Web 开发的通用语言

【HTTP 是什么?】

  HTTP = HyperText Transfer Protocol (超文本传输协议)
  你在浏览器输入网址按回车, 浏览器就发起一个 HTTP 请求到服务器,
  服务器处理后返回 HTTP 响应.

  整个过程:
    浏览器 (客户端) ──HTTP请求──→ Web 服务器
    浏览器 (客户端) ↢──HTTP响应── Web 服务器

【请求 (Request) 的四个部分】

  1. 方法 (Method): 我要干什么?
     GET    → 读取数据 (打开网页, 查列表)
     POST   → 创建数据 (注册, 发帖)
     PUT    → 更新数据 (修改资料, 全量替换)
     PATCH  → 部分更新数据 (只改昵称)
     DELETE → 删除数据 (删帖, 注销)

  2. URL (地址): 我要找谁?
     http://example.com/api/users/5?page=1
     ├──────┘ ├───────┘ ├───────┤ ├┘ ├────┘
     协议      域名       路径     路径参数 查询参数

  3. Headers (头部): 附加信息 (格式, 认证 token, ...)

  4. Body (请求体): 要发送的数据 (POST/PUT 时用)

【响应 (Response) 的三个部分】

  1. 状态码 (Status Code): 结果怎么样?
     200 OK          → 成功
     201 Created     → 创建成功
     400 Bad Request → 你的请求有问题
     404 Not Found   → 你要的资源不存在
     500 Internal Error → 服务器炸了

  2. Headers (头部): 响应的元信息

  3. Body (响应体): 你要的数据 (HTML / JSON / 图片 ...)

【JSON —— Web 的通用数据格式】

  几乎所有现代 API 都用 JSON 传输数据:
  {
    "name": "张三",
    "age": 30,
    "skills": ["Python", "FastAPI"]
  }

  Python ↔ JSON 映射:
    dict ↔ object, list ↔ array, str ↔ string
    int/float ↔ number, bool ↔ true/false, None ↔ null

【RESTful API 设计惯例】

  GET    /api/users      → 获取用户列表
  GET    /api/users/5    → 获取 ID=5 的用户
  POST   /api/users      → 创建新用户 (数据在请求体)
  PUT    /api/users/5    → 更新 ID=5 的用户
  DELETE /api/users/5    → 删除 ID=5 的用户

  特点: URL 都是名词 (users), 操作由 Method 决定.
"""
