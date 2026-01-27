"""
AI 分析器实现
"""
import os
import json
from typing import List, Dict, Optional
from loguru import logger
from openai import OpenAI
from anthropic import Anthropic

from src.analyzers.base import BaseAnalyzer
from src.core.exceptions import AnalysisException


class AIAnalyzer(BaseAnalyzer):
    """AI 分析器"""
    
    def __init__(self, config):
        """
        初始化 AI 分析器
        
        Args:
            config: 配置对象（Settings）
        """
        self.config = config
        self.ai_config = config.ai
        self.provider = self.ai_config.provider
        self.model = self.ai_config.model
        self.temperature = self.ai_config.temperature
        self.max_tokens = self.ai_config.max_tokens
        self.timeout = self.ai_config.timeout
        
        # 检查 API Key
        if not self.ai_config.api_key:
            logger.warning("未配置 AI API Key，AI 分析功能将不可用")
        
        # 初始化客户端
        self._init_client()
    
    def _init_client(self):
        """初始化 AI 客户端"""
        api_key = self.ai_config.api_key
        base_url = self.ai_config.base_url
        
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
    
    def analyze_single(self, article: Dict) -> Optional[Dict]:
        """
        分析单篇文章
        
        Args:
            article: 文章数据字典，包含 title, summary, content, source
            
        Returns:
            分析结果字典，包含 analysis_content, sentiment, sentiment_score, key_points
        """
        try:
            title = article.get('title', '')
            summary = article.get('summary', '')
            content = article.get('content', '')
            
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
            result_text = self._call_api(prompt)
            
            # 解析 JSON 响应
            return self._parse_response(result_text)
        
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")
            raise AnalysisException(f"AI 分析失败: {e}") from e
    
    def analyze_batch(self, articles: List[Dict]) -> Optional[Dict]:
        """
        批量分析多篇文章，生成综合摘要
        
        Args:
            articles: 文章列表
            
        Returns:
            批量分析结果字典，包含 summary_content, article_count
        """
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
            result_text = self._call_api(prompt)
            
            # 解析 JSON 响应
            return self._parse_batch_response(result_text, len(articles))
        
        except Exception as e:
            logger.error(f"批量 AI 分析失败: {e}")
            raise AnalysisException(f"批量 AI 分析失败: {e}") from e
    
    def _call_api(self, prompt: str) -> str:
        """调用 AI API"""
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
            return response.content[0].text
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
            return response.choices[0].message.content
    
    def _parse_response(self, result_text: str) -> Dict:
        """解析单篇文章分析响应"""
        try:
            # 尝试提取 JSON（可能包含 markdown 代码块）
            result_text = self._extract_json(result_text)
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
    
    def _parse_batch_response(self, result_text: str, article_count: int) -> Dict:
        """解析批量分析响应"""
        try:
            result_text = self._extract_json(result_text)
            result = json.loads(result_text)
            
            return {
                'summary_content': json.dumps(result, ensure_ascii=False),
                'article_count': article_count
            }
        
        except json.JSONDecodeError as e:
            logger.error(f"解析批量分析 JSON 失败: {e}")
            return {
                'summary_content': result_text,
                'article_count': article_count
            }
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        if '```json' in text:
            json_start = text.find('```json') + 7
            json_end = text.find('```', json_start)
            return text[json_start:json_end].strip()
        elif '```' in text:
            json_start = text.find('```') + 3
            json_end = text.find('```', json_start)
            return text[json_start:json_end].strip()
        return text.strip()
