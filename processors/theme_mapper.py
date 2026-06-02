"""
Theme Mapper — Keyword-based event→theme classification.
MVP: rules-driven mapping. P1: optional LLM refinement.
"""
from typing import List, Dict, Optional, Tuple


# Keyword-to-theme mapping rules.
# Each rule: (theme_id, [keywords], category_hints)
# category_hints: arXiv category prefixes for additional signal
THEME_RULES = [
    ('llm_frontier', [
        'gpt-5', 'gpt-4', 'claude', 'gemini', 'llama', 'frontier model',
        'large language model', 'llm benchmark', 'scaling law', 'moe',
        'mixture of experts', 'constitutional ai', 'rlhf', 'alignment',
        'pretraining', 'language model evaluation', 'multimodal llm',
        'chatgpt', 'bard', 'palm', 'mistral', 'falcon', 'deepseek',
        'qwen', 'kimi', 'glm', 'ernie', 'yi-', 'sparrow'
    ], ['cs.CL']),

    ('ai_agent', [
        'ai agent', 'autonomous agent', 'agent sdk', 'agent framework',
        'tool use', 'tool calling', 'function calling', 'multi-step',
        'webarena', 'agentbench', 'operator', 'adept', 'agent harness',
        'autogpt', 'babyagi', 'crewai', 'langgraph', 'agent protocol',
        'mcp server', 'model context protocol', 'task completion',
        'browser agent', 'computer use', 'desktop agent'
    ], ['cs.AI', 'cs.MA']),

    ('inference_compute', [
        'inference optimization', 'quantization', 'speculative decoding',
        'throughput', 'latency', 'tokens per second', 'edge inference',
        'inference chip', 'lpu', 'groq', 'tensorrt', 'onnx',
        'vllm', 'tgi', 'inference server', 'batch inference',
        'kv cache', 'attention optimization', 'flash attention',
        'model compression', 'distillation', 'pruning'
    ], ['cs.LG', 'cs.AR']),

    ('ai_coding', [
        'code generation', 'copilot', 'devin', 'cursor', 'codex',
        'ai coding', 'software engineering', 'code completion',
        'refactoring', 'code review', 'ide', 'jetbrains ai',
        'github copilot', 'code assistant', 'program synthesis',
        'code intelligence', 'swe-bench', 'humaneval', 'mbpp',
        'poolside', 'magic dev', 'codeium', 'tabnine'
    ], ['cs.SE', 'cs.PL']),

    ('compute_gpu', [
        'nvidia', 'h100', 'h200', 'b100', 'b200', 'gh200',
        'blackwell', 'hopper', 'gpu cluster', 'data center',
        'tpu', 'amd mi300', 'mi400', 'cerebras', 'wafer scale',
        'chip design', 'semiconductor', 'hbm', 'interconnect',
        'nvlink', 'infiniband', 'gpu supply', 'chip shortage'
    ], ['cs.AR', 'cs.DC']),

    ('ai_video', [
        'video generation', 'text-to-video', 'video editing',
        'sora', 'runway', 'pika', 'video synthesis', '4k video',
        'video diffusion', 'frame interpolation', 'motion generation',
        'video understanding', 'temporal consistency', 'gen-',
        'luma', 'haiper', 'kling', 'veo'
    ], ['cs.CV']),

    ('robotics', [
        'humanoid robot', 'robot manipulation', 'embodied ai',
        'figure ai', 'optimus', 'tesla bot', '1x technologies',
        'dexterous', 'visuomotor', 'robot learning', 'imitation learning',
        'robot foundation model', 'mobile manipulation', 'bimanual',
        'robot locomotion', 'sim-to-real', 'robotics transformer',
        'autonomous navigation', 'robot grasping'
    ], ['cs.RO']),

    ('ai_infrastructure', [
        'vector database', 'embedding model', 'model deployment',
        'mlops', 'fine-tuning', 'foundation model platform',
        'pinecone', 'weaviate', 'milvus', 'chroma', 'qdrant',
        'databricks', 'mosaicml', 'huggingface', 'model registry',
        'lora', 'qlora', 'peft', 'model serving', 'ai gateway',
        'prompt management', 'ai safety', 'red teaming',
        'model evaluation', 'rag', 'retrieval augmented'
    ], ['cs.DB', 'cs.DC']),
]


