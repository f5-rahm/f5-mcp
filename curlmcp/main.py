#!/usr/bin/env python3
"""
MCP Curl Server using fastmcp
Provides curl functionality via MCP protocol
"""

import subprocess
import shlex
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Curl MCP Server")


@mcp.tool()
def curl(args: str) -> str:
    """
    Execute a curl command with specified arguments.

    Args:
        args: The arguments to pass to curl (e.g., '-X GET https://api.example.com')

    Returns:
        The output from the curl command
    """
    try:
        # Security: Use shlex to safely parse arguments
        # This helps prevent command injection
        cmd_args = shlex.split(args)

        # Execute curl command with timeout
        result = subprocess.run(
            ["curl"] + cmd_args,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            check=False  # Don't raise exception on non-zero exit
        )

        # Return stdout, or stderr if stdout is empty
        output = result.stdout if result.stdout else result.stderr

        if result.returncode != 0 and not output:
            return f"curl command failed with exit code {result.returncode}"

        return output or "Command executed successfully with no output"

    except subprocess.TimeoutExpired:
        return "Error: curl command timed out after 30 seconds"
    except Exception as e:
        return f"Error executing curl: {str(e)}"


@mcp.tool()
def curl_manual() -> str:
    """
    Display the curl manual page.

    Returns:
        The curl manual/help text
    """
    try:
        result = subprocess.run(
            ["curl", "--manual"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.stdout:
            return result.stdout

        # Fallback to --help if --manual isn't available
        result = subprocess.run(
            ["curl", "--help"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        return result.stdout or "Curl help not available"

    except Exception as e:
        return f"Error getting curl manual: {str(e)}"


if __name__ == "__main__":
    # Run the server
    mcp.run(transport="http", host="0.0.0.0", port=8082, stateless_http=True)