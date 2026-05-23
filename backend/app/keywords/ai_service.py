"""AI生成拓展词服务 - 通过One API网关调用DeepSeek"""

import json
import asyncio

import httpx

from app.config import get_settings

settings = get_settings()

EXPANSION_PROMPT_TEMPLATE = """你是一个SEO关键词拓展专家。根据用户提供的核心主词和目标转化词，生成相关的副词和组合词。

要求：
1. 副词必须包含核心主词，并与目标转化词逻辑匹配
2. 组合词 = 核心主词 + 副词的自然组合
3. 生成10-20条副词
4. 覆盖常见长尾问答场景

请严格按以下JSON格式返回，不要包含其他内容：
{{"副词列表": ["副词1", "副词2", ...], "组合词列表": ["组合词1", "组合词2", ...]}}

核心主词：{keyword}
目标转化词：{target_word}"""


KEYWORD_TREE_PROMPT = """你是一个 GEO（Generative Engine Optimization）关键词策略专家。你的任务是根据用户提供的核心主词和目标转化词，生成一棵完整的关键词树，用于 AI 搜索优化。

背景：GEO 的目标是让企业品牌在 ChatGPT、DeepSeek、豆包、Kimi、Perplexity 等 AI 搜索引擎的回答中被推荐和提及。

输入信息：
- 核心主词：{keyword}
- 目标转化词：{target_word}
- 行业：{industry}
- 关联产品/服务：{related_product}
- 目标地区：{target_region}

请生成：
1. 5-10 个副词：核心主词的垂直细分场景，围绕"谁在用/在哪用/解决什么问题/哪类产品"展开
2. 每个副词下 10-20 个组合词：模拟真实用户向 AI 提问或搜索的自然表达

组合词必须覆盖以下搜索意图类型：
- 推荐类：哪家好、推荐、排行榜、口碑好
- 厂商类：厂家、厂商、服务商、源头企业、供应商
- 采购类：价格、多少钱、报价、收费标准
- 方案类：解决方案、系统方案、管理方案
- 场景类：适合XX店、适合XX行业
- 对比类：哪个好、怎么选、和XX区别
- 问答类：用什么、有哪些、如何选择
- 本地类：地区+关键词（仅当提供了目标地区时生成）

质量要求：
- 组合词必须像真实用户会问的问题或搜索短语，不能是机械拼接
- 副词不需要机械包含核心主词原文，但必须语义相关
- 不要生成重复、语义不自然、明显低质量的词
- priority 评分 1-100，越高表示搜索量和商业价值越大

请严格按以下 JSON 格式返回，不要包含其他内容：
{{"sub_words": [{{"name": "副词名称", "reason": "生成理由", "search_potential_score": 85, "combo_words": [{{"word": "组合词内容", "intent": "推荐类", "priority": 92}}]}}]}}"""


async def call_deepseek_legacy(keyword: str, target_word: str) -> dict:
    """
    调用One API网关(DeepSeek模型)生成拓展词（旧版）

    Returns:
        {"副词列表": [...], "组合词列表": [...]}
    """
    prompt = EXPANSION_PROMPT_TEMPLATE.format(keyword=keyword, target_word=target_word)

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.ONE_API_KEY}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{settings.ONE_API_BASE_URL}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            last_error = e
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

    raise RuntimeError(f"DeepSeek API调用失败，已重试3次: {last_error}")


# 保持向后兼容的别名
call_deepseek = call_deepseek_legacy


async def generate_keyword_tree(
    keyword: str,
    target_word: str,
    industry: str | None = None,
    related_product: str | None = None,
    target_region: str | None = None,
) -> dict:
    """调用One API网关生成完整关键词树"""
    prompt = KEYWORD_TREE_PROMPT.format(
        keyword=keyword,
        target_word=target_word,
        industry=industry or "未指定",
        related_product=related_product or "未指定",
        target_region=target_region or "不限",
    )

    payload = {
        "model": settings.DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "response_format": {"type": "json_object"},
    }

    headers = {
        "Authorization": f"Bearer {settings.ONE_API_KEY}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{settings.ONE_API_BASE_URL}/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, KeyError) as e:
            last_error = e
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

    raise RuntimeError(f"关键词树生成失败，已重试3次: {last_error}")
