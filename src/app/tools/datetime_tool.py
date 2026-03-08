"""
DatetimeTool - A simple tool that returns the current date and time.

RESPONSIBILITY:
    Demonstrates the Tool Pattern for agentic applications.
    An agent calls this tool to retrieve the current datetime — no external API
    required. This is the simplest possible tool: zero dependencies, always works.

ARCHITECTURE FIT:
    Tools encapsulate a unit of capability. Agents stay thin and just call tools.
    To add a new capability (web search, database query), follow this same pattern.
"""
from datetime import datetime


class DatetimeTool:
    """
    Returns the current date and time as a formatted string.

    USAGE:
        tool = DatetimeTool()
        result = tool.run()  # Returns "Friday, March 07, 2026 at 10:45:30 AM"
    """

    def run(self) -> str:
        """
        Execute the tool and return the current datetime.

        Returns:
            str: Human-readable current date and time string.
        """
        now = datetime.now()
        # Format: "Friday, March 07, 2026 at 10:45:30 AM"
        return now.strftime("%A, %B %d, %Y at %I:%M:%S %p")
