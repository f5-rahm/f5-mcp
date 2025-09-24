#!/usr/bin/env python3
"""
Simple MCP server with a BIG-IP object listing tool using FastMCP.
This serves as a basic example for the AI Step-by-Step lab.
"""

from fastmcp import FastMCP
import os
from dotenv import load_dotenv
from bigrest.bigip import BIGIP


load_dotenv('/app/.env')

F5_HOST = os.getenv('F5_HOST')
F5_USER = os.getenv('F5_USER')
F5_PASS = os.getenv('F5_PASS')

mcp = FastMCP("F5 MCP Server")


@mcp.tool
def obj_list(obj_type: str, obj_name: str = None):
    br = BIGIP(device = F5_HOST, username = F5_USER, password = F5_PASS, session_verify=False)
    if obj_name is None or obj_name == '':
        objs = br.load(f'/mgmt/tm/ltm/{obj_type}')
        return [obj.properties.get('name') for obj in objs]
    else:
        objs = br.load(f'/mgmt/tm/ltm/{obj_type}/{obj_name}')
        return [objs.properties]


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8081, stateless_http=True)