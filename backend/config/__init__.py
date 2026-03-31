"""
Configuration module for the Synapse Research Agent project.

Contains various configuration settings and utilities:
- LLM configuration
- Topic research agent and task configurations
- Logging configuration using loguru
"""

from .llm import llm
from .topic_research.agents import AGENT_CONFIGS as TOPIC_RESEARCH_AGENT_CONFIGS
from .topic_research.tasks import TASK_CONFIGS as TOPIC_RESEARCH_TASK_CONFIGS
from .sources_research.agents import AGENT_CONFIGS as SOURCES_RESEARCH_AGENT_CONFIGS
from .sources_research.tasks import TASK_CONFIGS as SOURCES_RESEARCH_TASK_CONFIGS
from .logging import setup_logging, logger
__all__ = [
    "llm",
    "TOPIC_RESEARCH_AGENT_CONFIGS",
    "TOPIC_RESEARCH_TASK_CONFIGS",
    "SOURCES_RESEARCH_AGENT_CONFIGS",
    "SOURCES_RESEARCH_TASK_CONFIGS",
    "setup_logging",
    "logger",
]
