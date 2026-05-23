# GEO营销系统 - 开发规范

> 所有开发窗口（子窗口）的强制执行规范。代码提交必须严格遵循以下约定。

## 1. 项目概述

GEO内容营销自动化系统：通过持续生产和分发高质量内容，提高企业品牌在AI搜索结果中的出现概率。

核心业务链路：
```
企业资料/产品资料 → 核心主词+拓展词 → AI生成文章 → 插入图片/知识库 → 发布到自媒体/官媒 → 收录与效果追踪
```

## 2. 技术栈

### 后端
- **框架**: Python 3.11+ / FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **数据库**: SQL Server 2022 (本地SSMS)
- **异步任务**: APScheduler + 数据库状态机（不依赖Redis）
- **AI网关**: One API（OpenAI兼容接口 /v1/chat/completions）
- **文件存储**: 本地磁盘（后续可切OSS）
- **API文档**: FastAPI自带 Swagger UI
- **认证**: JWT (python-jose + passlib)

### 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **模板**: vue-pure-admin
- **构建**: Vite
- **状态管理**: Pinia
- **HTTP**: Axios

### 支付
- **充值入口**: 虎皮椒 / Payjs（聚合支付）
- **钱包**: 自建余额体系（充值、扣费、退费、流水）

## 3. 项目结构

```
E:/营销系统/
├── CLAUDE.md                    # 本规范（子窗口强制加载）
├── docs/
│   ├── database/
│   │   └── schema.sql           # 完整建表SQL
│   └── api/                     # 接口补充说明
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI入口
│   │   ├── config.py            # 配置（环境变量）
│   │   ├── database.py          # SQLAlchemy引擎/会话
│   │   ├── deps.py              # 公共依赖注入
│   │   ├── users/               # 用户与认证
│   │   ├── keywords/            # 核心主词与拓展词
│   │   ├── knowledge/           # 企业资料库
│   │   ├── images/              # 图片素材库
│   │   ├── prompts/             # AI指令规则
│   │   ├── articles/            # 文章生成
│   │   ├── publishing/          # 发布管理
│   │   ├── media_orders/        # 官媒投放订单
│   │   ├── payments/            # 钱包与充值
│   │   ├── reports/             # 数据报表
│   │   └── common/              # 公共工具（分页、响应、异常）
│   ├── workers/
│   │   ├── scheduler.py         # APScheduler主进程
│   │   ├── article_worker.py    # 文章生成worker
│   │   └── publish_worker.py    # 发布worker
│   ├── migrations/              # Alembic迁移
│   ├── tests/
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/                    # vue-pure-admin项目
│   └── src/
│       └── views/marketing/     # 业务页面
├── uploads/                     # 本地文件存储
│   ├── knowledge/
│   └── images/
└── scripts/                     # 工具脚本
```

## 4. 核心模块

| 模块 | 职责 | 路由前缀 |
|------|------|----------|
| users | 注册登录、角色权限、用户管理 | /api/users |
| keywords | 核心主词CRUD、拓展词组合生成 | /api/keywords |
| knowledge | 企业资料上传、文本提取、分段 | /api/knowledge |
| images | 图片分类、上传、关联主词 | /api/images |
| prompts | AI指令模板（标题+内容）、平台规则 | /api/prompts |
| articles | 文章生成、列表、编辑、状态流转 | /api/articles |
| publishing | 平台授权、发布任务、链接回填 | /api/publishing |
| media_orders | 官媒资源列表、下单、订单管理 | /api/media-orders |
| payments | 充值、余额、流水、扣款 | /api/payments |
| reports | 数据概览、发布统计、消费统计 | /api/reports |

### 模块依赖
```
articles → keywords, knowledge, images, prompts
publishing → articles, users(平台授权)
media_orders → articles, payments
reports → 所有模块(只读聚合)
```

## 5. 编码规范

### 5.1 后端 Python

- **分层**: Router → Service → Model，禁止跨层
- **命名**:
  - 文件/模块: snake_case
  - 类名: PascalCase
  - 函数/变量: snake_case
  - 常量: UPPER_SNAKE_CASE
  - 数据库字段: snake_case
