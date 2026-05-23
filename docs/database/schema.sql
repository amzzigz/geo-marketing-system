-- GEO营销系统 数据库建表脚本
-- SQL Server 2022
-- 表前缀: mkt_
-- 编码: NVARCHAR (支持中文)

-- ============================================================
-- 1. 用户表
-- ============================================================
CREATE TABLE mkt_users (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL,
    phone NVARCHAR(20) NULL,
    email NVARCHAR(100) NULL,
    password_hash NVARCHAR(255) NOT NULL,
    company_name NVARCHAR(200) NULL,
    role NVARCHAR(20) NOT NULL DEFAULT 'enterprise',  -- admin/operator/enterprise
    balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    status TINYINT NOT NULL DEFAULT 1,  -- 1=正常 0=禁用
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE UNIQUE INDEX IX_mkt_users_username ON mkt_users(username) WHERE is_deleted = 0;

-- ============================================================
-- 2. 核心主词表
-- ============================================================
CREATE TABLE mkt_core_keywords (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    keyword NVARCHAR(100) NOT NULL,
    target_word NVARCHAR(200) NULL,       -- 目标转化词（品牌名/公司简称）
    industry NVARCHAR(50) NULL,
    related_product NVARCHAR(200) NULL,
    status TINYINT NOT NULL DEFAULT 1,    -- 1=启用 0=停用
    generated_article_count INT NOT NULL DEFAULT 0,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_core_keywords_user_id ON mkt_core_keywords(user_id);

-- ============================================================
-- 3. 拓展词表
-- ============================================================
CREATE TABLE mkt_keyword_expansions (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    core_keyword_id BIGINT NOT NULL,
    phrase NVARCHAR(300) NOT NULL,
    phrase_type NVARCHAR(20) NULL,        -- prefix/suffix/question/combined
    source NVARCHAR(20) NULL,             -- manual/ai/combiner
    quality_score TINYINT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    used_count INT NOT NULL DEFAULT 0,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_keyword_expansions_core ON mkt_keyword_expansions(core_keyword_id);
CREATE INDEX IX_mkt_keyword_expansions_user ON mkt_keyword_expansions(user_id);

-- ============================================================
-- 4. 企业资料文件表
-- ============================================================
CREATE TABLE mkt_knowledge_files (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    file_name NVARCHAR(255) NOT NULL,
    file_type NVARCHAR(20) NOT NULL,      -- docx/pdf/txt/md
    file_path NVARCHAR(500) NOT NULL,
    file_size BIGINT NULL,
    content_text NVARCHAR(MAX) NULL,      -- 提取的全文
    summary NVARCHAR(MAX) NULL,           -- AI摘要
    status TINYINT NOT NULL DEFAULT 1,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_knowledge_files_user ON mkt_knowledge_files(user_id);

-- ============================================================
-- 5. 企业资料分段表
-- ============================================================
CREATE TABLE mkt_knowledge_chunks (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    file_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    chunk_text NVARCHAR(MAX) NOT NULL,
    chunk_order INT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_knowledge_chunks_file ON mkt_knowledge_chunks(file_id);

-- ============================================================
-- 6. 图片分类表
-- ============================================================
CREATE TABLE mkt_image_categories (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    name NVARCHAR(100) NOT NULL,
    related_keyword_id BIGINT NULL,       -- 关联核心主词
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_image_categories_user ON mkt_image_categories(user_id);

-- ============================================================
-- 7. 图片素材表
-- ============================================================
CREATE TABLE mkt_image_assets (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    file_url NVARCHAR(500) NOT NULL,
    file_name NVARCHAR(255) NOT NULL,
    file_size BIGINT NULL,
    width INT NULL,
    height INT NULL,
    status TINYINT NOT NULL DEFAULT 1,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_image_assets_category ON mkt_image_assets(category_id);
CREATE INDEX IX_mkt_image_assets_user ON mkt_image_assets(user_id);

-- ============================================================
-- 8. AI指令模板表
-- ============================================================
CREATE TABLE mkt_ai_prompts (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NULL,                  -- NULL=系统默认模板
    name NVARCHAR(100) NOT NULL,
    platform NVARCHAR(50) NULL,           -- 适用平台，NULL=通用
    prompt_type NVARCHAR(20) NOT NULL,    -- title/content
    content_type NVARCHAR(30) NULL,       -- 科普/排行榜/推荐/问答/案例等
    prompt_text NVARCHAR(MAX) NOT NULL,
    is_default BIT NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_ai_prompts_user ON mkt_ai_prompts(user_id);

-- ============================================================
-- 9. 平台内容规则表
-- ============================================================
CREATE TABLE mkt_platform_rules (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    platform NVARCHAR(50) NOT NULL,
    allow_phone BIT NOT NULL DEFAULT 0,
    allow_website BIT NOT NULL DEFAULT 0,
    allow_qrcode BIT NOT NULL DEFAULT 0,
    allow_company_name BIT NOT NULL DEFAULT 1,
    content_length_min INT NULL,
    content_length_max INT NULL,
    sensitive_word_policy NVARCHAR(200) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE UNIQUE INDEX IX_mkt_platform_rules_platform ON mkt_platform_rules(platform);

-- ============================================================
-- 10. 自动发布任务表
-- ============================================================
CREATE TABLE mkt_auto_publish_tasks (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_name NVARCHAR(100) NOT NULL,
    platform NVARCHAR(50) NOT NULL,
    core_keyword_id BIGINT NOT NULL,
    image_category_id BIGINT NULL,
    knowledge_file_ids NVARCHAR(500) NULL,   -- JSON数组 [1,2,3]
    title_prompt_id BIGINT NULL,
    content_prompt_id BIGINT NULL,
    content_type NVARCHAR(30) NULL,
    publish_cycle NVARCHAR(20) NOT NULL,     -- daily/weekly/custom
    time_start NVARCHAR(5) NULL,             -- 09:00
    time_end NVARCHAR(5) NULL,               -- 18:00
    max_article_count INT NOT NULL DEFAULT 10,
    generated_count INT NOT NULL DEFAULT 0,
    published_count INT NOT NULL DEFAULT 0,
    status NVARCHAR(20) NOT NULL DEFAULT 'draft', -- draft/active/paused/completed/error
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_auto_publish_tasks_user ON mkt_auto_publish_tasks(user_id);
CREATE INDEX IX_mkt_auto_publish_tasks_status ON mkt_auto_publish_tasks(status);

-- ============================================================
-- 11. 文章表
-- ============================================================
CREATE TABLE mkt_articles (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    task_id BIGINT NULL,
    core_keyword_id BIGINT NULL,
    expansion_keyword_id BIGINT NULL,
    title NVARCHAR(300) NULL,
    content NVARCHAR(MAX) NULL,
    images NVARCHAR(MAX) NULL,            -- JSON数组，图片URL列表
    platform NVARCHAR(50) NULL,
    status NVARCHAR(20) NOT NULL DEFAULT 'pending',
        -- pending/generating/review/ready/publishing/published/failed/skipped
    publish_url NVARCHAR(500) NULL,
    fail_reason NVARCHAR(500) NULL,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    published_at DATETIME2 NULL
);
CREATE INDEX IX_mkt_articles_user ON mkt_articles(user_id);
CREATE INDEX IX_mkt_articles_task ON mkt_articles(task_id);
CREATE INDEX IX_mkt_articles_status ON mkt_articles(status);

-- ============================================================
-- 12. 平台授权表
-- ============================================================
CREATE TABLE mkt_platform_authorizations (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    platform NVARCHAR(50) NOT NULL,
    account_name NVARCHAR(100) NULL,
    auth_type NVARCHAR(20) NOT NULL,      -- cookie/token/oauth
    cookie_encrypted NVARCHAR(MAX) NULL,
    access_token_encrypted NVARCHAR(MAX) NULL,
    refresh_token_encrypted NVARCHAR(MAX) NULL,
    expire_at DATETIME2 NULL,
    status TINYINT NOT NULL DEFAULT 1,    -- 1=有效 0=失效
    last_auth_at DATETIME2 NULL,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_platform_auth_user ON mkt_platform_authorizations(user_id);

-- ============================================================
-- 13. 媒体资源表（官媒新闻源）
-- ============================================================
CREATE TABLE mkt_media_resources (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    channel NVARCHAR(50) NULL,
    region NVARCHAR(50) NULL,
    cost_price DECIMAL(10,2) NOT NULL,    -- 成本价
    sale_price DECIMAL(10,2) NOT NULL,    -- 销售价
    publish_rate TINYINT NULL,            -- 出稿率%
    pc_weight INT NULL,
    mobile_weight INT NULL,
    avg_publish_time NVARCHAR(50) NULL,   -- 平均出稿时间描述
    collect_status NVARCHAR(20) NULL,     -- 收录情况
    link_status NVARCHAR(20) NULL,        -- 链接情况
    contact_policy NVARCHAR(200) NULL,    -- 联系方式限制说明
    remark NVARCHAR(500) NULL,
    is_recommended BIT NOT NULL DEFAULT 0,
    status TINYINT NOT NULL DEFAULT 1,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);

-- ============================================================
-- 14. 媒体投稿订单表
-- ============================================================
CREATE TABLE mkt_media_orders (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    media_id BIGINT NOT NULL,
    order_no NVARCHAR(50) NOT NULL,
    title NVARCHAR(300) NOT NULL,
    content NVARCHAR(MAX) NULL,
    remark NVARCHAR(500) NULL,
    cost_price DECIMAL(10,2) NOT NULL,
    sale_price DECIMAL(10,2) NOT NULL,
    service_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
    status NVARCHAR(20) NOT NULL DEFAULT 'unpaid',
        -- unpaid/paid/pending/submitting/published/failed/refunded/cancelled
    publish_url NVARCHAR(500) NULL,
    fail_reason NVARCHAR(500) NULL,
    is_deleted BIT NOT NULL DEFAULT 0,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    completed_at DATETIME2 NULL
);
CREATE UNIQUE INDEX IX_mkt_media_orders_no ON mkt_media_orders(order_no);
CREATE INDEX IX_mkt_media_orders_user ON mkt_media_orders(user_id);
CREATE INDEX IX_mkt_media_orders_status ON mkt_media_orders(status);

-- ============================================================
-- 15. 充值记录表
-- ============================================================
CREATE TABLE mkt_recharge_records (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    pay_channel NVARCHAR(30) NOT NULL,    -- hupijiaoalipay/hupijiaowechat/payjs
    pay_status TINYINT NOT NULL DEFAULT 0, -- 0=待支付 1=已支付 2=失败
    transaction_no NVARCHAR(100) NULL,    -- 第三方流水号
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    paid_at DATETIME2 NULL
);
CREATE INDEX IX_mkt_recharge_records_user ON mkt_recharge_records(user_id);

-- ============================================================
-- 16. 余额流水表
-- ============================================================
CREATE TABLE mkt_balance_logs (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    type NVARCHAR(30) NOT NULL,
        -- recharge/media_deduct/ai_deduct/refund/manual_adjust/agent_commission
    amount DECIMAL(12,2) NOT NULL,        -- 正数=入账 负数=扣款
    before_balance DECIMAL(12,2) NOT NULL,
    after_balance DECIMAL(12,2) NOT NULL,
    related_order_id BIGINT NULL,
    remark NVARCHAR(200) NULL,
    created_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_balance_logs_user ON mkt_balance_logs(user_id);
CREATE INDEX IX_mkt_balance_logs_type ON mkt_balance_logs(type);

-- ============================================================
-- 17. 拓展词组合区域配置表
-- ============================================================
CREATE TABLE mkt_expansion_zones (
    id BIGINT IDENTITY(1,1) PRIMARY KEY,
    user_id BIGINT NOT NULL,
    core_keyword_id BIGINT NOT NULL,
    zone_code CHAR(1) NOT NULL,           -- A/B/C/D/E/F
    zone_name NVARCHAR(50) NOT NULL,      -- 前缀1/前缀2/核心词/副词/推荐词/疑问词
    words NVARCHAR(MAX) NULL,             -- 一行一个词，换行分隔
    created_at DATETIME2 NOT NULL DEFAULT GETDATE(),
    updated_at DATETIME2 NOT NULL DEFAULT GETDATE()
);
CREATE INDEX IX_mkt_expansion_zones_keyword ON mkt_expansion_zones(core_keyword_id);

-- ============================================================
-- 完成
-- ============================================================
