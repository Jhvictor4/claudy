"""Configuration for Claudy."""

from pathlib import Path

# Server configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
SERVER_TIMEOUT = 120  # seconds

# Session management configuration
SESSION_IDLE_TIMEOUT = 1200  # 20 minutes in seconds
SESSION_CLEANUP_INTERVAL = 300  # Check every 5 minutes

# Port file location
CLAUDY_DIR = Path.home() / ".claudy"
PORT_FILE = CLAUDY_DIR / "server.port"
PID_FILE = CLAUDY_DIR / "server.pid"

# Ensure .claudy directory exists
CLAUDY_DIR.mkdir(exist_ok=True)

# Output verbosity levels
VERBOSITY_QUIET = "quiet"      # Only final text response
VERBOSITY_NORMAL = "normal"    # Final response + basic info
VERBOSITY_VERBOSE = "verbose"  # Everything including thinking and tool calls


# Helper functions for file I/O
def _read_int_from_file(file_path: Path) -> int | None:
    """Read an integer value from a file."""
    try:
        if file_path.exists():
            return int(file_path.read_text().strip())
    except (ValueError, IOError):
        pass
    return None


def _write_int_to_file(file_path: Path, value: int) -> None:
    """Write an integer value to a file."""
    file_path.write_text(str(value))


# Public API
def get_server_port() -> int | None:
    """Read the server port from the port file."""
    return _read_int_from_file(PORT_FILE)


def save_server_port(port: int) -> None:
    """Save the server port to the port file."""
    _write_int_to_file(PORT_FILE, port)


def get_server_pid() -> int | None:
    """Read the server PID from the PID file."""
    return _read_int_from_file(PID_FILE)


def save_server_pid(pid: int) -> None:
    """Save the server PID to the PID file."""
    _write_int_to_file(PID_FILE, pid)


def clear_server_info() -> None:
    """Clear server port and PID files."""
    if PORT_FILE.exists():
        PORT_FILE.unlink()
    if PID_FILE.exists():
        PID_FILE.unlink()
