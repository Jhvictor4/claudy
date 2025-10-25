"""Configuration for Claudy."""

from pathlib import Path

# Server configuration
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
SERVER_TIMEOUT = 120  # seconds

# Session management configuration
SESSION_IDLE_TIMEOUT = 7200  # 2 hours in seconds
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


def get_server_port():
    """Read the server port from the port file."""
    try:
        if PORT_FILE.exists():
            return int(PORT_FILE.read_text().strip())
    except (ValueError, IOError):
        pass
    return None


def save_server_port(port):
    """Save the server port to the port file."""
    PORT_FILE.write_text(str(port))


def get_server_pid():
    """Read the server PID from the PID file."""
    try:
        if PID_FILE.exists():
            return int(PID_FILE.read_text().strip())
    except (ValueError, IOError):
        pass
    return None


def save_server_pid(pid):
    """Save the server PID to the PID file."""
    PID_FILE.write_text(str(pid))


def clear_server_info():
    """Clear server port and PID files."""
    if PORT_FILE.exists():
        PORT_FILE.unlink()
    if PID_FILE.exists():
        PID_FILE.unlink()
