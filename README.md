# GEO 内容营销自动化系统

通过持续生产和分发高质量内容，提高企业品牌在 AI 搜索结果中的出现概率。

## 功能概览

当前已实现（v0.1）：

- 用户注册登录与角色权限管理（admin / operator / enterprise）
- 核心主词管理 + AI 拓展词生成（关键词树）
- 企业资料库（支持 Word、PDF 上传与文本提取）
- 图片素材库（分类管理、关联主词）
- AI 指令规则配置（标题模板 + 内容模板）
- 手动生成文章（调用 AI 接口生成）

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11 / FastAPI / SQLAlchemy 2.0 (async) |
| 前端 | Vue 3 + TypeScript / Element Plus / Vite |
| 数据库 | SQL Server 2022 |
| 认证 | JWT (python-jose) |
| AI 接口 | OpenAI 兼容格式（One API / DeepSeek 等） |
| 异步任务 | APScheduler + 数据库状态机 |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- SQL Server 2022（或兼容版本）
- ODBC Driver 17 for SQL Server

### 后端部署

```bash
# 克隆项目
git clone <repo-url>
cd 营销系统/backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.dev .env
# 编辑 .env，填入数据库连接串和 AI 接口配置

# 创建数据库并执行建表脚本
# 在 SSMS 中创建数据库 geo_marketing，然后执行 docs/database/schema.sql

# 启动服务
uvicorn app.main:app --reload --port 8000
```

### 前端部署

```bash
cd 营销系统/frontend

# 安装依赖
npm install

# 启动开发服务器（默认代理到后端 8000 端口）
npm run dev
```

### AI 接口配置

系统通过 OpenAI 兼容接口（`/v1/chat/completions`）调用大模型，有两种配置方式：

1. **通过 One API 网关**：部署 [One API](https://github.com/songquanpeng/one-api)，在 `.env` 中配置 `ONE_API_BASE_URL` 和 `ONE_API_KEY`
2. **直接对接模型服务**：将 `ONE_API_BASE_URL` 设为 DeepSeek 等服务商的 API 地址，`ONE_API_KEY` 设为对应的 API Key

## 项目结构

```
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI 入口
│   │   ├── users/             # 用户与认证
│   │   ├── keywords/          # 核心主词与拓展词
│   │   ├── knowledge/         # 企业资料库
│   │   ├── images/            # 图片素材库
│   │   ├── prompts/           # AI 指令规则
│   │   ├── articles/          # 文章生成
│   │   └── common/            # 公共工具
│   ├── workers/               # 异步任务 worker
│   └── requirements.txt
├── frontend/                  # Vue 3 前端
├── docs/
│   └── database/schema.sql    # 建表脚本
├── uploads/                   # 文件存储目录
└── scripts/                   # 工具脚本
```

## API 文档

后端启动后访问：

- Swagger UI：`http://localhost:8000/docs`
- ReDoc：`http://localhost:8000/redoc`

## 账号说明

系统无内置默认账号，首次使用请通过注册接口创建用户：

```
POST /api/users/register
```

如需管理员账号，注册后在数据库中将 `mkt_users.role` 字段修改为 `admin`。

## 开发计划

| 版本 | 方向 |
|------|------|
| v0.2 | 拓展词组合器、自动定时生成任务 |
| v0.3 | 发布链接回填、平台授权管理 |
| v0.4 | 官媒投放订单、余额充值与消费 |
| v0.5 | 发布统计、消费报表、GEO 监控看板 |

## License

MIT
