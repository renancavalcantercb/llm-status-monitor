"""
Test suite for state management
"""

import pytest
import json
from pathlib import Path
from llm_monitor.state import StateManager


class TestStateManager:
    """Tests for StateManager class"""

    def test_load_nonexistent_file(self, tmp_path):
        """Test loading when state file doesn't exist"""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        state = manager.load()
        assert state == {}

    def test_save_and_load(self, tmp_path):
        """Test saving and loading state"""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # Update and save
        manager.update_service("test_service", "entry_123", "Test Title")
        assert manager.save() is True

        # Load in new instance
        new_manager = StateManager(state_file)
        state = new_manager.load()

        assert "test_service" in state
        assert state["test_service"]["last_id"] == "entry_123"
        assert state["test_service"]["last_title"] == "Test Title"
        assert "last_checked" in state["test_service"]

    def test_get_last_id(self, tmp_path):
        """Test getting last ID for a service"""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        # No state yet
        assert manager.get_last_id("service1") is None

        # Update state
        manager.update_service("service1", "id_456", "Title")
        assert manager.get_last_id("service1") == "id_456"

    def test_update_service(self, tmp_path):
        """Test updating service state"""
        state_file = tmp_path / "state.json"
        manager = StateManager(state_file)

        manager.update_service("service1", "id_1", "First")
        manager.update_service("service2", "id_2", "Second")

        state = manager.get_state()
        assert len(state) == 2
        assert state["service1"]["last_id"] == "id_1"
        assert state["service2"]["last_id"] == "id_2"

    def test_load_invalid_json(self, tmp_path):
        """Test loading invalid JSON file"""
        state_file = tmp_path / "state.json"

        # Write invalid JSON
        state_file.write_text("not valid json {")

        manager = StateManager(state_file)
        state = manager.load()

        # Should return empty dict on parse error
        assert state == {}

    def test_save_creates_directory(self, tmp_path):
        """Test that save creates parent directory if needed"""
        state_file = tmp_path / "nested" / "dir" / "state.json"
        manager = StateManager(state_file)

        manager.update_service("test", "id", "title")
        assert manager.save() is True

        assert state_file.exists()
        assert state_file.parent.exists()
