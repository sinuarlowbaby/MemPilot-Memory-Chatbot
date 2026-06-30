from unittest.mock import MagicMock
import mem0

# Mock Memory.from_config to prevent connecting to Qdrant/external databases on import
mem0.Memory.from_config = MagicMock(return_value=MagicMock())
