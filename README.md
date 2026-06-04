# 智扫通机器人智能客服 🤖

> 基于 LangChain ReAct Agent + RAG + Vue.js + FastAPI 的扫地机器人智能客服系统

---

## ⚠️ 使用必看

1. 请确保已安装 Python 3.10+ 及 Node.js 18+
2. **高德 API Key**：编辑 `config/agent.yaml`，将 `gaodekey` 替换为实际申请的高德 Web 服务 Key
3. **阿里云 API Key**：需配置环境变量 `DASHSCOPE_API_KEY`，用于通义千问大模型和 DashScope Embedding
4. **MySQL**：需本地安装 MySQL 8.0，首次启动自动建库建表

---

## 📖 项目简介

**智扫通机器人智能客服**是一款面向扫地机器人/扫拖一体机器人用户的 AI 智能体应用。系统前端采用 **Vue 3 + Vite** 构建现代化 SPA 界面，后端基于 **FastAPI** 提供 REST API 与 SSE 流式服务，核心引擎为 **LangChain ReAct Agent**，整合以下能力：

- **RAG 增强检索**：将产品手册、常见问题、维护指南等文档向量化存入 Chroma，AI 回答时优先检索知识库
- **高德地图 API**：实时获取用户定位与天气信息
- **动态提示词切换**：中间件通过识别特定意图（如生成报告），自动切换 System Prompt
- **多轮工具调用**：Agent 可自主规划并多轮调用所配备的工具
- **流式响应**：最终回答通过 SSE 逐字实时推送到前端
- **用户认证与会话管理**：JWT Token 认证，MySQL 持久化会话与消息，支持多轮对话记忆
- **角色分离**：普通用户与管理员分离登录，管理员拥有独立后台
- **知识库可视化管理**：管理员可在线查看、上传、删除知识库文档，MD5 自动去重

---

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| **LLM** | 阿里云通义千问 `qwen3-max`（通过 `ChatTongyi`） |
| **Embedding** | 阿里云 DashScope `text-embedding-v4` |
| **向量数据库** | Chroma（本地持久化） |
| **Agent 框架** | LangChain ReAct Agent + LangGraph + 中间件 |
| **后端** | FastAPI + SSE 流式 + 多线程桥接 |
| **前端** | Vue 3 + Vite + Vue Router（无 UI 框架，纯 CSS） |
| **数据库** | MySQL 8.0（用户 / 会话 / 消息 / 管理员表） |
| **认证** | Token 认证 + 角色权限控制（普通用户 / 管理员） |
| **外部服务** | 高德地图 REST API（天气、IP 定位） |
| **动态提示词** | 中间件根据上下文信号量自动切换 System Prompt |
| **去重机制** | 文档 MD5 哈希 + 上传时前端提示重复文件 |
| **日志** | 按天分文件，同时输出到控制台与文件 |

---

## 🏗 系统架构

```
┌──────────────────────────────────────────────────────────┐
│               Vue 3 SPA 前端 (frontend/)                  │
│  ┌──────────┐  ┌──────────────────────────────────────┐  │
│  │ 登录页    │  │  聊天页 (/chat)                       │  │
│  │ 角色选择  │  │  ├─ 侧边栏（会话列表）                 │  │
│  │ 普通/管理 │  │  ├─ 聊天气泡（流式渲染）               │  │
│  └──────────┘  │  └─ 输入框（Enter 发送）               │  │
│                │  管理员后台 (/admin)                    │  │
│                │  ├─ 用户数据统计                        │  │
│                │  └─ 知识库管理（查看/上传/删除）         │  │
│                └──────────────────────────────────────┘  │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP + SSE
┌──────────────────────▼───────────────────────────────────┐
│            FastAPI 后端 (backend/)                        │
│  ┌────────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │ auth.py    │  │ server.py│  │ admin.py             │ │
│  │ 登录/注册  │  │ SSE 聊天 │  │ 用户数据 + 知识库管理 │ │
│  │ Token 认证 │  │ 会话管理 │  │ MD5 去重 + 内容查看   │ │
│  └─────┬──────┘  └────┬─────┘  └──────────┬───────────┘ │
│        │              │                    │             │
│        ▼              ▼                    ▼             │
│  ┌──────────────────────────────────────────────────┐   │
│  │              MySQL 8.0 (database.py)              │   │
│  │  users │ admins │ auth_tokens │ sessions │ messages│   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│        ReAct Agent (agent/react_agent.py)                 │
│  ┌──────────────────────────────────────────────────┐   │
│  │  中间件层 (middleware.py)                         │   │
│  │  ├─ monitor_tool    工具调用监控                  │   │
│  │  ├─ log_before_model  模型调用前日志              │   │
│  │  └─ report_prompt_switch  动态提示词切换          │   │
│  └──────────────────────────────────────────────────┘   │
│  工具集：get_weather / get_user_location / rag_summarize  │
│         get_user_id / get_current_month / fetch_external  │
│         fill_context_for_report                          │
└──┬──────────────┬──────────────┬─────────────────────────┘
   │              │              │
   ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────────────┐
│ RAG 服务 │ │ 高德 API │ │  外部 CSV 数据   │
│ ChromaDB │ │ 天气/定位 │ │ data/external/   │
└──────────┘ └──────────┘ └──────────────────┘
```

