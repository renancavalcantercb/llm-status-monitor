"""
LLM Status Monitor - Monitor status pages for Claude and ChatGPT
"""

__version__ = "0.2.0"

from .monitor import StatusMonitor
from .config import Config

__all__ = ["StatusMonitor", "Config"]