def _match_keywords(text: str, keywords: List[str]) -> bool:
    """Case-insensitive keyword match."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _match_category(cat_hint: str, categories: List[str]) -> bool:
    """Check if arXiv category hints match."""
    if not cat_hint:
        return False
    return any(c in cat_hint for c in categories)


def map_event_to_themes(title: str, description: str, event_type: str,
                        source: str = '', cat_hint: str = '',
                        github_topics: Optional[List[str]] = None) -> List[Tuple[str, float]]:
    """
    Map an event to one or more themes with weights.
    Returns list of (theme_id, weight) tuples. Weights sum to 1.0.
    MVP: single theme (weight=1.0). P1: multi-theme.
    """
    text = f"{title} {description}"
    if github_topics:
        text += ' ' + ' '.join(github_topics)

    # Score each theme
    scores = []
    for theme_id, keywords, cat_hints in THEME_RULES:
        score = 0
        # Keyword match (strong signal)
        keyword_matched = _match_keywords(text, keywords)
        if keyword_matched:
            score += 5
        # Category hint match (auxiliary for arXiv)
        if cat_hint and _match_category(cat_hint, cat_hints):
            score += 2
        # Event type bonus — only when keywords already matched
        if keyword_matched:
            if event_type == 'RESEARCH_PAPER' and theme_id in ['llm_frontier', 'ai_agent', 'inference_compute', 'robotics', 'ai_video']:
                score += 1
            if event_type in ['FUNDING_ROUND', 'PRODUCT_LAUNCH'] and theme_id in ['compute_gpu', 'ai_coding', 'ai_infrastructure', 'ai_agent', 'robotics', 'ai_video']:
                score += 1
        if score > 0:
            scores.append((theme_id, score))

    if not scores:
        return []  # No mapping found — event will be filtered

    # Pick top theme only (MVP single-theme)
    scores.sort(key=lambda x: x[1], reverse=True)
    top_theme, top_score = scores[0]

    # Assign weight: 1.0 for clear match (score >= 5), 0.7 for fuzzy match
    weight = 1.0 if top_score >= 5 else 0.7

    return [(top_theme, weight)]


# Theme ID → Name mapping
THEME_NAMES = {
    'llm_frontier': 'LLM 前沿模型',
    'ai_agent': 'AI Agent 自主代理',
    'inference_compute': '推理计算',
    'ai_coding': 'AI 编程',
    'compute_gpu': '算力与芯片',
    'ai_video': 'AI 视频生成',
    'robotics': '机器人',
    'ai_infrastructure': 'AI 基础设施',
}


def get_theme_name(theme_id: str) -> str:
    return THEME_NAMES.get(theme_id, theme_id)


if __name__ == '__main__':
    # Test cases
    tests = [
        ("OpenAI releases GPT-5 with 2x reasoning", "New model scores 94% on MATH", "PRODUCT_LAUNCH", "", "cs.CL"),
        ("Nvidia announces Blackwell Ultra GPU", "Next-gen datacenter GPU for AI training", "PRODUCT_LAUNCH", "", ""),
        ("New speculative decoding technique reduces cost 70%", "Stanford research on inference optimization", "RESEARCH_PAPER", "arXiv", "cs.LG"),
        ("Figure AI raises $1.5B for humanoid robots", "Funding for humanoid robot mass production", "FUNDING_ROUND", "", ""),
        ("ollama/ollama: Get up and running with LLMs", "Local LLM runner", "PRODUCT_BETA", "GitHub", ""),
    ]
    for title, desc, etype, src, cat in tests:
        themes = map_event_to_themes(title, desc, etype, src, cat)
        print(f"  {title[:60]:60s} → {themes}")
