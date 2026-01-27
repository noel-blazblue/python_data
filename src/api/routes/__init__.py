"""API 路由模块"""

from src.api.routes.articles import router as articles_router
from src.api.routes.analysis import router as analysis_router
from src.api.routes.stats import router as stats_router
from src.api.routes.tasks import router as tasks_router

__all__ = [
    'articles_router',
    'analysis_router',
    'stats_router',
    'tasks_router',
]
