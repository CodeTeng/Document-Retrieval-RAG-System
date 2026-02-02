# 🧠 RAG Backend Service

基于 FastAPI 和 LangChain 构建的智能文档检索与问答后端服务。

## ✨ 特性

- 📄 **文档管理**：支持多格式文档上传（PDF, Word, Markdown, TXT）与解析
- 🔍 **混合检索**：结合向量检索（Faiss）与关键词匹配
- 🤖 **智能问答**：基于通义千问（Qwen）大模型的流式问答
- ⚡ **高性能**：基于 FastAPI 的异步架构

## 🛠️ 技术栈

- **Python**: 3.10+
- **Web Framework**: FastAPI
- **LLM Orchestration**: LangChain
- **Vector DB**: Faiss
- **Model Provider**: Aliyun DashScope (通义千问)
- **Package Manager**: uv

## 🚀 快速开始

### 1. 环境准备

确保已安装 Python 3.10+ 和 [uv](https://github.com/astral-sh/uv) 包管理器。

### 2. 配置环境变量

在 `rag-backend` 目录下创建 `.env` 文件：

```env
# Aliyun DashScope API Key
DASHSCOPE_API_KEY=your_api_key_here
```

### 3. 安装依赖

```bash
uv sync
```

或者使用 pip:

```bash
pip install -r requirements.txt
```

### 4. 启动服务

```bash
# 使用 uv 启动（推荐）
uv run start.py

# 或者直接运行
python app/main.py
```

服务将启动在 `http://localhost:8000`。
API 文档地址：`http://localhost:8000/docs`

## 📂 目录结构

```
rag-backend/
├── app/
│   ├── api/          # API 路由
│   ├── core/         # 核心配置
│   ├── schemas/      # Pydantic 模型
│   ├── services/     # 业务逻辑
│   └── main.py       # 入口文件
├── config/           # 配置文件
├── data/             # 数据存储（向量库/文档）
└── start.py          # 启动脚本
```
