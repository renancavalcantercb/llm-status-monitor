"""
State management for tracking processed RSS entries
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """Manages persistent state to track processed RSS entries"""

    def __init__(self, state_file: Path):
        self.state_file = state_file
        self._state: Dict[str, Any] = {}

    def load(self) -> Dict[str, Any]:
        """Load state from file"""
        if not self.state_file.exists():
            logger.info(f"State file not found: {self.state_file}")
            self._state = {}
            return self._state

        try:
            with open(self.state_file, 'r') as f:
                self._state = json.load(f)
            logger.info(f"Loaded state from {self.state_file}")
            return self._state
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse state file {self.state_file}: {e}")
            self._state = {}
            return self._state
        except Exception as e:
            logger.error(f"Failed to load state from {self.state_file}: {e}")
            self._state = {}
            return self._state

    def save(self) -> bool:
        """Save current state to file"""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self._state, f, indent=2)
            logger.debug(f"Saved state to {self.state_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save state to {self.state_file}: {e}")
            return False

    def get_last_id(self, service_id: str) -> Optional[str]:
        """Get the last seen entry ID for a service"""
        service_state = self._state.get(service_id, {})
        return service_state.get('last_id')

    def update_service(
        self,
        service_id: str,
        entry_id: str,
        title: str
    ) -> None:
        """Update state for a service with new entry information"""
        self._state[service_id] = {
            'last_id': entry_id,
            'last_title': title,
            'last_checked': datetime.now().isoformat()
        }
        logger.debug(f"Updated state for {service_id}: {title}")

    def get_state(self) -> Dict[str, Any]:
        """Get the current state dictionary"""
        return self._state
