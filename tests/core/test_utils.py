from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from vibe.core.utils import is_dangerous_directory


def test_is_dangerous_directory():
    # We mock Path.home to return a predictable path
    with patch("pathlib.Path.home") as mock_home:
        mock_home.return_value = Path("/home/user")

        # Exact match home (Should be dangerous)
        is_danger, reason = is_dangerous_directory("/home/user")
        assert is_danger, f"Home directory should be dangerous. Reason: {reason}"
        assert "home directory" in reason

        # Subdir of home (Should be safe)
        is_danger, reason = is_dangerous_directory("/home/user/projects")
        assert not is_danger, f"Home subdirectory should be safe. Reason: {reason}"

        # Dangerous home subdir (Documents)
        is_danger, reason = is_dangerous_directory("/home/user/Documents")
        assert is_danger, f"Documents directory should be dangerous. Reason: {reason}"
        assert "Documents folder" in reason

        # Subdir of Documents (Should be safe - debatable, but per current logic/plan)
        # Assuming we want to allow working IN a project inside Documents
        is_danger, reason = is_dangerous_directory("/home/user/Documents/MyProject")
        assert not is_danger, f"Documents subdirectory should be safe. Reason: {reason}"

        # Exact match system (Should be dangerous)
        is_danger, reason = is_dangerous_directory("/usr")
        assert is_danger, f"/usr should be dangerous. Reason: {reason}"

        # Subdir of system (Should be dangerous)
        # This currently fails in the original implementation
        is_danger, reason = is_dangerous_directory("/usr/bin")
        assert is_danger, f"/usr/bin should be dangerous. Reason: {reason}"
        assert "System" in reason or "usr" in reason

        # Other system paths
        is_danger, reason = is_dangerous_directory("/etc")
        assert is_danger, "/etc should be dangerous"

        is_danger, reason = is_dangerous_directory("/etc/nginx")
        assert is_danger, "/etc/nginx should be dangerous"

        # Safe system-like path (if it existed in a weird place?)
        # e.g. /usr/local/myapp (if we consider /usr/local safe? probably not)
        # Let's verify /tmp behavior if we decide to include it or not.
        # For now, let's stick to the core requirement: System subdirectories.
