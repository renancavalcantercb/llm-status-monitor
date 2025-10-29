#!/usr/bin/env python3
"""
Main entry point for LLM Status Monitor
"""

import sys
import logging
from pathlib import Path

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

from llm_monitor import StatusMonitor, Config


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler
            logging.FileHandler(
                log_dir / "monitor.log",
                encoding="utf-8"
            )
        ]
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def main() -> int:
    """Main function"""
    # Setup logging
    import os
    log_level = os.getenv("LOG_LEVEL", "INFO")
    setup_logging(log_level)

    logger = logging.getLogger(__name__)

    try:
        # Load configuration
        config = Config.from_env()
        logger.info("Configuration loaded successfully")

        # Create and run monitor
        monitor = StatusMonitor(config)
        monitor.run()

        return 0

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.error("Please check your .env file and ensure all required variables are set")
        return 1
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