---

## 👥 用户角色体系

系统将用户分为两类，采用**分表认证**，权限完全隔离：

### 普通用户

| 项目 | 说明 |
|------|------|
| **数据表** | `users`（ID 从 1001 起） |
| **预置账号** | `user1001` ~ `user1010`，密码 `123456` |
| **权限** | 登录后进入聊天页面，可使用 AI 客服所有功能 |
| **特性** | 每个用户拥有独立会话列表，历史消息持久化，Agent 自动获取当前用户 ID |

### 管理员

| 项目 | 说明 |
|------|------|
| **数据表** | `admins`（独立于 users 表） |
| **预置账号** | `admin`，密码 `admin123` |
| **权限** | 登录后进入管理后台，拥有以下功能： |
|  | 👥 **用户数据**：查看用户统计（总数/会话数/消息数）+ 用户聊天记录 + CSV 使用数据 |
|  | 📚 **知识库管理**：查看文档列表 + 在线查看内容 + 上传文档（MD5 自动去重） + 删除文档 + 重新加载向量库 |

### 登录页角色选择

登录页提供角色切换按钮：
- 选择「👤 普通用户」→ 登录后跳转 `/chat` 聊天页
- 选择「⚙️ 管理员」→ 登录后跳转 `/admin` 管理后台

路由守卫确保未授权用户无法访问对方页面。

---

## 📂 目录结构

```
agent_prac/
├── app.py                          # Streamlit 前端入口（保留，可独立运行）
├── backend/                        # FastAPI 后端
│   ├── server.py                   # 主应用：SSE 流式聊天 + 路由挂载
│   ├── auth.py                     # 认证路由（注册/登录/Token 验证/权限）
│   ├── admin.py                    # 管理员后台 API（用户数据 + 知识库管理）
│   ├── database.py                 # MySQL 连接池 + 完整 CRUD
│   └── __init__.py
├── agent/                          # Agent 核心
│   ├── react_agent.py              # ReAct Agent（含 user_id 注入 + 线程安全）
│   └── tools/
│       ├── agent_tools.py          # 7 个工具函数 + 高德 API + 线程局部变量
│       └── middleware.py           # 3 个中间件（监控/日志/提示词切换）
├── rag/                            # RAG 检索增强
│   ├── rag_summarize.py            # RAG 检索摘要服务
│   └── vector_store.py             # Chroma 向量库管理
├── model/
│   └── factory.py                  # 模型工厂（LLM + Embedding）
├── utils/
│   ├── config_handler.py           # YAML 配置加载器
│   ├── logger_handler.py           # 日志工具
│   ├── prompt_loader.py            # 提示词加载器
│   ├── file_handler.py             # 文档加载（PDF/TXT）
│   └── path_tools.py               # 路径工具
├── config/
│   ├── agent.yaml                  # Agent 配置（高德 API Key + 外部数据路径）
│   ├── rag.yaml                    # LLM / Embedding 模型名称
│   ├── chroma.yaml                 # 向量库配置（chunk_size/k/data_path 等）
│   └── prompts.yaml                # 提示词文件路径
├── prompts/
│   ├── main_prompt.txt             # 主 ReAct 提示词
│   ├── rag_summarize.txt           # RAG 摘要提示词
│   └── report_prompt.txt           # 报告生成提示词
├── frontend/                       # Vue 3 + Vite 前端
│   ├── index.html                  # HTML 入口
│   ├── vite.config.js              # Vite 配置（含 /api 代理到 :8000）
│   ├── package.json
│   └── src/
│       ├── main.js                 # Vue 应用入口（注册 Router）
│       ├── App.vue                 # 根组件（RouterView）
│       ├── assets/main.css         # 全局样式
│       ├── router/index.js         # Vue Router（/login /chat /admin）
│       ├── composables/
│       │   ├── useAuth.js          # 认证状态（Token/Role/登录/登出）
│       │   └── useChat.js          # 聊天逻辑（SSE 解析/会话管理/流式渲染）
│       ├── views/
│       │   ├── LoginView.vue       # 登录/注册页（含角色选择）
│       │   ├── ChatView.vue        # 聊天主视图（侧边栏 + 对话区）
│       │   └── AdminView.vue       # 管理员后台（用户数据 + 知识库管理）
│       └── components/
│           ├── Sidebar.vue         # 会话列表侧边栏
│           ├── ChatArea.vue        # 聊天区域容器
│           ├── ChatMessage.vue     # 单条消息气泡
│           └── ChatInput.vue       # 输入框组件
├── data/
│   ├── 扫地机器人100问.pdf
│   ├── 扫地机器人100问2.txt
│   ├── 扫拖一体机器人100问.txt
│   ├── 故障排除.txt
│   ├── 维护保养.txt
│   ├── 选购指南.txt
│   └── external/
│       └── records.csv              # 用户使用记录（外部数据，1001~1010）
├── chroma_db/                       # Chroma 持久化目录（自动生成）
├── logs/                            # 日志文件目录（自动生成）
└── md5.text                         # 文档 MD5 去重记录
```