- **返回格式**: 统一 `{"code": 0, "data": ..., "message": "success"}`
- **异常**: 自定义 `BizException(code, message)` + 全局handler
- **分页**: `{"items": [], "total": N, "page": P, "page_size": S}`
- **类型标注**: 所有函数必须有参数和返回值类型标注
- **Pydantic**: 请求体用 Schema，响应用 Schema，禁止直接返回ORM对象
- **async**: 数据库操作用async，CPU密集型任务放worker

### 5.2 前端

- **文件命名**: kebab-case，如 `keyword-list.vue`
- **组件命名**: PascalCase
- **API层**: `src/api/marketing/xxx.ts`
- **类型**: 所有接口必须有TypeScript类型定义
- **禁止**: any类型、console.log残留、硬编码魔法值

### 5.3 数据库

- **表前缀**: `mkt_`
- **必备字段**: `id`, `created_at`, `updated_at`
- **主键**: bigint IDENTITY(1,1)
- **软删除**: `is_deleted` BIT DEFAULT 0
- **索引命名**: `IX_表名_字段名`
- **禁止**: 外键约束（应用层保证一致性）
- **字符集**: NVARCHAR（支持中文）

### 5.4 Git

- **分支**: `main` → `dev` → `feature/模块-功能`
- **提交**: `feat(模块): 描述` / `fix(模块): 描述`
- **单次提交**: 一个子任务一次提交
- **禁止**: 直接推main

## 6. 业务流程规范

### 6.1 文章生成流程
```
用户创建自动任务 → 调度器触发 → 选取拓展词 → 拼装prompt(指令+企业资料+关键词)
  → 调用One API → 解析结果 → 插入图片 → 存储文章 → 等待发布
```

### 6.2 One API对接
- 统一走 /v1/chat/completions
- 超时60s，重试3次，指数退避
- 模型选择和Key轮询由One API管理
- 业务层只负责prompt构造和结果解析

### 6.3 文章状态机
```
待生成 → 生成中 → 待审核 → 待发布 → 发布中 → 发布成功/发布失败
```

### 6.4 媒体订单状态机
```
待支付 → 已支付 → 待投稿 → 投稿中 → 已发布/发布失败 → 已退款
```

## 7. 用户角色

| 角色 | 权限范围 |
|------|----------|
| admin | 全部功能、用户管理、媒体资源管理、系统配置 |
| operator | 协助配置、审核资料、处理失败任务、维护默认模板 |
| enterprise | 上传资料、管理主词、配置任务、查看报表、充值消费 |

## 8. 子窗口任务协议

### 接收格式
```
任务编号: TASK-XXX
类型: feature / fix / refactor
模块: 具体模块名
描述: 做什么
验收标准: 完成判定
依赖: 前置条件
```

### 完成汇报
```
任务编号: TASK-XXX
状态: 已完成 / 部分完成 / 阻塞
变更文件: [列表]
关键决策: [偏离说明]
遗留问题: [如有]
```

### 禁止事项
- 禁止修改 CLAUDE.md
- 禁止修改非任务范围文件
- 禁止自行决定架构变更（上报总调）
- 禁止引入规范外依赖（上报审批）

## 9. 环境配置

### 开发环境
- Python 3.11+
- Node.js 18+
- SQL Server 2022（本地）
- SSMS（数据库管理）

### 配置约定
- 开发: `.env.dev`
- 生产: `.env.prod`
- One API地址和Key通过环境变量注入，禁止硬编码
- 数据库连接串通过环境变量，禁止明文密码入库

## 10. 版本计划

| 版本 | 里程碑 | 核心功能 |
|------|--------|----------|
| v0.1 | 基础可用 | 项目骨架、登录注册、企业资料、图片素材、核心主词、AI指令、手动生成文章 |
| v0.2 | 自动创作 | 拓展词组合器、自动任务、定时生成、任务启停 |
| v0.3 | 发布闭环 | 手动回填发布链接、平台授权管理、发布记录 |
| v0.4 | 付费投放 | 媒体资源列表、投稿订单、余额充值、消费明细 |
| v0.5 | 数据报表 | 发布统计、消费统计、GEO监控、数据概览看板 |
