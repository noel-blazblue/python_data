"""
AI 分析模块
使用 OpenAI/Anthropic 等 API 进行新闻分析
"""
import os
import json
import yaml
from typing import List, Dict, Optional
from loguru import logger
from openai import OpenAI
from anthropic import Anthropic


class AIAnalyzer:
    """AI 分析器"""
    
    def __init__(self, config_path='app_config.yaml'):
        """初始化 AI 分析器"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        ai_config = self.config.get('ai', {})
        self.provider = ai_config.get('provider', 'openai')
        self.model = ai_config.get('model', 'gpt-4o-mini')
        self.temperature = ai_config.get('temperature', 0.7)
        self.max_tokens = ai_config.get('max_tokens', 2000)
        self.timeout = ai_config.get('timeout', 60)
        
        # 从环境变量或配置读取 API Key
        api_key = os.getenv('AI_API_KEY') or ai_config.get('api_key', '')
        if not api_key:
            logger.warning("未配置 AI API Key，AI 分析功能将不可用")
        
        # 初始化客户端
        base_url = ai_config.get('base_url', '')
        
        if self.provider == 'openai':
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url if base_url else None,
                timeout=self.timeout
            )
        elif self.provider == 'anthropic':
            self.client = Anthropic(api_key=api_key, timeout=self.timeout)
        elif self.provider == 'deepseek':
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url or 'https://api.deepseek.com/v1',
                timeout=self.timeout
            )
        else:
            # 自定义 OpenAI 兼容接口
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.timeout
            )
        
        self.provider = self.provider  # 保存提供商类型
    
    def analyze_single_article(self, article: Dict) -> Optional[Dict]:
        """分析单篇文章"""
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = article.get('content', '')
            source = article.get('source', '')
            
            # 构建分析文本
            text_to_analyze = f"标题: {title}\n"
            if summary:
                text_to_analyze += f"摘要: {summary}\n"
            if content:
                text_to_analyze += f"内容: {content[:1000]}\n"  # 限制内容长度
            
            # 构建提示词
            prompt = f"""请对以下新闻进行分析，并提供：
1. 简要分析（200字以内）
2. 情感倾向（positive/negative/neutral）
3. 关键要点（3-5个要点，JSON数组格式）
4. 重要性评分（1-10分）

新闻内容：
{text_to_analyze}

请以 JSON 格式返回，格式如下：
{{
    "analysis": "分析内容",
    "sentiment": "positive/negative/neutral",
    "sentiment_score": 0.0-1.0,
    "key_points": ["要点1", "要点2", "要点3"],
    "importance_score": 1-10
}}
"""
            
            # 调用 AI API
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                result_text = response.content[0].text
            else:
                # OpenAI 兼容接口
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                result_text = response.choices[0].message.content
            
            # 解析 JSON 响应
            try:
                # 尝试提取 JSON（可能包含 markdown 代码块）
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                
                result = json.loads(result_text)
                
                return {
                    'analysis_type': 'general',
                    'analysis_content': result.get('analysis', ''),
                    'sentiment': result.get('sentiment', 'neutral'),
                    'sentiment_score': result.get('sentiment_score', 0.5),
                    'key_points': json.dumps(result.get('key_points', []), ensure_ascii=False)
                }
            
            except json.JSONDecodeError as e:
                logger.error(f"解析 AI 响应 JSON 失败: {e}")
                logger.debug(f"响应内容: {result_text}")
                # 返回原始文本作为分析内容
                return {
                    'analysis_type': 'general',
                    'analysis_content': result_text,
                    'sentiment': 'neutral',
                    'sentiment_score': 0.5,
                    'key_points': '[]'
                }
        
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")
            return None
    
    def analyze_batch_articles(self, articles: List[Dict]) -> Optional[Dict]:
        """批量分析多篇文章，生成综合摘要"""
        try:
            if not articles:
                return None
            
            # 构建文章列表文本
            articles_text = ""
            for i, article in enumerate(articles[:20], 1):  # 最多20篇
                articles_text += f"\n{i}. {article.get('title', '无标题')}\n"
                if article.get('summary'):
                    articles_text += f"   摘要: {article.get('summary', '')[:200]}\n"
            
            # 构建提示词
            prompt = f"""请对以下 {len(articles)} 篇新闻进行综合分析，提供：
1. 整体趋势分析（300字以内）
2. 主要热点话题（3-5个）
3. 重要事件总结
4. 可能的影响和趋势预测

新闻列表：
{articles_text}

请以 JSON 格式返回，格式如下：
{{
    "trend_analysis": "整体趋势分析",
    "hot_topics": ["话题1", "话题2", "话题3"],
    "key_events": "重要事件总结",
    "impact_prediction": "影响和趋势预测"
}}
"""
            
            # 调用 AI API
            if self.provider == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                result_text = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
                result_text = response.choices[0].message.content
            
            # 解析 JSON 响应
            try:
                if '```json' in result_text:
                    json_start = result_text.find('```json') + 7
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                elif '```' in result_text:
                    json_start = result_text.find('```') + 3
                    json_end = result_text.find('```', json_start)
                    result_text = result_text[json_start:json_end].strip()
                
                result = json.loads(result_text)
                
                return {
                    'summary_content': json.dumps(result, ensure_ascii=False),
                    'article_count': len(articles)
                }
            
            except json.JSONDecodeError as e:
                logger.error(f"解析批量分析 JSON 失败: {e}")
                return {
                    'summary_content': result_text,
                    'article_count': len(articles)
                }
        
        except Exception as e:
            logger.error(f"批量 AI 分析失败: {e}")
            return None
