import logging
import sys
from datetime import datetime

class ConsoleFormatter(logging.Formatter):
    """Pretty, colorized console logs."""

    COLORS = {
        "DEBUG": "\033[90m",    # grey
        "INFO": "\033[94m",     # blue
        "WARNING": "\033[93m",  # yellow
        "ERROR": "\033[91m",    # red
        "CRITICAL": "\033[95m", # magenta
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        ts = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        name = record.name.replace("maf.", "")
        msg = record.getMessage()
        return f"{color}{ts} [{record.levelname:<8}] {name}: {msg}{self.RESET}"
    
debug_handler = logging.StreamHandler(sys.stderr)    # VSCode debug console
debug_handler.setFormatter(ConsoleFormatter())
root = logging.getLogger()
root.setLevel(logging.INFO)
root.handlers.clear()
# root.addHandler(stream_handler)
root.addHandler(debug_handler)

# quiet down noisy libs
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("anyio").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

    
def get_logger(name: str="maf") -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
    