---

## 📦 环境依赖

### Python（3.10+）

| 包名 | 用途 |
|------|------|
| `fastapi` | 后端 Web 框架 |
| `uvicorn` | ASGI 服务器 |
| `pymysql` | MySQL 数据库驱动 |
| `langchain` / `langchain-core` / `langchain-community` | Agent / Tool 框架 |
| `langgraph` | 基于图的 Agent 执行引擎 |
| `langchain-chroma` | Chroma 向量库集成 |
| `chromadb` | Chroma 向量数据库 |
| `dashscope` | 阿里云 DashScope SDK |
| `pypdf` | PDF 文档加载 |
| `pyyaml` | YAML 配置解析 |

安装：
```bash
pip install fastapi uvicorn pymysql langchain langchain-core langchain-community langgraph langchain-chroma chromadb dashscope pypdf pyyaml
```

### 前端（Node.js 18+）

```bash
cd frontend
npm install
```

---

## ⚙️ 配置说明

### 1. 阿里云 API Key

设置系统环境变量：

```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
```

> 可在 [阿里云百炼平台](https://bailian.console.aliyun.com/) 获取 API Key。

### 2. 高德地图 API Key

编辑 `config/agent.yaml`：

```yaml
gaodekey: 你的高德Web服务Key        # ← 替换这里
gaode_base_url: https://restapi.amap.com
gaode_timeout: 5
```

> 可在 [高德开放平台](https://console.amap.com/) 申请 Web 服务类型的 API Key。

### 3. 模型配置

编辑 `config/rag.yaml`：

```yaml
chat_model_name: qwen3-max
embedding_model_name: text-embedding-v4
```

### 4. 向量库配置

编辑 `config/chroma.yaml`：

```yaml
collection_name: agent
persist_directory: chroma_db
k: 3                     # 检索返回的最相关文档数
data_path: data           # 知识库文件目录
md5_hex_store: md5.text   # MD5 去重记录文件
allow_knowledge_file_type: ["txt", "pdf"]
chunk_size: 200
chunk_overlap: 20
```

### 5. MySQL 配置

编辑 `backend/database.py` 中的 `DB_CONFIG`（默认无需修改）：

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "agent_rag",
    "charset": "utf8mb4",
}
```

---

## 🚀 快速开始

### 1. 启动 MySQL

确保本地 MySQL 8.0 服务已启动。

### 2. 启动后端

```bash
cd agent_prac
uvicorn backend.server:app --reload --port 8000
```

后端启动后访问 `http://localhost:8000/docs` 可查看 Swagger API 文档。

### 3. 启动前端

```bash
cd agent_prac/frontend
npm install    # 首次运行
npm run dev
```

浏览器打开 `http://localhost:5173`，自动跳转登录页。

### 4. 登录

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 普通用户 | `user1001` ~ `user1010` | `123456` |
| 管理员 | `admin` | `admin123` |

---

## 💬 使用方式

### 普通用户 —— AI 客服聊天

登录后进入聊天页面，可以：

**产品咨询**（RAG 检索知识库）：
```
扫地机器人的滤网多久需要更换一次？
扫拖一体机器人和扫地机器人有什么区别？
```

**天气与定位查询**（高德 API）：
```
我现在所在城市今天的天气怎么样？
```

**使用报告生成**（自动切换报告提示词 + 外部数据）：
```
帮我生成我的使用报告
```
> Agent 自动获取当前登录用户的 ID，无需手动提供

**连续对话记忆**：
```
用户：小户型适合什么扫地机器人？
AI：建议选择轻便灵活的机型...
用户：那你推荐哪个具体的品牌？
AI：根据您的小户型需求，推荐米家1C...（记住了上一轮的上下文）
```

### 管理员 —— 管理后台

登录时选择「⚙️ 管理员」，进入后台：

**👥 用户数据 Tab**：
- 统计卡片：总用户数 / 总会话数 / 总消息数
- 用户列表：每个用户的会话数、消息数、CSV 使用数据
- 点击「查看聊天」可查看用户最近的聊天记录

**📚 知识库管理 Tab**：
- 文件列表：显示文件名、大小、MD5 哈希
- 查看内容：点击「查看」弹出模态框，展示 TXT 文件完整内容
- 上传文档：支持 PDF / TXT，自动 MD5 去重，重复内容显示黄色提示
- 删除文档：确认后删除
- 重新加载向量库：清除 MD5 缓存，下次全量重新索引

---

## 🛠 工具列表

Agent 配备了以下 7 个工具：

| 工具名 | 描述 | 数据源 |
|--------|------|--------|
| `rag_summarize` | 从向量知识库中检索参考资料 | ChromaDB |
| `get_weather` | 获取指定城市的实时天气 | 高德天气 API |
| `get_user_location` | 通过 IP 获取用户所在城市 | 高德 IP 定位 API |
| `get_user_id` | 获取当前登录用户 ID（线程安全，非随机） | Token 认证上下文 |
| `get_current_month` | 获取当前月份 | 系统时间 |
| `fetch_external_data` | 获取指定用户在指定月份的使用记录（自动使用当前用户 ID） | CSV 外部数据 |
| `fill_context_for_report` | 触发报告模式，通知中间件切换提示词 | 中间件信号 |

---

## 🔄 中间件机制

| 中间件 | 类型 | 作用 |
|--------|------|------|
| `monitor_tool` | `@wrap_tool_call` | 记录每次工具调用的名称和参数；检测 `fill_context_for_report` 调用时设置 `context["report"] = True` |
| `log_before_model` | `@before_model` | 每次模型调用前记录消息数量及最新消息内容 |
| `report_prompt_switch` | `@dynamic_prompt` | 检查 `context["report"]`，True 时切换到报告生成提示词，False 时使用主提示词 |

---

## 🔐 认证与安全

- **密码哈希**：pbkdf2_hmac（SHA-256 + 100000 次迭代 + 固定盐值）
- **Token 认证**：64 位十六进制随机 Token，存储在 `auth_tokens` 表
- **角色权限**：管理员 API 全部通过 `require_admin` 依赖校验
- **路由守卫**：前端 Vue Router `beforeEach` 校验 Token 和 Role
- **文件安全**：知识库文件操作通过 `os.path.realpath` 防路径穿越

---

## 🧠 记忆与会话管理

```
用户发消息 → 后端加载该 session 最近 20 条消息作为 Agent history
→ Agent 在上下文中理解对话历史 → 生成回答
→ 用户消息和 AI 回答分别存入 MySQL messages 表
→ 切换会话 / 新建会话 → 各自独立记忆，互不干扰
→ 重新登录 → 会话列表从 MySQL 恢复
```

---

## 📋 日志说明

日志文件存放在 `logs/` 目录下，按天自动创建：

```
logs/
└── agent_20260603.log    # 格式：{name}_{YYYYMMDD}.log
```

- **控制台**：输出 INFO 及以上级别日志
- **文件**：输出 DEBUG 及以上级别日志（更详细）

---


## 📄 许可证

本项目仅供学习与参考使用。
